from datetime import timedelta
from .repository import Repository
from .models.msil_variant import MSILVariant
from sqlalchemy.orm import Session

class MSILVariantRepository(Repository):
    """MSILLineRepository to manage MSILLine data table.
    
    Args:
        Repository (class): Base repository
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILVariant
    
    def variant_ids(self):
        variant_dict = {}
        with self.session:
            variants = self.session.query(MSILVariant).all()
            for variant in variants:
                variant_dict[variant.variant_name]=variant.id
            return variant_dict
        
    def check_for_variants(self,variant_names):
        with self.session:
            result_dict = {}
            results = self.session.query(self.model_type.variant_name,self.model_type.id).where(self.model_type.variant_name.in_(variant_names)).distinct().all()
            for item in results:
                result_dict[item[0]]=item[1]
            return result_dict
    


