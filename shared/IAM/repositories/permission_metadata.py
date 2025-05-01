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

    
    
    


    