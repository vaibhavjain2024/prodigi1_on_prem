from sqlalchemy.orm import Session
from app.modules.digiprod.repositories.iot_sap_logs_production_repository import get_all_sap_production_logs


class IOTSapLogsProductionService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_all_sap_logs_production(self, start_time: str, end_time: str, **query_params):
        """
        Fetch all SAP production logs from the database.

        """
        return get_all_sap_production_logs(
            self.db,
            start_time=start_time,
            end_time=end_time,
            **query_params
        )
