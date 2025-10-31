import os
from pathlib import Path
from sqlalchemy import DateTime, create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
load_dotenv()

Base = declarative_base()
BASE_DIR = Path(__file__).resolve().parent 


DB_FILENAME = os.getenv("DB_NAME") 


DB_PATH = BASE_DIR / DB_FILENAME 


DATABASE_URL = f"sqlite:///{DB_PATH}"

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    source_name = Column(String)
    url = Column(String, nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False)
    topic = Column(String, nullable=False)
    downloaded_at = Column(DateTime, nullable=False)
    generic_news = Column(Boolean)

engine = create_engine(DATABASE_URL)

def setup_database_orm():
    Base.metadata.create_all(bind=engine)