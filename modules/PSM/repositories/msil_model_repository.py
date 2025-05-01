from .repository import Repository
from .models.msil_model import MSILModel
from sqlalchemy.orm import Session
from sqlalchemy import (
    and_,
    desc,
    func,
    case
)

class MSILModelRepository(Repository):
    """
    MSILModelRepository to manage MSILModel data table.
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILModel
    
    def model_ids(self,shop_id):
        model_dict = {}
        with self.session:
            models = self.session.query(MSILModel).filter(MSILModel.shop_id==shop_id).all()
            for model in models:
                model_dict[model.model_name]=model.id
            return model_dict
    
    def update_model(self, id, model, description):
        with self.session:
            model_obj = self.session.query(MSILModel).filter(MSILModel.id==id).first()
            model_obj.model_name = model
            model_obj.model_description = description
            self.commit()
    
    def check_for_models(self,model_names,shop_id):
        with self.session:
            result_dict={}
            results = self.session.query(self.model_type.model_name,self.model_type.id).filter(self.model_type.shop_id==shop_id).where(self.model_type.model_name.in_(model_names)).distinct().all()
            for item in results:
                result_dict[item[0]]=item[1]
            return result_dict