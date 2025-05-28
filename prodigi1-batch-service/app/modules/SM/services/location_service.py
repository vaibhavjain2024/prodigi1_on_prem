from ..repository.location_repository import LocationRepository


class LocationService:
    def __init__(self, repository: LocationRepository):
        self.repository = repository

    def get_location_name(self,location_id):
        try:
            location_object = self.repository.get(location_id)
            if location_object and hasattr(location_object, 'location_name'):
                location_name = location_object.location_name
                return location_name
            else:
                return None
        except Exception as e:
            print(f"Error while fetching location name :: {e}")
            return None 
        
