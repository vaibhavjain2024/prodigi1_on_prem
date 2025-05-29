from sqlalchemy.orm import Session
from enum import Enum
from app.modules.digiprod.repositories.models.iot_sap_logs_production import (
    ProductionSAPLogs,
    ProductionSAPLogAttempt,
)


def serialize_production_log(log, attempts=[]):
    """Serialize ProductionSAPLogs with attached attempts."""
    data = {}
    for column in log.__table__.columns:
        val = getattr(log, column.name)
        data[column.name] = val.value if isinstance(val, Enum) else val

    data["attempts"] = [
        {
            attempt_col.name: getattr(attempt, attempt_col.name).value
            if isinstance(getattr(attempt, attempt_col.name), Enum)
            else getattr(attempt, attempt_col.name)
            for attempt_col in attempt.__table__.columns
        }
        for attempt in attempts
    ]
    return data


def apply_filters(query, filters):
    """Apply dynamic filters to ProductionSAPLogs query."""
    for field, value in filters.items():
        if value is None or value == "" or (isinstance(value, (list, dict, set)) and not value):
            continue

        column_attr = getattr(ProductionSAPLogs, field, None)
        if column_attr is not None:
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


def get_all_sap_production_logs(db: Session, start_time=None, end_time=None, **filters):
    """Get all production logs with attempts, based on filters."""
    query = db.query(ProductionSAPLogs)

    if start_time:
        query = query.filter(ProductionSAPLogs.data_capture_time >= start_time)
    if end_time:
        query = query.filter(ProductionSAPLogs.data_update_time <= end_time)

    query = apply_filters(query, filters)
    production_logs = query.all()

    # Get all relevant attempts
    log_ids = [log.id for log in production_logs]
    attempts = (
        db.query(ProductionSAPLogAttempt)
        .filter(ProductionSAPLogAttempt.log_id.in_(log_ids))
        .all()
    )

    # Map attempts to logs
    attempts_mapping = {}
    for attempt in attempts:
        attempts_mapping.setdefault(attempt.log_id, []).append(attempt)

    # Serialize each log with its attempts
    return {
        "production": [
            serialize_production_log(log, attempts_mapping.get(log.id, []))
            for log in production_logs
        ]
    }
