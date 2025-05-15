from app.modules.PSM.repositories.models.msil_model import MSILModel
from app.modules.PSM.repositories.models.msil_plan import MSILPlan
from .repository import Repository
from .models.msil_part import MSILPart
from .models.msil_equipment import MSILEquipment
from .models.msil_recipe import MSILRecipe
from sqlalchemy.orm import Session
from sqlalchemy import (
    and_,
    desc,
    func,
    case,
    text
)


class MSILPartRepository(Repository):
    """
    MSILPartRepository to manage MSILPart data table.
    """

    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILPart

    def get_unique_filters(self, shop_id):
        with self.session:
            priority_subquery = self.session.query(
                MSILPlan.material_code.label("material_code"),
                func.max(MSILPlan.priority).label("priority_max")) \
                .group_by(MSILPlan.material_code) \
                .subquery()

            output_subquery = self.get_part_equipment()

            return self.session.query(output_subquery.c.equipment_group, output_subquery.c.equipment_name,
                                      MSILModel.model_name, self.model_type.part_name,
                                      self.model_type.pe_code, priority_subquery.c.priority_max) \
                .join(MSILModel, self.model_type.model_id == MSILModel.id) \
                .join(output_subquery, self.model_type.material_code == output_subquery.c.material_code) \
                .join(priority_subquery, priority_subquery.c.material_code == self.model_type.material_code) \
                .filter(MSILModel.shop_id == shop_id) \
                .distinct().all()

    def get_part_equipment(self):

        with self.session:
            output_1_subquery = self.session.query(MSILRecipe.equipment_id.label('equipment_id'),
                                                   MSILRecipe.output_1.label('material_code')).join(MSILPart,
                                                                                                    MSILRecipe.output_1 == MSILPart.material_code)
            output_2_subquery = self.session.query(MSILRecipe.equipment_id.label('equipment_id'),
                                                   MSILRecipe.output_2.label('material_code')).join(MSILPart,
                                                                                                    MSILRecipe.output_2 == MSILPart.material_code)
            combined = output_1_subquery.union_all(output_2_subquery).subquery()
            equipment_query = self.session.query(combined.c.material_code.label('material_code'),
                                                 MSILEquipment.id.label('equipment_id'),
                                                 MSILEquipment.name.label('equipment_name'),
                                                 MSILEquipment.equipment_group.label('equipment_group')).join(
                MSILEquipment, combined.c.equipment_id == MSILEquipment.id).subquery()

            return equipment_query

    def check_part(self, part_name, material_code, pe_code, model_id, equipment_id):

        with self.session:
            output_subquery = self.get_part_equipment()
            query = self.session.query(self.model_type) \
                .join(output_subquery, self.model_type.material_code == output_subquery.c.material_code) \
                .filter(self.model_type.part_name == part_name
                        , self.model_type.material_code == material_code
                        , self.model_type.pe_code == pe_code
                        , self.model_type.model_id == model_id
                        , output_subquery.c.equipment_id == equipment_id).first()
            if query:
                return True
            return False

    def check_parts(self, part_list):
        with self.session:
            query_params = "ARRAY["
            for part in part_list:
                query_params = query_params + "('" + \
                               part["row_number"] + \
                               "','" + part["model_name"] + \
                               "','" + part["machine_name"] + \
                               "','" + part["part_name"] + \
                               "','" + part["part_number"] + \
                               "','" + part["pe_code"] + \
                               "'),"
            query_params = query_params[:-1] + "]::part_details[]"

            parts_not_found = self.session.execute(
                text("SELECT public.check_combination_exists(" + query_params + ")")).first()
            if parts_not_found:
                return parts_not_found[0]

    def check_for_names(self, part_names):
        with self.session:
            results = self.session.query(self.model_type.part_name).where(
                self.model_type.part_name.in_(part_names)).distinct().all()
            return results

    def check_for_numbers(self, part_numbers):
        with self.session:
            results = self.session.query(self.model_type.material_code).where(
                self.model_type.material_code.in_(part_numbers)).distinct().all()
            return results

    def check_for_codes(self, part_codes):
        with self.session:
            results = self.session.query(self.model_type.pe_code).where(
                self.model_type.pe_code.in_(part_codes)).distinct().all()
            return results

    def material_codes(self):
        material_codes = []
        with self.session:
            results = self.session.query(self.model_type).all()
            for i in results:
                material_codes.append(i.material_code)
            return material_codes

    def update_part(self, material_code, model, shop_id):
        with self.session:
            self.session.query(self.model_type).filter_by(material_code=material_code, shop_id=shop_id).update(model)
            self.session.commit()

    def check_existing_part_for_different_shops(self, part_numbers, shop_id):
        with self.session:
            query = self.session.query(self.model_type.material_code).filter(
                and_(self.model_type.material_code.in_(part_numbers), self.model_type.shop_id != shop_id)).all()
            return query
