from sqlmodel import Session, SQLModel, create_engine
from typing import Generator

DATABASE_URL: str = 'sqlite:///./manara.db'

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session