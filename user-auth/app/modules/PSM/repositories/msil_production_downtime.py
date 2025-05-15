from .repository import Repository
from .models.msil_downtime import MSILDowntime
from .models.msil_downtime_reason import MSILDowntimeReasons
from .models.msil_downtime_remark import MSILDowntimeRemarks
from .models.msil_equipment import MSILEquipment
from .models.msil_production import MSILProduction
from .models.msil_shift import MSILShift
from .models.msil_model import MSILModel
from .models.msil_part import MSILPart
from sqlalchemy import (
    extract,
    func,
    desc,
    case,
    and_,
    cast
)
from sqlalchemy.orm import Session
import datetime
class MSILProductionDowntimeRepository(Repository):
    """

    """

    def __init__(self,session:Session):
        self.session = session
        self.model_type = MSILDowntime
        self.remark_model = MSILDowntimeRemarks

    


    def get_downtime_filtered(self, shop_id, shift, equipment_name=None, model_name=None, part_name=None):
       
        current_date = datetime.now().date()

        with self.session:
            query = self.session.query(self.model_type, MSILEquipment.name, MSILModel.model_name, MSILPart.part_name, MSILDowntimeReasons.reason, MSILDowntimeRemarks.remark, self.model_type.shift) \
                .filter(self.model_type.shift == shift,self.model_type.shop_id == shop_id, self.model_type.start_time >= current_date, self.model_type.end_time < current_date + datetime.timedelta(days=1))
            
            if shift:
                query = query.filter(self.model_type.shift == shift)

            if equipment_name:
                query = query.filter(MSILEquipment.name == equipment_name)

            if model_name:
                query = query.filter(MSILModel.model_name == model_name)

            if part_name:
                query = query.filter(MSILPart.part_name == part_name)

            query = query.join(MSILModel, self.model_type.model_id == MSILModel.id)
            query = query.join(MSILPart, self.model_type.material_code == MSILPart.material_code)
            query = query.join(MSILEquipment, self.model_type.equipment_id == MSILEquipment.id)
            query = query.join(MSILDowntimeReasons, self.model_type.reason_id == MSILDowntimeReasons.id)
            query = query.join(MSILDowntimeRemarks, self.model_type.remark_id == MSILDowntimeRemarks.id, isouter=True)
            # query = query.join(MSILShift, self.model_type.shift == MSILShift.shift_name)

            return query.order_by(desc(self.model_type.start_time)).all()


