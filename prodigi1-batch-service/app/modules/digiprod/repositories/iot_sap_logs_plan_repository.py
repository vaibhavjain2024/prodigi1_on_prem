from sqlalchemy.orm import Session
from enum import Enum
from app.modules.digiprod.repositories.models.iot_sap_logs_plan import PlanSAPLogs


def serialize_plan_log(obj):
    """Serialize PlanSAPLogs object to dict, handling Enums."""
    data = {}
    for column in obj.__table__.columns:
        val = getattr(obj, column.name)
        data[column.name] = val.value if isinstance(val, Enum) else val
    return data


def apply_filters(query, filters):
    """Apply dynamic filters to the query."""
    for field, value in filters.items():
        # Skip empty values or unset enum for 'data_sent_flag'
        if value is None or value == "" or (isinstance(value, (list, dict, set)) and not value):
            continue
        if field == "data_sent_flag" and not value:
            continue
        column_attr = getattr(PlanSAPLogs, field, None)
        if column_attr is not None:
            if isinstance(value, Enum):
                query = query.filter(column_attr == value.value)
            else:
                query = query.filter(column_attr == value)
    return query


def get_all_sap_plan_logs(db: Session, schedule_start=None, schedule_finish=None, **filters):
    """Fetch filtered SAP plan logs from the database."""

    query = db.query(PlanSAPLogs)

    if schedule_start:
        query = query.filter(PlanSAPLogs.schedule_start >= schedule_start)
    if schedule_finish:
        query = query.filter(PlanSAPLogs.schedule_finish <= schedule_finish)

    query = apply_filters(query, filters)

    plan_logs = query.all()

    return {"plan": [serialize_plan_log(row) for row in plan_logs]}
