from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session


class Base(DeclarativeBase):
    pass


def get_database() -> Engine:
    engine = create_engine("sqlite:///database.db")
    Base.metadata.create_all(engine)
    return engine


@contextmanager
def session(engine: Engine | None = None) -> Generator[Session, None, None]:
    if engine is None:
        engine = get_database()
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
