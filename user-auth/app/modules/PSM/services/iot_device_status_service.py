from sqlalchemy.orm import Session
from ..repositories.msil_iot_device_status_repository import IOTDeviceStatusRepository
from datetime import datetime

class IOTDeviceStatusService:
    def __init__(self, repository: IOTDeviceStatusRepository):
        self.repository = repository

    def create_or_update_device_status(self, client_id, event_type, timestamp, status):
        timestamp = datetime.fromtimestamp(timestamp / 1000) 
        existing_statuses = self.repository.get_device_status_by_client_id(client_id)
        if existing_statuses:
            # Update existing statuses
            updated_statuses = self.repository.update_device_status_by_client_id(client_id, event_type=event_type, timestamp=timestamp, status=status)
            return updated_statuses
        else:
            # Create new status
            new_status = self.repository.add_device_status(client_id, event_type, timestamp, status)
            return new_status

    def get_device_status_by_client_id(self, client_id):
        return self.repository.get_device_status_by_client_id(client_id)