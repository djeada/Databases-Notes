#!/usr/bin/env python3
"""A small multiline SQL console for SQL Server running in Docker."""

from __future__ import annotations

import argparse
import getpass
import os
import queue
import re
import subprocess
import sys
import threading
import time
import uuid
from typing import TextIO


DEFAULT_CONTAINER = "sqlserver-demo"
DEFAULT_SERVER = "localhost"
DEFAULT_USER = "sa"
DEFAULT_DATABASE = "master"
DEFAULT_SQLCMD = "/opt/mssql-tools18/bin/sqlcmd"
SHELL_SETUP = (
    "IFS= read -r SQLCMDPASSWORD || exit 2; "
    "export SQLCMDPASSWORD; "
    'exec "$@"'
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Paste and execute multiline SQL against SQL Server in Docker."
    )
    parser.add_argument("--container", default=os.getenv("SQL_DOCKER_CONTAINER", DEFAULT_CONTAINER))
    parser.add_argument("--server", default=DEFAULT_SERVER)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--database", default=DEFAULT_DATABASE)
    parser.add_argument("--sqlcmd", default=DEFAULT_SQLCMD, help="sqlcmd path inside the container")
    return parser.parse_args()


def ask(label: str, default: str) -> str:
    answer = input(f"{label} [{default}]: ").strip()
    return answer or default


class DockerSqlSession:
    """Keep one sqlcmd connection alive and delimit output for each batch."""

    def __init__(
        self,
        container: str,
        server: str,
        user: str,
        database: str,
        sqlcmd_path: str,
        password: str,
    ) -> None:
        self.container = container
        self.server = server
        self.user = user
        self.database = database
        self.sqlcmd_path = sqlcmd_path
        self.password = password
        self._output: queue.Queue[tuple[str, str | None]] = queue.Queue()
        self._process: subprocess.Popen[str] | None = None
        self._reader: threading.Thread | None = None

    def start(self) -> None:
        command = [
            "docker",
            "exec",
            "-i",
            self.container,
            "/bin/sh",
            "-c",
            SHELL_SETUP,
            "sqlcmd",
            self.sqlcmd_path,
            "-S",
            self.server,
            "-U",
            self.user,
            "-C",
            "-r",
            "1",
            "-W",
            "-l",
            "30",
        ]
        try:
            self._process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except FileNotFoundError as error:
            if error.filename == "docker":
                raise RuntimeError("Docker CLI was not found. Install Docker or add it to PATH.") from error
            raise

        assert self._process.stdin is not None
        assert self._process.stdout is not None
        assert self._process.stderr is not None
        for name, stream in (("data", self._process.stdout), ("message", self._process.stderr)):
            threading.Thread(target=self._read_output, args=(stream, name), daemon=True).start()

        # The shell wrapper consumes this first line and exposes it only to sqlcmd's
        # environment. It avoids putting the SA password in Docker's command line.
        self._process.stdin.write(self.password + "\n")
        self._process.stdin.flush()
        self.password = ""

    def _read_output(self, stream: TextIO, name: str) -> None:
        try:
            for line in stream:
                self._output.put((name, line))
        finally:
            self._output.put((name, None))

    def execute(self, sql: str, *, show_output: bool = True) -> bool:
        process = self._process
        if process is None or process.stdin is None:
            raise RuntimeError("SQL session has not been started.")
        if process.poll() is not None:
            raise RuntimeError("The Docker/sqlcmd process has exited.")

        marker = f"__PYSQL_{uuid.uuid4().hex}__"
        # Mark both streams independently so a fast stderr reader cannot hide
        # trailing result rows. Restore the caller's NOCOUNT setting afterward.
        packet = (
            f"{sql.rstrip()}\nGO\n"
            "DECLARE @quiet bit = CASE WHEN @@OPTIONS & 512 = 512 THEN 1 ELSE 0 END;\n"
            "SET NOCOUNT ON;\n"
            f"SELECT '{marker}END' AS [{marker}BEGIN];\n"
            "IF @quiet = 0 SET NOCOUNT OFF;\n"
            f"PRINT '{marker}';\nGO\n"
        )
        try:
            process.stdin.write(packet)
            process.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            raise RuntimeError("Could not send SQL; the connection may have closed.") from error

        def emit(text: str, color: str = "#cdd6f4") -> None:
            if not show_output:
                return
            if sys.stdout.isatty():
                from prompt_toolkit import print_formatted_text
                from prompt_toolkit.formatted_text import FormattedText
                print_formatted_text(FormattedText([(color, text)]), end="")
            else:
                sys.stdout.write(text)
                sys.stdout.flush()

        had_error = False
        messages: list[str] = []
        completed: set[str] = set()
        closed: set[str] = set()
        control_result = False
        data_started = False

        def show_messages() -> None:
            if messages:
                emit("\n  Messages\n", "#89b4fa")
                error_body = False
                for line in messages:
                    if re.match(r"Msg \d+, Level \d+", line):
                        error_body = True
                        emit("    " + line, "#9399b2")
                    elif line.startswith("Changed database context") or re.match(r"\(\d+ rows? affected\)", line):
                        error_body = False
                        emit("    " + line, "#9399b2")
                    else:
                        emit("    " + line, "#f38ba8" if error_body or "Sqlcmd: Error" in line else "#cdd6f4")

        while len(completed) < 2:
            source, line = self._output.get()
            if line is None:
                closed.add(source)
                if len(closed) == 2:
                    show_messages()
                    raise RuntimeError("sqlcmd exited before completing the script.")
                continue
            value = line.strip()
            if source == "message" and value == marker:
                completed.add(source)
                continue
            if source == "data" and value == marker + "BEGIN":
                control_result = True
                continue
            if source == "data" and control_result:
                if value == marker + "END":
                    completed.add(source)
                continue
            if source == "message" or re.fullmatch(r"\(\d+ rows? affected\)", value):
                messages.append(line)
                if re.search(r"\bMsg\s+\d+,\s*Level\s+\d+", line) or "Sqlcmd: Error" in line:
                    had_error = True
            else:
                if not data_started and not value:
                    continue
                if not data_started:
                    emit("\n  Results\n", "#89b4fa")
                    data_started = True
                emit("    " + line)
        show_messages()
        return not had_error

    def change_database(self, database: str) -> bool:
        # Database names cannot be supplied as SQL parameters. Quote as a T-SQL
        # identifier by doubling closing brackets.
        identifier = database.replace("]", "]]")
        if not identifier:
            print("Database name cannot be empty.")
            return False
        if not self.execute(f"USE [{identifier}];"):
            print("Database was not changed.")
            return False
        self.database = database
        return True

    def close(self) -> None:
        process = self._process
        if process is None:
            return
        if process.stdin is not None:
            try:
                process.stdin.write("QUIT\n")
                process.stdin.flush()
                process.stdin.close()
            except (BrokenPipeError, OSError):
                pass
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def print_help() -> None:
    print("""Paste SQL directly into the editor, including any GO lines.
Enter inserts a new line. Ctrl+R or Esc then Enter runs the whole script.
Arrow keys move through the script; Ctrl+C clears it; Ctrl+D exits when empty.
Commands on their own line (press Enter): :help, :use DATABASE, :status, :quit.
GO separates SQL batches inside the script; it does not submit the editor.""")


