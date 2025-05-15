import datetime
from app.modules.PSM.repositories.models.msil_alert_notification import AlertNotification
from app.modules.PSM.repositories.models.msil_part import MSILPart
from ..repositories.msil_recipe_repository import MSILRecipeRepository
from ..repositories.models.msil_recipe import MSILRecipe
from .service import Service
import pytz

ist_tz = pytz.timezone('Asia/Kolkata')

class MSILRecipeService(Service):
    
    def __init__(self, repository : MSILRecipeRepository):
        super().__init__(repository, self.transform_model_to_dict, 
                         self.transform_dict_to_model)
        self.repository = repository
    
    def get_input_material(self, output_part_ids, shop_id):   
        materials, scenario = self.repository.get_input_material(output_part_ids, shop_id)
        return self.transform_input_materials(materials, scenario)
    
    def get_recipe_by_program_number(self, program_number, equipment_id, shop_id):
        recipe : MSILRecipe = self.repository.filter_by(data_number=program_number, equipment_id=equipment_id, shop_id=shop_id)
        if recipe:
            return {
                "input_1" : recipe.input_1,
                "input_2" : recipe.input_2,
                "output_1" : recipe.output_1,
                "output_2" : recipe.output_2
            }
        elif program_number != "0" and program_number != 0:
            notification_obj = AlertNotification()
            notification_obj.notification = f"Recipe not found for program number {program_number} and equipment id {equipment_id}"
            notification_obj.notification_metadata = None
            notification_obj.alert_type = "Data number Error"
            notification_obj.created_at = datetime.datetime.now(ist_tz).replace(tzinfo=None)
            notification_obj.shop_id = shop_id
            self.repository.add(notification_obj)
            raise Exception(f"Recipe not found for program number {program_number} and equipment id {equipment_id}")
    
    def transform_input_materials(self, materials, scenario):
        if materials == []:
            return {
                "recipe" : { "error" : "Incorrect combination chosen"}
            }
        recipe_obj = {
        }
        input_1 : MSILPart = None
        input_2 : MSILPart = None
        if scenario !=  "ONE_OUT_COMBINED":
            for material in materials:
                recipe : MSILRecipe = material[0]
                if recipe.output_1:
                    recipe_obj[recipe.output_1] = []
                    if recipe.input_1:
                        recipe_obj[recipe.output_1].append("input_1")
                    if recipe.input_2:
                        recipe_obj[recipe.output_1].append("input_2")
                if recipe.output_2:
                    recipe_obj[recipe.output_2] = []
                    if recipe.input_1:
                        recipe_obj[recipe.output_2].append("input_1")
                    if recipe.input_2:
                        recipe_obj[recipe.output_2].append("input_2")
                        
                input_1 = input_1 or material[1]
                input_2 = input_2 or material[2]
                    
        else:
            recipe_obj = {
                materials[0][0].output_1 : ["input_1"],
                materials[1][0].output_1 : ["input_2"]
            }
            input_1 = materials[0][1]
            input_2 = materials[1][1]
            if materials[0][2] != None:
                recipe_obj["error"] = "Incorrect combination chosen"
        input_materials = { "recipe" : recipe_obj }
        if input_1:
            input_materials["input_1"] = {
                "material_code" : input_1.material_code,
                "part_name" : input_1.part_name,
                "pe_code" : input_1.pe_code,
                "description" : input_1.description,
                "material_type" : input_1.material_type,
                "supplier" : input_1.supplier,
                "unit" : input_1.unit,
                "thickness_nominal" : input_1.thickness_nominal,
                "thickness_upper" : input_1.thickness_upper,
                "thickness_lower" : input_1.thickness_lower,
                "thickness_tolerance_unit" : input_1.thickness_tolerance_unit,
                "thickness_unit" : input_1.thickness_unit,
                "width_nominal" : input_1.width_nominal,
                "width_upper" : input_1.width_upper,
                "width_lower" : input_1.width_lower,
                "width_unit" : input_1.width_unit,
                "width_tolerance_unit" : input_1.width_tolerance_unit,
                "weight" : input_1.weight,
                "weight_unit" : input_1.weight_unit
                }
        
        if input_2:
            input_materials["input_2"] = {
            "material_code" : input_2.material_code,
            "part_name" : input_2.part_name,
            "pe_code" : input_2.pe_code,
            "description" : input_2.description,
            "material_type" : input_2.material_type,
            "supplier" : input_2.supplier,
            "unit" : input_2.unit,
            "thickness_nominal" : input_2.thickness_nominal,
            "thickness_upper" : input_2.thickness_upper,
            "thickness_lower" : input_2.thickness_lower,
            "thickness_tolerance_unit" : input_2.thickness_tolerance_unit,
            "thickness_unit" : input_2.thickness_unit,
            "width_unit" : input_2.width_unit,
            "width_nominal" : input_2.width_nominal,
            "width_upper" : input_2.width_upper,
            "width_lower" : input_2.width_lower,
            "width_tolerance_unit" : input_2.width_tolerance_unit,
            "weight" : input_2.weight,
            "weight_unit" : input_2.weight_unit
            }
        return input_materials

    def transform_model_to_dict(self, model : MSILRecipe):
        return {
            "id": model.id,
            "equipment_id": model.equipment_id,
            "data_number": model.data_number,
            "data_number_description": model.data_number_description,
            "input_1": model.input_1,
            "input_1_qty": model.input_1_qty,
            "input_2": model.input_2,
            "input_2_qty": model.input_2_qty,
            "output_1": model.output_1,
            "output_1_qty": model.output_1_qty,
            "output_2": model.output_2,
            "output_2_qty": model.output_2_qty,
            "die_obj": model.die_obj,
            "input_storage_unit_group": model.input_storage_unit_group,
            "output_storage_unit_group": model.output_storage_unit_group,
            "shop_id": model.shop_id,
        }
    
    def transform_dict_to_model(self, dict):
        pass

    # def update_input_materials(self, input_material_updates):
        
    #     return self.repository.update_input_materials(input_material_updates)


    def add_input_materials(self, input_material_data_list):
        
        return self.repository.add_input_materials(input_material_data_list)

    def get_recipe_by_equipment_and_parts(self, equipment_id, part_1, part_2):
        """
        Fetch the recipe based on equipment_id, part_1, and part_2 (output materials).
        """
        recipe_data = self.repository.get_recipe_by_equipment_and_parts(equipment_id, part_1, part_2)

        if recipe_data:
            return self.transform_model_to_dict(recipe_data)
        else:
            return {"error": "No recipe found for the given equipment and parts."}