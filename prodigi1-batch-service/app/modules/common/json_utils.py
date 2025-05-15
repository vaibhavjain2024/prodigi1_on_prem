import datetime

def default_format_for_json(obj):
    """Handler for dict data helps to serialize it to Json.

    This method is used to cast the dict values to isoformat if the type of value is date/datetime.

    Args:
        obj (any): values of dict.

    Returns:
        None/datetime: if obj is data/datetime then date/datetime in isoformat otherwise None.
    """    
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()