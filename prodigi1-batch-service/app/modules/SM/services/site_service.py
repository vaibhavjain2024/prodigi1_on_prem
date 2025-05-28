from ..repository.site_repository import SiteReporsitory

class SiteService():
    def __init__(self, repository : SiteReporsitory):
        self.repository = repository
    
    def get_location_and_site_by_module(self,module_id):
        results = self.repository.get_location_and_site_by_module(module_id=module_id)
        results = self.transform_location_and_site_by_module(data=results)
        return results

    def transform_location_and_site_by_module(self,data):
        results = []
        id = 0
        for each in data:
            site_id,site_name,location_id,location_name = each
            site_obj = self.get_site_obj(site_id,site_name,results)
            site_obj['locations'].append(self.create_location_obj(location_id=location_id,location_name=location_name))

        return results        

        
    def get_site_obj(self,site_id,site_name,data):

        if len(data) != 0 and data[-1]['site_id'] == site_id:
            site_obj = data[-1]
        else:
            site_obj = self.create_site_obj(site_id,site_name)
            data.append(site_obj)
        return site_obj
    
    def create_site_obj(self,site_id,site_name):
        return {
            'site_id' : site_id,
            'site_name' : site_name,
            'locations' : [] 
        }
            
    def create_location_obj(self,location_id,location_name):
        return {
            'location_id' : location_id,
            'location_name' : location_name
        } 
