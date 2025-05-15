from datetime import timedelta
from .repository import Repository
from .models.msil_line import MSILLine
from sqlalchemy.orm import Session

class MSILLineRepository(Repository):
    """MSILLineRepository to manage MSILLine data table.
    
    Args:
        Repository (class): Base repository
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILLine

    def line_ids(self,shop_id):
        line_dict = {}
        with self.session:
            lines = self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id).all()
            for line in lines:
                line_dict[line.name]=line.id
            return line_dict
    
    def check_and_add_lines(self,line_list,shop_id):
        with self.session:
            lines = self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id).all()
            existing = set([line.name for line in lines])
            new = line_list - existing
            if new:
                for item in new:
                    new_line=MSILLine()
                    new_line.name=item
                    new_line.shop_id=shop_id
                    self.add(new_line)
                return True
            return False

