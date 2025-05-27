from app.modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from app.modules.PSM.repositories.msil_recipe_repository import MSILRecipeRepository
from app.modules.PSM.repositories.msil_downtime_reason_repository import MSILDowntimeReasonRepository

IMM_SHOP_ID = 24


class IotSapLogsFilters:
    def __init__(self, session):
        self.session = session
        self.recipe_repository = MSILRecipeRepository(session)
        self.equipment_repository = MSILEquipmentRepository(session)
        self.downtime_reason_repository = MSILDowntimeReasonRepository(session)

    def get_sap_logs_downtime_filters(self, shop_id):
        """Get filters for SAP downtime logs based on shop_id."""
        header_material = self.recipe_repository.get_header_material_by_shop(
            shop_id)

        # Todo: For IMM shop, fetch work center from iot_sap_shop_equipment_mapping
        work_center = self.equipment_repository.get_equipment_by_shop(shop_id)
        reasons = self.downtime_reason_repository.get_resons_by_shop(shop_id)

        return {
            "header_material": header_material,
            "work_center": work_center,
            "reasons": reasons
        }

    def get_sap_logs_plan_filters(self, shop_id):
        """Get filters for SAP plan logs based on shop_id."""
        work_center = self.equipment_repository.get_equipment_by_shop(shop_id)

        return {
            "work_center": work_center
        }

    def get_sap_logs_production_filters(self, shop_id):
        """Get filters for SAP production logs based on shop_id."""
        machine = self.recipe_repository.get_recipe_filters_by_shop(shop_id)

        return {
            "machine": machine
        }
