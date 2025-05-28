from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

# create a new db session


def get_session(session, engine):
    from .models.iot_sap_logs_downtime import IOTSapLogsDowntime
    Base.metadata.create_all(engine)
    return session
