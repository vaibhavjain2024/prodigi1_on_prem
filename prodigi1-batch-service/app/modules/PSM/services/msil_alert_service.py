import datetime
from ..repositories.msil_alert_repository import MSILAlertRepository
from ..repositories.models.msil_alert_notification import AlertNotification
import pytz

ist_tz = pytz.timezone('Asia/Kolkata')

class MSILAlertService:
    def __init__(self, repository: MSILAlertRepository):
        self.repository = repository

    def get_alert_notifications(self, shop_id):
        notification_list = self.repository.get_alerts(shop_id)

        notifications = []
        for notification in notification_list:
            notification_obj = {
                "id" : notification.id,
                "notification" : notification.notification,
                "created_at" : notification.created_at,
                "alert_type" : notification.alert_type, 
                "metadata" : notification.notification_metadata,
            }
            notifications.append(notification_obj)
        
        return notifications

    


    def add_notification(self, notification, shop_id=None, alert_type=None, metadata=None, ):
        notification_obj = AlertNotification()
        notification_obj.notification = notification
        notification_obj.notification_metadata = metadata
        notification_obj.alert_type = alert_type
        notification_obj.created_at = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        notification_obj.shop_id = shop_id
        self.repository.add(notification_obj)

