from .models.user_role import UserRole
from .repository import Repository


class UserRoleRepository(Repository):
    """Role reportory to manage role table

    Args:
        Repository (class): Base repository
    """    
    def __init__(self, session):
        self.session = session
        self.model_type = UserRole

    def get_user_role_by_user_id(self, user_id):
        with self.session as session:     
            return session.query(self.model_type).filter_by(user_id=user_id).all()
        # return self.session.query(self.model_type).filter_by(user_id=user_id).all()
    
    def get_roles_list(self, role_id):
        with self.session as session:     
            return session.query(self.model_type).filter_by(role_id=role_id).all()
    
    def remove_role(self,user_role):
        self.session.delete(user_role)
        self.session.commit()

    def get_user_ids_by_role_ids(self,role_ids):
        with self.session as session:     
            return session.query(self.model_type.user_id).filter(self.model_type.role_id.in_(role_ids)).all()
        
    def get_role_ids_by_user_id(self,user_id):
        with self.session as session:     
            return session.query(self.model_type.role_id).filter(self.model_type.user_id == user_id).all()