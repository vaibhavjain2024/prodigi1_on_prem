from .models.permission import Permission
from .repository import Repository

class PermissionsRepository(Repository):
    """Permissions reportory to manage permissions table

    Args:
        Repository (class): Base repository
    """    
    def __init__(self, session):
        self.session = session
        self.model_type = Permission

    def get_permissions_by_resource_name(self, resource_name):
        # with self.session() as session:    
        #     return session.query(self.model_type).filter_by(resource=resource_name).first()
        return self.session.query(self.model_type).filter_by(resource=resource_name).first()
    
    def get_permissions_by_role_id(self, role_id):
        # with self.session() as session:
        #     return session.query(self.model_type).filter_by(role_id=role_id).all()
        return self.session.query(self.model_type).filter_by(role_id=role_id).all()
    
    
    


    