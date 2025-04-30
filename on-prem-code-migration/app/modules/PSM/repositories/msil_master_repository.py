from .models.msil_digiprod_master import MSILDigiprodMaster
from .repository import Repository
from sqlalchemy.orm import Session
from sqlalchemy import (
    desc
)

class MSILDigiprodMasterRepository(Repository):
    """MSILDigiprodMaster to manage Master data table.
    
    Args:
        Repository (class): Base repository
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILDigiprodMaster

    def get_previous_file(self, shop_id):
        with self.session:
            return self.session.query(MSILDigiprodMaster) \
                            .filter(MSILDigiprodMaster.shop_id == shop_id) \
                            .order_by(desc(MSILDigiprodMaster.version)) \
                            .first()
    
    def get_masters(self, shop_id):
        with self.session:
            return self.session.query(MSILDigiprodMaster) \
                                .filter(MSILDigiprodMaster.shop_id == shop_id) \
                                .order_by(desc(MSILDigiprodMaster.version)) \
                                .all()
    
    def update_master_status(self,shop_id,version,status,error=None,initiate_date=None,review_date=None):
        with self.session:
            result = self.session.query(MSILDigiprodMaster).filter(
                self.model_type.shop_id==shop_id,
                self.model_type.version==version
            ).first()

            if result:
                result.file_status=status
                result.error_messages=error
                if initiate_date:
                    result.review_initiated_date=initiate_date
                if review_date:
                    result.review_date=review_date
            self.commit()
    
    def get_master_shop_version(self,shop,version):
        with self.session:
            return self.session.query(MSILDigiprodMaster).filter(
                MSILDigiprodMaster.shop_id==shop,
                MSILDigiprodMaster.version==version
                ).first()