from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = ''

engine = create_engine(URL_DATABASE)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base = declarative_base()