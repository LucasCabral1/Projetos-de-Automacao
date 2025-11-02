import os
from pathlib import Path
from sqlalchemy import DateTime, create_engine, Column, Integer, String, Boolean, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
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

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    articles = relationship("Article", back_populates="author")
    
engine = create_engine(DATABASE_URL)

def setup_database_orm():
    Base.metadata.create_all(bind=engine)