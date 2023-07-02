from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

SQLALCHEMY_DB_URL = 'sqlite:///./blog.db'

engine = create_engine(SQLALCHEMY_DB_URL, connect_args={"check_same_thread": False})
LocalSession = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False, ))
LocalSession()
Base = declarative_base()
