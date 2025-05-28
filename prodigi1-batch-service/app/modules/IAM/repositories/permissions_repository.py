from .models.permission import Permission
from .repository import Repository
from sqlalchemy.dialects.postgresql import JSONB
class PermissionsRepository(Repository):
    """Permissions reportory to manage permissions table

    Args:
        Repository (class): Base repository
    """    
    def __init__(self, session):
        self.session = session
        self.model_type = Permission

    def get_permissions_by_resource_name(self, resource_name):
        with self.session as session:    
            return session.query(self.model_type).filter_by(resource=resource_name).first()
        # return self.session.query(self.model_type).filter_by(resource=resource_name).first()
    
    def get_permissions_by_role_id(self, role_id):
        with self.session as session:
            return session.query(self.model_type).filter_by(role_id=role_id).all()
        # return self.session.query(self.model_type).filter_by(role_id=role_id).all()
    
    def remove_permission(self, role_id):
        command = self.model_type.__table__.delete().where(self.model_type.role_id == role_id)
        self.session.execute(command)
        self.session.commit()

    def get_role_ids_by_resource_name_and_shop_id(self,resource_name,shop_id):
        with self.session as session:    
            return session.query(self.model_type.role_id).filter(self.model_type.resource==resource_name,self.model_type.scope.contains({"ALLOWED_SHOP_IDS": [shop_id]})).all()
        
    def get_role_ids_by_resource_name_and_action(self, resource_name, action):
        with self.session as session:    
            return session.query(self.model_type.role_id) \
                          .filter(self.model_type.resource==resource_name,
                                  self.model_type.action == action).all()

    def get_permissions_by_role_ids(self, role_ids):
        with self.session as session:
            return session.query(self.model_type).filter(self.model_type.role_id.in_(role_ids)).all()