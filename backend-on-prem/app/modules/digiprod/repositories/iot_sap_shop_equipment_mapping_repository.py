from .repository import Repository
from .models.iot_sap_shop_equipment_mapping import iotSAPshopEquipmentMapping
from sqlalchemy.orm import Session


class IOTSapShopEquipmentMappingRepository(Repository):
    """IOTSapShopEquipmentMappingRepository to manage IOTSapShopEquipmentMapping data table.

    Args:
        Repository (class): Base repository
    """

    def __init__(self, session: Session):
        self.session = session
        self.model_type = iotSAPshopEquipmentMapping

    def get_sap_work_center_by_shop(self, iot_shop_id):
        """Get SAP work center by IoT shop ID."""
        with self.session:
            result = self.session.query(self.model_type.sap_work_center) \
                .filter(self.model_type.iot_shop_id == iot_shop_id) \
                .all()
            return [row.sap_work_center for row in result] if result else None
