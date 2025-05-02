from ..repositories.msil_part_repository import MSILPartRepository
from ..repositories.msil_model_repository import MSILModelRepository
from ..repositories.models.msil_part import MSILPart
from .service import Service

class MSILPartService(Service):
    def __init__(self, repository : MSILPartRepository):
        super().__init__(repository, self.transform_model_to_dict, 
                         self.transform_dict_to_model)
        self.repository = repository

    def get_part_filters(self, shop_id):
        
        filters = self.repository.get_unique_filters(shop_id)
        return self.transform_filters(filters)
    
    def transform_filters(self,filters):
        filter_list = []
        for filter in filters:
            filter_list.append({
                "machine_group" : filter[0],
                "machine" : filter[1],
                "model" : filter[2],
                "part_name" : filter[3],
                "pe_code" :  filter[4],
                "priority_max" : filter[5]
            })
        return filter_list


    def transform_model_to_dict(self, model: MSILPart):
        return {
            "material_code" : model.material_code,
            "part_name" : model.part_name,
            "pe_code" : model.pe_code,
            "model" : model.model,
            "description" : model.description,
            "material_type" : model.material_type,
            "supplier" : model.supplier,
            "unit" : model.unit,
            "thickness_nominal" : model.thickness_nominal,
            "thickness_upper" : model.thickness_upper,
            "thickness_lower" : model.thickness_lower,
            "thickness_tolerance_unit" : model.thickness_tolerance_unit,
            "width_nominal" : model.width_nominal,
            "width_upper" : model.width_upper,
            "width_lower" : model.width_lower,
            "width_tolerance_unit" : model.width_tolerance_unit,
            "weight" : model.weight,
            "expiry_time" : model.expiry_time,
            "expiry_uom" : model.expiry_uom,
            "origin" : model.origin,
            "grade" : model.grade,
            "shop_id" : model.shop_id
        }

    def transform_dict_to_model(self, dict_obj):
        model = MSILPart()
        model.material_code = dict_obj.get("material_code", None)
        model.part_name = dict_obj.get("part_name", None)
        model.pe_code = dict_obj.get("pe_code", None)
        model.model = dict_obj.get("model", None)
        model.description = dict_obj.get("description", None)
        model.material_type = dict_obj.get("material_type", None)
        model.supplier = dict_obj.get("supplier", None)
        model.unit = dict_obj.get("unit", None)
        model.thickness_nominal = dict_obj.get("thickness_nominal", None)
        model.thickness_upper = dict_obj.get("thickness_upper", None)
        model.thickness_lower = dict_obj.get("thickness_lower", None)
        model.thickness_tolerance_unit = dict_obj.get("thickness_tolerance_unit", None)
        model.width_nominal = dict_obj.get("width_nominal", None)
        model.width_upper = dict_obj.get("width_upper", None)
        model.width_lower = dict_obj.get("width_lower", None)
        model.width_tolerance_unit = dict_obj.get("width_tolerance_unit", None)
        model.weight = dict_obj.get("weight", None)
        model.expiry_time = dict_obj.get("expiry_time", None)
        model.expiry_uom = dict_obj.get("expiry_uom", None)
        model.origin = dict_obj.get("origin", None)
        model.grade = dict_obj.get("grade", None)
        model.shop_id = dict_obj.get("shop_id", None)
        return model

    