def interactive_loop(session: DockerSqlSession) -> None:
    from prompt_toolkit import PromptSession, print_formatted_text
    from prompt_toolkit.formatted_text import FormattedText
    from prompt_toolkit.lexers import Lexer
    from prompt_toolkit.styles import Style

    class SqlLexer(Lexer):
        def lex_document(self, document):
            pattern = re.compile(r"(--[^\n]*|'(?:''|[^'])*'|\b(?:SELECT|FROM|WHERE|CREATE|DATABASE|TABLE|INDEX|NONCLUSTERED|CLUSTERED|PRIMARY|KEY|CONSTRAINT|NOT|NULL|INT|VARCHAR|NVARCHAR|USE|GO|ON|AS|INSERT|INTO|VALUES|UPDATE|SET|DELETE|JOIN|ORDER|BY|GROUP|IF|EXISTS|DROP|ALTER|AND|OR|BEGIN|END|COUNT)\b|\b\d+\b)", re.I)
            def get_line(number):
                tokens = []
                for part in pattern.split(document.lines[number]):
                    if not part:
                        continue
                    kind = "comment" if part.startswith("--") else "string" if part.startswith("'") else "number" if part.isdigit() else "keyword" if pattern.fullmatch(part) else ""
                    tokens.append((f"class:{kind}" if kind else "", part))
                return tokens
            return get_line

    style = Style.from_dict({
        "": "#cdd6f4", "keyword": "#89b4fa bold", "string": "#a6e3a1",
        "number": "#fab387", "comment": "#7f849c italic", "gutter": "#9399b2",
    })

    def message(text, color="#89b4fa"):
        print_formatted_text(FormattedText([(color, text)]))
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.history import InMemoryHistory

    bindings = KeyBindings()

    @bindings.add("c-r")
    @bindings.add("escape", "enter")
    def submit(event):
        event.current_buffer.validate_and_handle()

    @bindings.add("enter")
    def newline_or_command(event):
        buffer = event.current_buffer
        if buffer.text.strip().startswith(":") and "\n" not in buffer.text.strip():
            buffer.validate_and_handle()
        else:
            buffer.insert_text("\n")

    editor = PromptSession(
        multiline=True,
        key_bindings=bindings,
        history=InMemoryHistory(),
        enable_open_in_editor=False,
        lexer=SqlLexer(),
        style=style,
        erase_when_done=False,
        reserve_space_for_menu=0,
        prompt_continuation=lambda width, line, wrap: [("class:gutter", " " * width if wrap else f"  {line + 1:>3} │ ")],
    )
    # Reserve two plain rows below the editor while typing.
    from prompt_toolkit.layout.containers import HSplit, Window, ConditionalContainer
    from prompt_toolkit.filters import is_done

    editor.layout.container = HSplit([
        editor.layout.container,
        ConditionalContainer(Window(height=2, char=" "), filter=~is_done),
    ])
    message("\n  SQL CONSOLE", "#89b4fa bold")
    message(f"  {session.container}  ·  {session.user}  ·  persistent session", "#7f849c")
    message("  Paste SQL below. Ctrl+R runs it; Enter adds a line. :help shows commands.\n", "#a6adc8")
    run_number = 0
    while True:
        try:
            sql = editor.prompt([("class:gutter", "    1 │ ")]).strip()
        except EOFError:
            print("Goodbye.")
            return
        except KeyboardInterrupt:
            print("SQL buffer cleared.")
            continue
        if not sql:
            continue
        if sql.startswith(":"):
            command, _, argument = sql.partition(" ")
            command, argument = command.lower(), argument.strip()
            if command in {":quit", ":q", ":exit"}:
                print("Goodbye.")
                return
            if command in {":help", ":h", ":paste"}:
                print_help()
            elif command in {":clear", ":cancel"}:
                print("SQL buffer cleared.")
            elif command == ":status":
                print(f"Container: {session.container} | Server: {session.server} | User: {session.user}")
                session.execute("SELECT DB_NAME() AS current_database;")
            elif command in {":use", ":database"}:
                if argument:
                    session.change_database(argument)
                else:
                    print("Usage: :use DATABASE")
            else:
                print(f"Unknown command {command!r}. Type :help.")
            continue
        run_number += 1
        message(f"\n  ── Run {run_number} · {len(sql.splitlines())} lines ──", "#89b4fa")
        started = time.monotonic()
        try:
            success = session.execute(sql)
        except KeyboardInterrupt:
            print("\nExecution interrupted; closing the SQL session.")
            return
        except RuntimeError as error:
            print(f"Connection error: {error}")
            return
        elapsed = time.monotonic() - started
        message(f"  {'✓ Completed' if success else '✗ SQL errors reported'} · {elapsed:.2f}s\n", "#a6e3a1" if success else "#f38ba8")


