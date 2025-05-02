from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.repository.db_setup import get_session

class SessionHelper:
    def __init__(self, connection_string):
        if not connection_string:
            raise ValueError("Connection string cannot be None or empty.")
        
        # Create SQLAlchemy engine
        self.engine = create_engine(connection_string, pool_size=30)

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        session = get_session(session, self.engine)
        return session

    def close(self):
        if hasattr(self, 'engine'):
            self.engine.dispose()