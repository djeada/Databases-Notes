"""Optimistic concurrency control with SQLAlchemy and SQLite.

Two sessions load the same row. The first update succeeds. The second update
uses the old version number and is rejected by SQLAlchemy's version checking.

Run from the repository root:
    python -m pip install -r scripts/orm/requirements.txt
    python scripts/orm/optimistic_concurrency_demo.py
"""

from __future__ import annotations

from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.orm.exc import StaleDataError


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    version_id: Mapped[int] = mapped_column(nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version_id}


def main() -> None:
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)

    with Session(engine) as seed:
        seed.add(Document(title="Initial title"))
        seed.commit()

    session_a = Session(engine)
    session_b = Session(engine)

    try:
        doc_a = session_a.scalar(select(Document).where(Document.id == 1))
        doc_b = session_b.scalar(select(Document).where(Document.id == 1))

        if doc_a is None or doc_b is None:
            raise RuntimeError("Expected document row")

        print(
            f"Both sessions loaded version {doc_a.version_id}: "
            f"A={doc_a.title!r}, B={doc_b.title!r}"
        )

        doc_a.title = "Edited by session A"
        session_a.commit()
        print(f"Session A committed version {doc_a.version_id}")

        doc_b.title = "Edited by session B"
        try:
            session_b.commit()
        except StaleDataError:
            session_b.rollback()
            print("Session B was rejected because its version was stale.")

        with Session(engine) as verify:
            current = verify.get(Document, 1)
            if current is None:
                raise RuntimeError("Document disappeared")
            print(
                f"Final row: title={current.title!r}, "
                f"version={current.version_id}"
            )
    finally:
        session_a.close()
        session_b.close()


if __name__ == "__main__":
    main()
