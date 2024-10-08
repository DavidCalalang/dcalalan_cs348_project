from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pymysql

URL_DATABASE = 'mysql+pymysql://root:@34.135.119.225:3306/cs348-project'

engine = create_engine(URL_DATABASE)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()