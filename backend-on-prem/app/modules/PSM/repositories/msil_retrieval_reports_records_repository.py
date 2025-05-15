from .repository import Repository
from .models.msil_retrieval_reports_records import MSILRetrievalReportsRecords
from sqlalchemy.orm import Session


class MSILRetrievalReportsRecordsRepository(Repository):
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILRetrievalReportsRecords

    def get_report_record(self, report_id):
        with self.session:
            return (
                self.session.query(
                    self.model_type
                )
                .filter(
                    self.model_type.id == report_id
                )
                .first()
            )

    def add_or_update_reports(self,
                              report_id=None,
                              module=None,
                              table = None,
                              description=None,
                              download_url=None,
                              start_date = None,
                              end_date = None,
                              status=None):
        if report_id:
            with self.session:
                result = (
                    self.session.query(
                        self.model_type
                    )
                    .filter(
                        self.model_type.id == report_id
                    )
                    .first()
                )
                if result:
                    update_dict = dict()
                    if module:
                        update_dict["module"] = module
                    if table:
                        update_dict["table"] = table
                    if description:
                        update_dict["description"] = description
                    if download_url:
                        update_dict["download_url"] = download_url
                    if start_date:
                        update_dict["start_date"] = start_date
                    if end_date:
                        update_dict["end_date"] = end_date
                    if status:
                        update_dict["status"] = status
                    self.update(id=report_id, model=update_dict)
                    self.commit()
                    return True
                else:
                    return False
        else:
            reports_record = MSILRetrievalReportsRecords()
            if module:
                reports_record.module = module
            if table:
                reports_record.table = table
            if description:
                reports_record.description = description
            if download_url:
                reports_record.download_url = download_url
            if start_date:
                reports_record.start_date = start_date
            if end_date:
                reports_record.end_date = end_date
            if status:
                reports_record.status = status

            model = self.add(reports_record)
            return model
