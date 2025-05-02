from modules.PSM.repositories.models.msil_alert_notification import AlertNotification
from modules.PSM.repositories.repository import Repository
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import datetime
import pytz

ist_tz = pytz.timezone('Asia/Kolkata')

class MSILAlertRepository(Repository):
    """Component Measurement Repository to manage Component Dimension Measurement table

    Args:
        Repository (class): Base repository
    """

    def __init__(self, session: Session):
        self.session = session
        self.model_type = AlertNotification


    def get_alerts(self, shop_id, limit=1000):
        with self.session:
            
            current_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None)
            datetime_filter = None
            current_date = current_datetime.date()
            prev_date = current_datetime - datetime.timedelta(days=1)
            if  (current_datetime.hour >= 6): 
                datetime_filter = datetime.datetime.combine(current_date,datetime.time(6,0,0))
            else:
                datetime_filter = datetime.datetime.combine(prev_date,datetime.time(6,0,0))
            query = self.session.query(AlertNotification)
            query = query \
                        .filter(AlertNotification.created_at > datetime_filter) \
                        .filter(AlertNotification.shop_id == shop_id) 

            return query.order_by(AlertNotification.created_at.desc()).limit(limit).all()

