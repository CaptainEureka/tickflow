from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import metadata, tasks_table

def get_database():
    engine = create_engine("sqlite:///path/to/database.db")
    metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_tasks_table():
    return tasks_table
