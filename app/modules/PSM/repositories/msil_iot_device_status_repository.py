from sqlalchemy.orm import Session
from .repository import Repository
from .models.msil_iot_device_status import IOTDeviceStatus

class IOTDeviceStatusRepository:
    def __init__(self, session: Session):
        self.session = session
        self.model_type = IOTDeviceStatus

    def add_device_status(self, client_id, event_type, timestamp, status):
        new_status = IOTDeviceStatus(
            client_id=client_id,
            event_type=event_type,
            timestamp=timestamp,
            status=status
        )
        with self.session:
            self.session.add(new_status)
            self.session.commit()
        return new_status

    def get_device_status_by_id(self, status_id):
        with self.session:
            return self.session.query(self.model_type).filter(self.model_type.id == status_id).first()

    def get_device_status_by_client_id(self, client_id):
        with self.session:
            return self.session.query(self.model_type).filter(self.model_type.client_id == client_id).first()

    def get_all_device_statuses(self):
        with self.session:
            return self.session.query(self.model_type).all()

    def update_device_status(self, status_id, **kwargs):
        with self.session:
            status = self.get_device_status_by_id(status_id)
            if status:
                for key, value in kwargs.items():
                    setattr(status, key, value)
                self.session.commit()
        return status

    def update_device_status_by_client_id(self, client_id, **kwargs):
        obj = self.session.query(self.model_type).filter_by(client_id=client_id).first()
        with self.session:
            if obj:
                for key, value in kwargs.items():
                    setattr(obj, key, value)
                self.session.commit()
        return True
            

    def delete_device_status(self, status_id):
        with self.session:
            status = self.get_device_status_by_id(status_id)
            if status:
                self.session.delete(status)
                self.session.commit()
        return status