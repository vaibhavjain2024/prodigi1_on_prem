from app.modules.PSM.repositories.models.msil_batch import MSILBatch
from app.modules.PSM.repositories.models.msil_quality_punching import MSILQualityPunching
from app.modules.PSM.repositories.repository import Repository
from app.modules.PSM.repositories.models.msil_input_material import MSILInputMaterial
from sqlalchemy.orm import Session
import datetime
import pytz
from sqlalchemy import (
    and_,
    desc,
    cast,
    Date,
    func,
    case ,
    not_   ,
    or_,
    select
)

ist_tz = pytz.timezone('Asia/Kolkata')


class MSILBatchRepository(Repository):

    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILBatch

    def get_batches_with_null_end_time(self,shift_start=None,shift_end=None):
        filters = []
        if shift_start is not None and shift_end is not None:
            filters.append(MSILBatch.start_time >= shift_start)
            filters.append(MSILBatch.start_time < shift_end)
        with self.session:
            query = self.session.query(
                MSILBatch.id,
                MSILBatch.name,
                MSILBatch.shift,
                MSILBatch.start_time,
                MSILBatch.end_time,
                MSILBatch.prod_qty,
                MSILBatch.input_id,
                MSILBatch.output_id,
                MSILBatch.production_id,
                MSILBatch.material_code,
                MSILBatch.SPM,
                MSILQualityPunching.equipment_id,
                MSILQualityPunching.shop_id
            ) \
                .join(MSILBatch,MSILBatch.id == MSILQualityPunching.batch_id)\
                .filter(self.model_type.end_time.is_(None)) \
                .filter(*filters)\
                .all()
            return query
    
    def get_max_of_batch_id(self):
        with self.session:
            return self.session.query(
                func.max(MSILBatch.id)
            ).select_from(MSILBatch)\
            .first()
        
        
    def update_unfinished_batches(self,batch_id,end_time):
        """
        """
        self.session.query(MSILBatch).filter(MSILBatch.id == batch_id).update(
                {MSILBatch.end_time: end_time}, synchronize_session=False
            )
        self.session.commit()

    def bulk_insert_batches(self,batch_arr):
        self.bulk_insert(batch_arr)

    # def get_shop_id(self, production_id):
    #     production: MSILProduction = self.get(production_id)
    #     equipment: MSILEquipment = self.session.query(MSILEquipment) \
    #         .filter(MSILEquipment.id == production.equipment_id).first()
    #
    #     return  equipment.shop_id

    def get_batches_with_input_materials(self, batch_id: int):
        """
        Query for a batch along with its associated input materials.
        """
        with self.session:
            result = (
                self.session.query(self.model_type, MSILInputMaterial)
                .join(MSILInputMaterial, self.model_type.id == MSILInputMaterial.batch_id)
                .filter(self.model_type.id == batch_id)
                .order_by(MSILInputMaterial.id)
                .all() #all() to get all input materials associated to the batch
            )
        return result

    def get_batches(self, batch_ids):
        with self.session:
            return self.session.query(self.model_type) \
                                .filter(self.model_type.id.in_(batch_ids) ) \
                                .all()