def main() -> int:
    args = parse_args()
    print("SQL Server Docker console")
    print("Enter accepts the shown default. The password is hidden as you type.")
    container = ask("Docker container", args.container)
    server = ask("SQL Server inside the container", args.server)
    user = ask("SQL login", args.user)
    database = ask("Initial database", args.database)
    sqlcmd_path = ask("sqlcmd path inside container", args.sqlcmd)
    password = os.getenv("SQLCMDPASSWORD")
    if password is None:
        password = getpass.getpass("SA password: ")
    if not password:
        print("Password cannot be empty.", file=sys.stderr)
        return 2

    session = DockerSqlSession(container, server, user, database, sqlcmd_path, password)
    try:
        print(f"Connecting to Docker container {container}...", flush=True)
        session.start()
        # `:use` on startup ensures the connection selects the configured
        # database without restarting sqlcmd, preserving one live SQL session.
        if not session.change_database(database):
            return 1
        print(f"Checking connection to {container} ({server}) as {user}...")
        if not session.execute("SELECT 1 AS connection_test;", show_output=True):
            print("Connection check returned a SQL error. Check the settings above.", file=sys.stderr)
            return 1
        print("Connected. Multiline editor ready — paste SQL and press Ctrl+R to run.")
        interactive_loop(session)
        return 0
    except (RuntimeError, OSError) as error:
        print(f"Could not connect: {error}", file=sys.stderr)
        print(
            "Check that Docker is running, the container is started, and the login/password are correct.",
            file=sys.stderr,
        )
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    # Keep the original launch command working with an isolated dependency install.
    from pathlib import Path
    editor_python = Path.home() / ".local/share/sql-docker-console/venv/bin/python"
    try:
        import prompt_toolkit
    except ImportError:
        if editor_python.exists() and str(editor_python.parent.parent) != sys.prefix:
            os.execv(str(editor_python), [str(editor_python), str(Path(__file__).resolve()), *sys.argv[1:]])
        raise SystemExit("Multiline editor dependency missing. Install prompt-toolkit in your Python environment.")
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        raise SystemExit(130)
