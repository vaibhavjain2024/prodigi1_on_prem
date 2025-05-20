import site
from collections import defaultdict
from ..repository.models.iot_msil_shop import MSILShop
from ..repository.shop_repository import ShopRepository


class ShopService:
    def __init__(self, repository: ShopRepository):
        self.repository = repository

    def get_all_values(self, fetch_location_mappings = False):
        model_list = self.repository.get_all_values()
        if fetch_location_mappings:
            module_having_location_association = self.repository.get_all_values_for_location_associations()
            if len(module_having_location_association):
                model_list += module_having_location_association
        
        filter_values = []
        for model in model_list:
            filter_values.append({
                "module" : model.module,
                "site" : model.site,
                "location" : model.location,
                "plant" : model.plant,
                "shop" : model.shop,
                "module_display_name": model.module_display_name
            })
        return filter_values
        

    def get_all_values_by_filter_values(
        self,
        module_name="All",
        site_name="All",
        location_name="All",
        plant_name="All",
        shop_name="All",
    ):
        model_list = self.repository.get_all_values_by_filter_values(
            module_name, site_name, location_name, plant_name, shop_name
        )
        module_list = []
        site_list = []
        location_list = []
        plant_list = []
        shop_list = []
        if model_list != None:
            for shop_model in model_list:
                if shop_model[0] not in module_list:
                    module_list.append(shop_model[0])
                if shop_model[1] not in site_list:
                    site_list.append(shop_model[1])
                if shop_model[2] not in location_list:
                    location_list.append(shop_model[2])
                if shop_model[3] not in plant_list:
                    plant_list.append(shop_model[3])
                if shop_model[4] not in shop_list:
                    shop_list.append(shop_model[4])
            dict = {
                "module": module_list,
                "site": site_list,
                "location": location_list,
                "plant": plant_list,
                "shop": shop_list,
            }
            return dict
        else:
            return None

    def transform_shops_to_sites(self, shops):
        sites = []

        for shop in shops:
            shop_obj = shop[0]
            site_obj = shop[2]
            location_obj = shop[3]
            plant_obj = shop[4]

            shop_dict = {
                "id": shop_obj.id,
                "shop_name": shop_obj.shop_name,
                "shop_type": shop_obj.shop_type,
                "plant_id": plant_obj.id,
            }

            # Add site if it doesnt exist
            site_index = [
                index for index, value in enumerate(sites) if value["id"] == site_obj.id
            ]
            if len(site_index) == 0:
                site = {
                    "id": site_obj.id,
                    "site_name": site_obj.site_name,
                    "locations": [],
                }
                sites.append(site)
                site_index = len(sites) - 1
            else:
                site_index = site_index[0]

            # Add location if it doesnt exist
            locations = sites[site_index]["locations"]
            location_index = [
                index
                for index, value in enumerate(locations)
                if value["id"] == location_obj.id
            ]
            if len(location_index) == 0:
                location = {
                    "id": location_obj.id,
                    "location_name": location_obj.location_name,
                    "site_id": site_obj.id,
                    "plants": [],
                }
                locations.append(location)
                location_index = len(locations) - 1
            else:
                location_index = location_index[0]

            # Add plant if it doesnt exist
            plants = locations[location_index]["plants"]
            plant_index = [
                index
                for index, value in enumerate(plants)
                if value["id"] == plant_obj.id
            ]
            if len(plant_index) == 0:
                plant = {
                    "id": plant_obj.id,
                    "plant_name": plant_obj.plant_name,
                    "location_id": location_obj.id,
                    "shops": [shop_dict],
                }
                plants.append(plant)
            else:
                plant_index = plant_index[0]
                plants[plant_index]["shops"].append(shop_dict)

        return sites

    def get_all_sites_from_module(self, module_name):
        shops = self.repository.get_shops_by_module(module_name)
        return self.transform_shops_to_sites(shops)

    def get_all_shops_by_plant_id_or_type_repair(
        self, plant_id, repair: list = None
    ) -> list:
        return self.repository.get_shops_by_plant_id_or_type_repair(
            plant_id=plant_id, repair=repair
        )

    def collect_shop_and_plant_ids(self, shop_ids):
        return self.repository.collect_shop_and_plant_ids(shop_ids)

    def get_plant_and_common_shops(self, shop_ids):
        return self.repository.get_plant_and_common_shops(shop_ids)

    def get_shop_name(self, shop_ids):
        return self.repository.get_shop_name(shop_ids)

    def check_if_args_exist_in_role_master(
            self, staff_id, group_name=None, line_name=None, area_name=None
    ):
        return self.repository.check_if_args_exist_in_role_master(
            staff_id, group_name=None, line_name=None, area_name=None
        )

    def transform_group_line_area_shops_to_sites(self, shops):
        sites = defaultdict(lambda: {"site_name": None, "locations": {}})
        for shop in shops:
            shop_obj = shop[0]
            site_obj = shop[2]
            location_obj = shop[3]
            plant_obj = shop[4]
            role_obj = shop[5]

            role_info = {
                'sub_category': role_obj.sub_category,
                'group': role_obj.group_name,
                'line': role_obj.line_name,
                'area': role_obj.area_name,
            }

            site = sites[site_obj.id]
            if not site.get('site_name'):
                site['site_name'] = site_obj.site_name

            location = site['locations'].get(location_obj.id)
            if not location:
                location = {
                    'location_name': location_obj.location_name,
                    'plants': {},
                }
                site['locations'][location_obj.id] = location

            plant = location['plants'].get(plant_obj.id)
            if not plant:
                plant = {
                    'plant_name': plant_obj.plant_name,
                    'shops': [],
                }
                location['plants'][plant_obj.id] = plant

            shop_dict = {
                'id': shop_obj.id,
                'plant_id': plant_obj.id,
                'shop_name': shop_obj.shop_name,
                'shop_type': shop_obj.shop_type,
                'roles': [role_info],
            }
            existing_shop = next((s for s in plant['shops']
                                  if s['shop_name'] == shop_obj.shop_name),
                                 None
                                 )
            if existing_shop:
                existing_shop['roles'].append(role_info)
            else:
                plant['shops'].append(shop_dict)

        # Remove unnecessary 'id' keys
        cleaned_sites = [
            {
                'site_name': site['site_name'],
                'locations': [
                    {
                        'location_name': location['location_name'],
                        'id': location_id,
                        'plants': [
                            {
                                'plant_name': plant['plant_name'],
                                'id': plant_id,
                                'location_id': location_id,
                                'shops': plant['shops']
                            }
                            for plant_id, plant in location['plants'].items()
                        ]
                    }
                    for location_id, location in site['locations'].items()
                ]
            }
            for site_id, site in sites.items()
        ]
        return cleaned_sites

    def get_site_hierarchical_data(self, module_name):
        list_obj = self.repository.get_shop_group_line_area_details(module_name)
        return self.transform_group_line_area_shops_to_sites(list_obj)

    def get_shop_and_location_map(self,module_name):
        location_wise_shop_name = {}
        location_shop_map = {}
        shop_name_map_1 = {}
        shop_name_map_2 = {}
        data = self.get_all_sites_from_module(module_name)
        for each in data:
            locations = each['locations']
            for each in locations:
                location_name = each['location_name']
                location_wise_shop_name[location_name] = []
                location_shop_map[location_name] =[]
                plants = each['plants']
                for each in plants:
                    shops = each['shops']
                    for each in shops:
                        location_wise_shop_name[location_name].append(each['shop_name'])
                        location_shop_map[location_name].append(each['id'])
                        shop_name_map_1[str(each['id'])] = each['id']
                        shop_name_map_2[str(each['id'])] = each['shop_name']
        result = {
            "shop_name_map_1" : shop_name_map_1,
            "shop_name_map_2" : shop_name_map_2,
            "location_shop_map" : location_shop_map
        }
        return result

    def get_all_sites_from_module_id(self, module_id):
        shops = self.repository.get_shops_by_module_id(module_id)
        return self.transform_shops_to_sites(shops)
    
    def get_shop_and_location_map_by_module_id(self,module_id):
        location_wise_shop_name = {}
        location_shop_map = {}
        shop_name_map_1 = {}
        shop_name_map_2 = {}
        data = self.get_all_sites_from_module_id(module_id)
        for each in data:
            locations = each['locations']
            for each in locations:
                location_name = each['location_name']
                location_wise_shop_name[location_name] = []
                location_shop_map[location_name] =[]
                plants = each['plants']
                for each in plants:
                    shops = each['shops']
                    for each in shops:
                        location_wise_shop_name[location_name].append(each['shop_name'])
                        location_shop_map[location_name].append(each['id'])
                        shop_name_map_1[str(each['id'])] = each['id']
                        shop_name_map_2[str(each['id'])] = each['shop_name']
        result = {
            "shop_name_map_1" : shop_name_map_1,
            "shop_name_map_2" : shop_name_map_2,
            "location_shop_map" : location_shop_map
        }
        return result
    
    def get_location_id_by_location_name(self,location_name):
        respone = self.repository.get_location_id_by_location_name(location_name)
        if respone != None:
            location_id = respone.id
            return location_id
        return respone


    def transform_module_shop_association(self, list_obj):
        module_shop_mapper = dict()
        for data in list_obj:

            shop_id, shop_name, module_id, module_name = data
            shop_obj = {
                "shop_id": shop_id,
                "shop_name": shop_name
            }

            if not module_shop_mapper.get(module_id):
                module_shop_mapper[module_id] = {
                    "module_name": None,
                    "shops": []
                }
                module_shop_mapper[module_id]["module_name"] = module_name
                module_shop_mapper[module_id]["shops"] = [shop_obj.copy()]
            else:
                module_shop_mapper[module_id]["shops"].append(shop_obj.copy())

        return module_shop_mapper

    def get_module_shop_association(self):
        list_obj = self.repository.get_module_shop_association()
        return self.transform_module_shop_association(list_obj)
    
    def get_modules_names_and_id(self):
        res = self.repository.get_modules_names_and_id()
        res = {each.id:each.display_name for each in res}
        return res

    def get_shop_type(self, shop_id):
        return self.repository.get_shop_type(shop_id)

    def get_shop_details_by_module_ids(self, module_ids, aggregate_by_module_id = False):
        data = self.repository.get_shop_detail_by_module_ids(module_ids)
        response = []
        for details in data:
            response.append({
                'module_id': details[0],
                'module_name': details[1],
                'module_display_name': details[2],
                'shop_id': details[3],
                'shop_name': details[4],
                'shop_type': details[5]
            })
        if aggregate_by_module_id:
            module_id_to_shop_details_map = {}
            for info in response:
                if info['module_id'] in module_id_to_shop_details_map:
                    module_id_to_shop_details_map[info['module_id']]['shop_details'].append({
                        'shop_id': info['shop_id'],
                        'shop_name': info['shop_name'],
                        'shop_type': info['shop_type']
                    })
                else:
                    module_id_to_shop_details_map[info['module_id']] = {
                        'module_name': info['module_name'],
                        'module_display_name': info['module_display_name'],
                        'shop_details': [
                            {
                                'shop_id': info['shop_id'],
                                'shop_name': info['shop_name'],
                                'shop_type': info['shop_type']
                            }
                        ]
                    }
            return module_id_to_shop_details_map
        return response
    
    def get_all_shops(self, get_map_of_shop_id_and_name = False):
        model_list = self.repository.get_all()
        shop_list = []
        if get_map_of_shop_id_and_name:
            id_to_name_map ={}
            for model in model_list:
                id_to_name_map[model.id] = model.shop_name
            return id_to_name_map
        else:     
            for model in model_list:
                shop_list.append({
                    "shop_id" : model.id,
                    "shop_name" : model.shop_name,
                    "shop_type" : model.shop_type,
                    "plant_id" : model.plant_id,
                })
            return shop_list
        
    def get_all_module(self, get_map_of_module_id_and_name = False):
        model_list = self.repository.get_all_module()
        module_list = []
        if get_map_of_module_id_and_name:
            id_to_name_map = {}
            for model in model_list:
                id_to_name_map[model.id] = {
                    "module_name" : model.module_name,
                    "display_name": model.display_name
                }
            return id_to_name_map

        for model in model_list:
            module_list.append({
                "id" : model.id,
                "module_name" : model.module_name,
                "display_name": model.display_name
            })
        return module_list
    
    def get_location_details_by_module_ids(self, module_ids, aggregate_by_module_id = False):
        data = self.repository.get_location_details_by_module_ids(module_ids)
        response = []
        for details in data:
            response.append({
                'module_id': details[0],
                'module_name': details[1],
                'module_display_name': details[2],
                'location_id': details[3],
                'location_name': details[4]
            })
        if aggregate_by_module_id:
            module_id_to_location_details_map = {}
            for info in response:
                if info['module_id'] in module_id_to_location_details_map:
                    module_id_to_location_details_map[info['module_id']]['location_details'].append({
                        'location_id': info['location_id'],
                        'location_name': info['location_name']
                    })
                else:
                    module_id_to_location_details_map[info['module_id']] = {
                        'module_name': info['module_name'],
                        'module_display_name': info['module_display_name'],
                        'location_details': [
                            {
                                'location_id': info['location_id'],
                                'location_name': info['location_name']
                            }
                        ]
                    }
            return module_id_to_location_details_map
        return response
    

    def get_shop_id(self, shop_name):
        return self.repository.get_shop_id(shop_name)

    def get_all_plants(self, get_map_of_plant_id_and_details = False):
        '''
        Get the list of plants in list format or aggregated by plant_id
        '''
        model_list = self.repository.get_all_plants()
        plant_list = []
        if get_map_of_plant_id_and_details:
            id_to_detail_map = {}
            for model in model_list:
                id_to_detail_map[model.id] = {
                    "plant_name" : model.plant_name,
                    "location_id": model.location_id
                }
            return id_to_detail_map

        for model in model_list:
            plant_list.append({
                "id" : model.id,
                "plant_name" : model.plant_name,
                "location_id": model.location_id
            })
        return plant_list
    
    def get_all_shops_by_shop_type(self, shop_type):
        '''
        Get the list of shops by shop_types
        '''
        model_list = self.repository.get_all_shops_by_shop_type(shop_type)
        shop_list = []
        for model in model_list:
            shop_list.append({
                'id': model.id,
                'shop_name': model.shop_name,
                'shop_type': model.shop_type,
                'plant_id': model.plant_id
            })
        return shop_list
    
    def get_shop_locations_by_modules(self, module_ids, aggregate_by_module_id = False):
        '''
        Get the list of locations associated to shops by module_ids
        '''
        model_list = self.repository.get_locations_by_module(module_ids)
        location_list = []
        for model in model_list:
            location_list.append({
                'module_id': model.module_id,
                'module_name': model.module_name,
                'shop_id': model.shop_id,
                'plant_id': model.plant_id,
                'location_id': model.location_id,
                'location_name': model.location_name,
                'module_display_name': model.module_display_name
            })
        if aggregate_by_module_id:
            module_id_to_details_map = {}
            for info in location_list:
                if info['module_id'] in module_id_to_details_map:
                    module_id_to_details_map[info['module_id']]['location_details'].append({
                        'shop_id': info['shop_id'],
                        'plant_id': info['plant_id'],
                        'location_id': info['location_id'],
                        'location_name': info['location_name']
                    })
                else:
                    module_id_to_details_map[info['module_id']] = {
                        'module_name': info['module_name'],
                        'module_display_name': info['module_display_name'],
                        'location_details': [
                            {
                                'shop_id': info['shop_id'],
                                'plant_id': info['plant_id'],
                                'location_id': info['location_id'],
                                'location_name': info['location_name']
                            }
                        ]
                    }
            return module_id_to_details_map
        return location_list
    
    def get_all_locations(self, get_map_of_location_id_and_details = False):
        '''
        Get the list of locations in list format or aggregated by location_id
        '''
        model_list = self.repository.get_all_locations()
        location_list = []
        if get_map_of_location_id_and_details:
            id_to_detail_map = {}
            for model in model_list:
                id_to_detail_map[model.id] = {
                    "location_name" : model.location_name
                }
            return id_to_detail_map

        for model in model_list:
            location_list.append({
                "id" : model.id,
                "location_name" : model.location_name
            })
        return location_list
    
    def get_location_wise_shops_by_module(self, module_name):
        '''
        Get the location wise shop names for a particualt module
        '''
        results = self.repository.get_location_wise_shops_by_module(module_name)
        return results
    
    def get_all_sites(self):
        '''
        Get the list of sites in list format
        '''
        model_list = self.repository.get_all_sites()
        sites_list = []
        for model in model_list:
            sites_list.append({
                "id" : model.id,
                "site_name" : model.site_name
            })
        return sites_list
