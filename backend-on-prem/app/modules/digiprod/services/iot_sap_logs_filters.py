from app.modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from app.modules.PSM.repositories.msil_recipe_repository import MSILRecipeRepository
from app.modules.PSM.repositories.msil_downtime_reason_repository import MSILDowntimeReasonRepository
from app.modules.PSM.repositories.msil_downtime_remarks_repository import MSILDowntimeRemarkRepository
from app.modules.digiprod.repositories.iot_sap_shop_equipment_mapping_repository import IOTSapShopEquipmentMappingRepository

IMM_SHOP_ID = '24'


class IotSapLogsFilters:
    def __init__(self, session):
        self.session = session
        self.recipe_repository = MSILRecipeRepository(session)
        self.equipment_repository = MSILEquipmentRepository(session)
        self.downtime_reason_repository = MSILDowntimeReasonRepository(session)
        self.remarks_repository = MSILDowntimeRemarkRepository(session)
        self.iot_sap_shop_equipment_mapping_repository = IOTSapShopEquipmentMappingRepository(
            session)

    def get_sap_logs_downtime_filters(self, shop_id):
        """
        Returns filter options for SAP downtime logs for the given shop_id.

        Includes:
        - Header material
        - Work center (via shop equipment mapping or equipment)
        - Downtime reasons
        """
        header_material = self.recipe_repository.get_header_material_by_shop(
            shop_id)

        if shop_id == IMM_SHOP_ID:
            work_center = self.iot_sap_shop_equipment_mapping_repository.get_sap_work_center_by_shop(
                shop_id)
        else:
            work_center = self.equipment_repository.get_equipment_by_shop(
                shop_id)

        reasons = self.downtime_reason_repository.get_reasons_by_shop(shop_id)
        #  add remartks to each disct of reasons
        for reason in reasons:
            reason['remarks'] = self.remarks_repository.get_remarks_by_reason_id(
                reason['reason_id'])

        return {
            "header_material": header_material,
            "work_center": work_center,
            "reasons": reasons
        }

    def get_sap_logs_plan_filters(self, shop_id):
        """Get filters for SAP plan logs based on shop_id."""
        if shop_id == IMM_SHOP_ID:
            work_center = self.iot_sap_shop_equipment_mapping_repository.get_sap_work_center_by_shop(
                shop_id)
        else:
            work_center = self.equipment_repository.get_equipment_by_shop(
                shop_id)

        return {
            "work_center": work_center
        }

    def get_sap_logs_production_filters(self, shop_id):
        """Get filters for SAP production logs based on shop_id."""
        machine = self.recipe_repository.get_recipe_filters_by_shop(shop_id)

        return {
            "machine": machine
        }
