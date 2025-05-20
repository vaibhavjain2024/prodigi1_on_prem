from .repository import Repository
from .models.iot_msil_location import MSILLocation
from .models.iot_msil_site import MSILSite
from .models.iot_module_location_association import IOTModuleLocationAssociation

class SiteReporsitory(Repository):
    def __init__(self, session):
        self.session = session
        self.model_type = MSILSite

    def get_location_and_site_by_module(self,module_id=None):
        with self.session:
            query = self.session.query(
                self.model_type.id,
                self.model_type.site_name,
                MSILLocation.id,
                MSILLocation.location_name
            ).join(MSILSite , MSILSite.id == MSILLocation.site_id) \
            .join(IOTModuleLocationAssociation, MSILLocation.id == IOTModuleLocationAssociation.iot_msil_location_id)\
            .filter(IOTModuleLocationAssociation.iot_module_id == module_id) \
            .distinct()\
            .all()

            print(query)

            return query