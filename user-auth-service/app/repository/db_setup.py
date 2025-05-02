from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

#create a new db session 
def get_session(session, engine):

    from app.models.auth_token import AuthToken
    Base.metadata.create_all(engine)
    return session




