from .models.role import Role
from .repository import Repository


class RoleRepository(Repository):
    """Role reportory to manage role table

    Args:
        Repository (class): Base repository
    """    
    def __init__(self, session):
        self.session = session
        self.model_type = Role

    def get_roles_by_tenant(self, tenant):
        """Get all roles for a tenant
        """  
        with self.session as session:       
            return session.query(self.model_type).filter_by(tenant=tenant).all()
        # return self.session.query(self.model_type).filter_by(tenant=tenant).all()
    
    def get_role_by_tenant_and_name(self,tenant,name):
        with self.session as session: 
            return session.query(self.model_type).filter_by(tenant=tenant, name=name).first()
        # return self.session.query(self.model_type).filter_by(tenant=tenant, name=name).first()
        
    def get_role_by_ids(self, role_ids):
        with self.session as session: 
            return session.query(self.model_type).filter(self.model_type.id.in_(role_ids)).all()


    