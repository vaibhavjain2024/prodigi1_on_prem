from .models.user import User
from .repository import Repository
# from boto3.dynamodb.conditions import Attr

class UserRepository(Repository):
    """Role reportory to manage role table

    Args:
        Repository (class): Base repository
    """    
    def __init__(self, session):
        self.session = session
        self.model_type = User

    def get_users(self, tenant):
        """Get all users for a tenant
        """
        # with self.session() as session:         
        #     return session.query(self.model_type).filter_by(tenant=tenant).all()
        return self.session.query(self.model_type).filter_by(tenant=tenant).all()

    def get_user_by_federation_identifier(self,identifier):
        # with self.session() as session: 
        #     return session.query(self.model_type).filter_by(federation_identifier=identifier).first()
        return self.session.query(self.model_type).filter_by(federation_identifier=identifier).first()
        
    
    