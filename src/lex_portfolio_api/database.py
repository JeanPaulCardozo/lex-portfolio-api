import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(url=DATABASE_URL)

session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)

base = declarative_base()


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
