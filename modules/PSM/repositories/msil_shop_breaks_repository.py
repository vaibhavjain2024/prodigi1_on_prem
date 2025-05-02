from .repository import Repository
from .models.msil_shop_breaks import MSILShopBreaks
from sqlalchemy.orm import Session
from sqlalchemy import (
    and_,
    desc,
    func,
    case
)
import datetime

class MSILShopBreaksRepository(Repository):
    """
    MSILModelRepository to manage MSILModel data table.
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILShopBreaks
        self.current = datetime.date.today()
        self.next = self.current + datetime.timedelta(days=1)
    
    def update_breaks(self, breaks, shop_id):
        with self.session:
            self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id).delete()
            for item in breaks:
                start = datetime.datetime.strptime(str(item['start_time']).strip(),'%H:%M:%S').time()
                end = datetime.datetime.strptime(str(item['end_time']).strip(),'%H:%M:%S').time()
                start_dt = datetime.datetime.combine(self.current,start)
                if end < start :
                    end_dt = datetime.datetime.combine(self.next,end)
                else:
                    end_dt = datetime.datetime.combine(self.current,end)
                
                item['duration_minutes'] = int((end_dt-start_dt).total_seconds()/60)
            self.session.bulk_insert_mappings(mappings=breaks,mapper=self.model_type)
            self.session.commit()

    
