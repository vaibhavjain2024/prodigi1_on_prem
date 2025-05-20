
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class SessionHelper:
    def __init__(self, connection_string):
        if not connection_string:
            raise ValueError("Connection string cannot be None or empty.")
        
        # Create SQLAlchemy engine
        self.engine = create_engine(connection_string, pool_size=100)

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        # session = get_session(session, self.engine)
        return session

    def close(self):
        if hasattr(self, 'engine'):
            self.engine.dispose()

    def __enter__(self):
        """Create and return a session when entering the context."""
        self.session = self.get_session()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.session.rollback()
        
        self.session.close()
        self.close()