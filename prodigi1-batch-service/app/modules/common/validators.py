from datetime import datetime

def validate_date_time_format(date_time, format='%Y-%m-%d %H:%M:%S'):
    try:
        if date_time is not None:
            datetime.strptime(date_time, format)
        return True
    except ValueError:
        return False
