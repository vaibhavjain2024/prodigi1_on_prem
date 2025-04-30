from modules.PSM.repositories.models.msil_part import MSILPart
from modules.PSM.repositories.models.msil_recipe import MSILRecipe
from modules.PSM.repositories.models.msil_input_material import MSILInputMaterial
from .repository import Repository
from sqlalchemy.orm import Session
from sqlalchemy import (
    and_,
    desc,
    func,
    case,
    or_
)
from sqlalchemy.orm import aliased

class MSILRecipeRepository(Repository):
    """
    MSILMachineRepository to manage MSILMachine data table.
    """
    def __init__(self, session: Session ):
        self.session = session
        self.model_type = MSILRecipe
        self.input_model = MSILInputMaterial
    
    def get_input_material(self, output_part_ids, shop_id):
        scenario = ""
        with self.session:
            input_1_part = aliased(MSILPart)
            input_2_part = aliased(MSILPart)

            ## one out scenarios
            if len(output_part_ids) == 1:
                query = self.session.query(
                self.model_type, 
                input_1_part, 
                input_2_part
                ) \
                .select_from(self.model_type) \
                .filter(self.model_type.shop_id == shop_id) \
                .filter(or_(self.model_type.output_1 == output_part_ids[0],
                            self.model_type.output_2 == output_part_ids[0])) \
                .join(input_1_part, input_1_part.material_code == self.model_type.input_1, isouter=True) \
                .join(input_2_part, input_2_part.material_code == self.model_type.input_2, isouter=True) \
                .all()
                scenario = "ONE_OUT"
            else:
                ## two out scenario
                query = self.session.query(
                    self.model_type, 
                    input_1_part, 
                    input_2_part
                ) \
                .select_from(self.model_type) \
                .filter(self.model_type.shop_id == shop_id) \
                .filter(or_(
                    and_(self.model_type.output_1 == output_part_ids[0],
                        self.model_type.output_2 == output_part_ids[1]),
                    and_(self.model_type.output_1 == output_part_ids[1],
                        self.model_type.output_2 == output_part_ids[0]),
                    ),
                 ) \
                .join(input_1_part, input_1_part.material_code == self.model_type.input_1, isouter=True) \
                .join(input_2_part, input_2_part.material_code == self.model_type.input_2, isouter=True) \
                .all()
                scenario = "TWO_OUT"
                if query == []:
                    ## one in one out double scenarios
                    query = self.session.query(
                        self.model_type, 
                        input_1_part, 
                        input_2_part
                    ) \
                    .select_from(self.model_type) \
                    .filter(self.model_type.shop_id == shop_id) \
                    .filter(or_(
                        and_(self.model_type.output_1 == output_part_ids[0],
                            self.model_type.output_2 == None),
                        and_(self.model_type.output_1 == output_part_ids[1],
                            self.model_type.output_2 == None),
                        and_(self.model_type.output_2 == output_part_ids[0],
                            self.model_type.output_1 == None),
                        and_(self.model_type.output_2 == output_part_ids[1],
                            self.model_type.output_1 == None)
                        ),
                    ) \
                    .join(input_1_part, input_1_part.material_code == self.model_type.input_1, isouter=True) \
                    .join(input_2_part, input_2_part.material_code == self.model_type.input_2, isouter=True) \
                    .all()
                    scenario = "ONE_OUT_COMBINED"

            return query,scenario


    def add_input_materials(self, input_material_data_list):
        """
        Args:
                - 'production_id'
                - 'batch_id'
                - 'part_name'
                - 'thickness'
                - 'width'
                - 'material_details
                - 'material_qty

        """
        num_rows_added = 0

        with self.session:
            for input_data in input_material_data_list:
                production_id = input_data.get('production_id')
                batch_id = input_data.get('batch_id')
                part_name = input_data.get('part_name')
                thickness = input_data.get('thickness')
                width = input_data.get('width')
                material_details = input_data.get('material_details')
                material_qty = input_data.get('material_qty')

                
                # existing_entry = self.session.query(MSILInputMaterial) \
                #     .filter(MSILInputMaterial.production_id == production_id) \
                #     .filter(MSILInputMaterial.batch_id == batch_id) \
                #     .filter(MSILInputMaterial.part_name == part_name) \
                #     .first()

                # if existing_entry:
                #     # existing_entry.thickness=thickness,
                #     # existing_entry.width=width,
                #     # existing_entry.details=material_details,
                #     # existing_entry.material_qty=material_qty
                #     # self.session.merge(existing_entry)
                #     # self.session.commit()
                #     pass
                #     # raise ValueError("Input material with the same production_id, batch_id, and part_name already exists.")
                # else:
                input_material = MSILInputMaterial()
                input_material.production_id=production_id,
                input_material.batch_id=batch_id,
                input_material.part_name=part_name,
                input_material.thickness=thickness,
                input_material.width=width,
                input_material.details=material_details,
                input_material.material_qty=material_qty
                self.add(input_material)
                num_rows_added += 1

        return num_rows_added
    
    def recipe_combinations(self,shop_id):
        recipe_combinations=[]
        with self.session:
            results = self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id).all()
            for i in results:
                recipe_combinations.append([i.equipment_id,i.data_number,i.output_1,i.output_2])
            return recipe_combinations
    
    def update_recipe(self,shop_id,eqp_id,number,out_1,out_2,model):
        with self.session:
            result = self.session.query(self.model_type).filter_by(data_number=number,
                                                                shop_id=shop_id,
                                                                equipment_id=eqp_id,
                                                                output_1=out_1,
                                                                output_2=out_2).update(model)
            self.session.commit()
    
    # def add_input_materials(self, input_material_data_list):
    #     """
    #     Args:
    #             - 'production_id'
    #             - 'batch_id'
    #             - 'part_name'
    #             - 'thickness'
    #             - 'width'
    #             - 'material_details
    #             - 'material_qty

    #     """
    #     num_rows_added = 0
    #     batch_wise_input_material = {}

    #     with self.session:

    #         for input_data in input_material_data_list:
    #             # production_id = input_data.get('production_id')
    #             batch_id = input_data.get('batch_id')
    #             # part_name = input_data.get('part_name')
    #             # thickness = input_data.get('thickness')
    #             # width = input_data.get('width')
    #             # material_details = input_data.get('material_details')
    #             # material_qty = input_data.get('material_qty')
    #             batch_group = batch_wise_input_material.get(batch_id, None)
    #             if batch_group == None:
    #                 batch_wise_input_material[batch_id]=[]
    #             batch_wise_input_material[batch_id].append(input_data)
    #         # print(batch_wise_input_material)

    #         for data in batch_wise_input_material.keys():
    #             # print(data)
    #             input_material_batch = batch_wise_input_material[data]
    #             # print(input_material_batch)

    #             if len(input_material_batch) == 1:
    #                 print("inside 1 input for batch")

    #                 first_input_material = input_material_batch[0]
    #                 # print(first_input_material)
    #                 # production_id_1 = first_input_material['production_id']
    #                 # print(production_id_1)
    #                 # thickness_1 = first_input_material['thickness']
    #                 # print(thickness_1)
    #                 # second_input_material = input_material_batch[1]

    #                 # print(second_input_material)
    #                 existing_entries = self.session.query(MSILInputMaterial) \
    #                     .filter(MSILInputMaterial.production_id == first_input_material['production_id']) \
    #                     .filter(MSILInputMaterial.batch_id == first_input_material['batch_id']) \
    #                     .filter(MSILInputMaterial.part_name == first_input_material['part_name']) \
    #                     .first()
    #                 # print(existing_entries)

    #                 if existing_entries:
    #                     existing_entries.thickness=first_input_material['thickness'],
    #                     existing_entries.width=first_input_material['width'],
    #                     existing_entries.details=first_input_material['material_details'],
    #                     existing_entries.material_qty=first_input_material['material_qty']
    #                     self.session.merge(existing_entries)
    #                     self.session.commit()
    #                 #     raise ValueError("Input material with the same production_id, batch_id, and part_name already exists.")
    #                 else:
    #                     input_material = MSILInputMaterial()
    #                     input_material.production_id=first_input_material['production_id'],
    #                     input_material.batch_id=first_input_material['batch_id'],
    #                     input_material.part_name=first_input_material['part_name'],
    #                     input_material.thickness=first_input_material['thickness'],
    #                     input_material.width=first_input_material['width'],
    #                     input_material.details=first_input_material['material_details'],
    #                     input_material.material_qty=first_input_material['material_qty']
    #                     # input_material.production_id=production_id,
    #                     # input_material.batch_id=batch_id,
    #                     # input_material.part_name=part_name,
    #                     # input_material.thickness=thickness,
    #                     # input_material.width=width,
    #                     # input_material.details=material_details,
    #                     # input_material.material_qty=material_qty
    #                     self.add(input_material)
    #                 num_rows_added += 1
    #             else:
    #                 print("inside 2 input for same batch")

    #                 first_input_material = input_material_batch[0]
    #                 second_input_material = input_material_batch[1]
    #                 if first_input_material:
    #                     existing_entries_1 = self.session.query(MSILInputMaterial) \
    #                     .filter(MSILInputMaterial.production_id == first_input_material['production_id']) \
    #                     .filter(MSILInputMaterial.batch_id == first_input_material['batch_id']) \
    #                     .filter(MSILInputMaterial.part_name == first_input_material['part_name']) \
    #                     .first()

    #                     if existing_entries_1:
    #                         existing_entries_1.thickness=first_input_material['thickness'],
    #                         existing_entries_1.width=first_input_material['width'],
    #                         existing_entries_1.details=first_input_material['material_details'],
    #                         existing_entries_1.material_qty=first_input_material['material_qty']
    #                         self.session.merge(existing_entries_1)
    #                         self.session.commit()

    #                     else:
    #                         input_material = MSILInputMaterial()
    #                         input_material.production_id=first_input_material['production_id'],
    #                         input_material.batch_id=first_input_material['batch_id'],
    #                         input_material.part_name=first_input_material['part_name'],
    #                         input_material.thickness=first_input_material['thickness'],
    #                         input_material.width=first_input_material['width'],
    #                         input_material.details=first_input_material['material_details'],
    #                         input_material.material_qty=first_input_material['material_qty']
    #                         self.add(input_material)
    #                     num_rows_added += 1
                        
                        
                
    #                 elif second_input_material:
    #                     existing_entries_2 = self.session.query(MSILInputMaterial) \
    #                     .filter(MSILInputMaterial.production_id == second_input_material['production_id']) \
    #                     .filter(MSILInputMaterial.batch_id == second_input_material['batch_id']) \
    #                     .filter(MSILInputMaterial.part_name == second_input_material['part_name']) \
    #                     .first()

    #                     if existing_entries_2:
    #                         existing_entries_2.thickness=second_input_material['thickness'],
    #                         existing_entries_2.width=second_input_material['width'],
    #                         existing_entries_2.details=second_input_material['material_details'],
    #                         existing_entries_2.material_qty=second_input_material['material_qty']
    #                         self.session.merge(existing_entries_2)
    #                         self.session.commit()

    #                     else:
    #                         input_material = MSILInputMaterial()
    #                         input_material.production_id=second_input_material['production_id'],
    #                         input_material.batch_id=second_input_material['batch_id'],
    #                         input_material.part_name=second_input_material['part_name'],
    #                         input_material.thickness=second_input_material['thickness'],
    #                         input_material.width=second_input_material['width'],
    #                         input_material.details=second_input_material['material_details'],
    #                         input_material.material_qty=second_input_material['material_qty']
    #                         self.add(input_material)
    #                     num_rows_added += 1
    #     return num_rows_added


    # def update_input_materials(self, input_material_updates):

    #     with self.session:
    #         for update_data in input_material_updates:
    #             input_material_id = update_data.get('input_material_id')
    #             details = update_data.get('details')
    #             thickness = update_data.get('thickness')
    #             width = update_data.get('width')
    #             material_qty = update_data.get('material_qty')
            
    #             if input_material_id:
    #                 query = self.session.query(MSILInputMaterial).filter(MSILInputMaterial.id == input_material_id)

    #                 if details is not None:
    #                     query.update({MSILInputMaterial.details: details})
    #                 if thickness is not None:
    #                     query.update({MSILInputMaterial.thickness: thickness})
    #                 if width is not None:
    #                     query.update({MSILInputMaterial.width: width})
    #                 if material_qty is not None:
    #                     query.update({MSILInputMaterial.material_qty: material_qty})
    #                 self.session.commit()

    #     return True

    def get_recipe_by_equipment_and_parts(self, equipment_id, output_1, output_2):
        """
        Fetch the recipe based on equipment_id and output_1 (part_1), output_2 (part_2).
        """
        with self.session:
            result = self.session.query(self.model_type) \
                .filter(self.model_type.equipment_id == equipment_id) \
                .filter(
                or_(
                    and_(
                        self.model_type.output_1 == output_1,
                        self.model_type.output_2 == output_2
                    ),
                    and_(
                        self.model_type.output_1 == output_2,
                        self.model_type.output_2 == output_1
                    ),
                    and_(
                        self.model_type.output_1 == output_1,
                        self.model_type.output_2.is_(None)  # Case where output_2 is NULL
                    ),
                    and_(
                        self.model_type.output_1 == output_2,
                        self.model_type.output_2.is_(None)  # Case where output_2 is NULL
                    )
                )
            ) \
                .first()  # Fetch the first matching recipe
            return result