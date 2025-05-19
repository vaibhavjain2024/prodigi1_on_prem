from .models.permission_metadata import PermissionMetadata
from .repository import Repository

class PermissionMetadataRepository(Repository):
    """Permission Metadata reportory to manage permissions table

    Args:
        Repository (class): Base repository
    """    
    def __init__(self, session):
        self.session = session
        self.model_type = PermissionMetadata

    def get_permission_meta_by_module_ids(self, module_ids):
        with self.session:
            query = (
                self.session.query(self.model_type)
                .filter(self.model_type.module_id.in_(module_ids))
            )
            return query.all()
        
    def get_all_permission_metadata(self, limit= 1000, offset= 0):
        with self.session: 
            return self.session.query(self.model_type).limit(limit).offset(offset).all()
    
    
    


    