from sqlalchemy.orm import Session
from app.modules.digiprod.repositories.iot_sap_logs_plan_repository import get_all_sap_plan_logs


class IOTSapLogsPlanService:
    def __init__(self, db):
        self.db = db

    def fetch_all_sap_logs(self, schedule_start: str, schedule_finish: str, **query_params):
        """
        Fetch all SAP plan logs from the database.

        Args:
            schedule_start (str): The schedule start time 
            schedule_finish (str): The schedule end time 

        Returns:
            list: A list of SAP plan logs.
        """
        return get_all_sap_plan_logs(
            self.db,
            schedule_start=schedule_start,
            schedule_finish=schedule_finish,
            **query_params
        )
