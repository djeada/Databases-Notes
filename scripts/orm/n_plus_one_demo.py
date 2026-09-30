"""Compare lazy relationship loading with select-in eager loading.

Run from the repository root:
    python -m pip install -r scripts/orm/requirements.txt
    python scripts/orm/n_plus_one_demo.py
"""

from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import ForeignKey, String, create_engine, event, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    selectinload,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    author: Mapped[User] = relationship(back_populates="posts")


@contextmanager
def count_sql(engine):
    count = 0

    def before_cursor_execute(*_args):
        nonlocal count
        count += 1

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        yield lambda: count
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)


def seed(engine) -> None:
    Base.metadata.create_all(engine)

    with Session(engine) as session, session.begin():
        for user_number in range(1, 6):
            user = User(name=f"User {user_number}")
            user.posts = [
                Post(title=f"Post {user_number}-A"),
                Post(title=f"Post {user_number}-B"),
            ]
            session.add(user)


def lazy_loading_demo(engine) -> int:
    with Session(engine) as session, count_sql(engine) as sql_count:
        users = session.scalars(select(User).order_by(User.id)).all()

        # Accessing .posts triggers one additional SELECT for each user.
        total_posts = sum(len(user.posts) for user in users)

        print(f"lazy loading: {len(users)} users, {total_posts} posts")
        return sql_count()


def selectin_loading_demo(engine) -> int:
    with Session(engine) as session, count_sql(engine) as sql_count:
        users = session.scalars(
            select(User)
            .options(selectinload(User.posts))
            .order_by(User.id)
        ).all()

        total_posts = sum(len(user.posts) for user in users)

        print(f"selectinload: {len(users)} users, {total_posts} posts")
        return sql_count()


def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    seed(engine)

    lazy_queries = lazy_loading_demo(engine)
    eager_queries = selectin_loading_demo(engine)

    print(f"lazy-loading SQL statements: {lazy_queries}")
    print(f"selectinload SQL statements:  {eager_queries}")


if __name__ == "__main__":
    main()
