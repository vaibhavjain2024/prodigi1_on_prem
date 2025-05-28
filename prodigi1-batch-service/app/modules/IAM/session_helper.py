# import os
# from sqlalchemy import create_engine
# from IAM.repositories.db_setup import get_session

# from sqlalchemy.orm.session import sessionmaker


# session_helper = {}
# def get_session_helper(env, connection_string):
#     if env not in session_helper.keys():
#         session_helper[env] = SessionHelper(connection_string)
#     return session_helper[env]


# class SessionHelper():
#     def __init__(self, connection_string):
#         connection_string = os.environ.get(connection_string)
#         self.engine = create_engine(connection_string)
    
    
#     def get_session(self):
#         Session = sessionmaker(bind=self.engine)
#         session = Session()
#         self.session = get_session(session, self.engine)
#         #return Session
#         return self.session

# import os
# from sqlalchemy import create_engine
# from IAM.repositories.db_setup import get_session

# from sqlalchemy.orm.session import sessionmaker


# session_helper = {}
# def get_session_helper(env, connection_string):
#     if env not in session_helper.keys():
#         session_helper[env] = SessionHelper(connection_string)
#     return session_helper[env]


# class SessionHelper():
#     def __init__(self, connection_string):
#         connection_string = os.environ.get(connection_string)
#         self.engine = create_engine(connection_string)
    
    
#     def get_session(self):
#         Session = sessionmaker(bind=self.engine)
#         session = Session()
#         self.session = get_session(session, self.engine)
#         #return Session
#         return self.session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .repositories.db_setup import get_session

class SessionHelper:
    def __init__(self, connection_string):
        if not connection_string:
            raise ValueError("Connection string cannot be None or empty.")
        
        # Create SQLAlchemy engine
        self.engine = create_engine(connection_string, pool_size=100)

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        session = get_session(session, self.engine)
        return session

    def close(self):
        if hasattr(self, 'engine'):
            self.engine.dispose()