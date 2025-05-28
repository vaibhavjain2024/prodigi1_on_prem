from sqlalchemy.orm import Session
from app.modules.digiprod.repositories.models.iot_sap_logs_downtime import DowntimeSAPLogs
from enum import Enum


def serialize_downtime_log(obj):
    """Serialize DowntimeSAPLogs object to dict, handling Enums."""
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
        column_attr = getattr(DowntimeSAPLogs, field, None)
        if column_attr is not None:
            # Support comma-separated values
            if isinstance(value, str) and "," in value:
                values_list = [v.strip()
                               for v in value.split(",") if v.strip()]
                query = query.filter(column_attr.in_(values_list))
            elif isinstance(value, list):
                query = query.filter(column_attr.in_(value))
            elif isinstance(value, Enum):
                query = query.filter(column_attr == value.value)
            else:
                query = query.filter(column_attr == value)

    return query


def get_all_sap_downtime_logs(db: Session, start_time=None, end_time=None, **filters):
    """Fetch filtered SAP downtime logs from the database."""

    query = db.query(DowntimeSAPLogs)

    if start_time:
        query = query.filter(DowntimeSAPLogs.start_time >= start_time)
    if end_time:
        query = query.filter(DowntimeSAPLogs.end_time <= end_time)

    query = apply_filters(query, filters)

    downtime_logs = query.all()

    return {"downtime": [serialize_downtime_log(row) for row in downtime_logs]}
