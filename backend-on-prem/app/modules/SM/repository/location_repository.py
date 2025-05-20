from .models.iot_msil_location import MSILLocation
from .repository import Repository

class LocationRepository(Repository):

    def __init__(self, session):
        self.session = session
        # Each repository should define its model_type
        self.model_type = MSILLocation