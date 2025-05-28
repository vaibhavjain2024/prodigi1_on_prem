from sqlalchemy.orm import Session
from app.modules.digiprod.repositories.iot_sap_logs_downtime_repository import get_all_sap_downtime_logs


class IOTSapLogsDowntimeService:
    def __init__(self, db):
        self.db = db

    def fetch_all_sap_logs(self, start_time: str, end_time: str, **query_params):
        """
        Fetch all SAP downtime logs from the database.

        Args:
            start_time (str): The start time for filtering logs.
            end_time (str): The end time for filtering logs.

        Returns:
            list: A list of SAP downtime logs.
        """
        return get_all_sap_downtime_logs(
            self.db,
            start_time=start_time,
            end_time=end_time,
            **query_params
        )

# def fetch_all_sap_logs(db: Session):
#     return get_all_sap_downtime_logs(db)
