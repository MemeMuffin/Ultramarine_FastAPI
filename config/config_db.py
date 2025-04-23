"""Database connection configuration"""

from sqlmodel import SQLModel, create_engine, Session

sqlite_file_name = "ultramarines.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    """Creates database and its tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Creates a connection with the database"""
    with Session(engine) as session:
        yield session
