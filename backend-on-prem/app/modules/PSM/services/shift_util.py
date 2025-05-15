import datetime
import pytz
from datetime import datetime as dt
ist_tz = pytz.timezone('Asia/Kolkata')

SHIFT_MAPPING_WITH_TIME = {
        (datetime.time(6, 30, 0), datetime.time(15, 14, 59)) : "A",
        (datetime.time(15, 15, 0), datetime.time(23, 59, 59)) : "B",
        (datetime.time(0, 0, 0), datetime.time(6, 29, 59)) : "C"
    }

def get_shift(time):
    shift = None
    for each_shift in SHIFT_MAPPING_WITH_TIME:
        if each_shift[0] <= time <= each_shift[1]:
            shift = SHIFT_MAPPING_WITH_TIME.get(each_shift)
    return shift

def get_shift_with_start_end(time):
    shift = None
    start_time = None
    end_time = None
    for each_shift in SHIFT_MAPPING_WITH_TIME:
        if each_shift[0] <= time <= each_shift[1]:
            shift = SHIFT_MAPPING_WITH_TIME.get(each_shift)
            start_time = each_shift[0]
            end_time = each_shift[1]
    return shift,start_time,end_time

def get_production_date(shift):
    utc_now = dt.utcnow()

    # Convert to IST (Indian Standard Time)
    ist_timezone = pytz.timezone('Asia/Kolkata')
    ist_now = utc_now.astimezone(ist_timezone)
    if shift != "C":
        print((ist_now  - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
        return datetime.datetime.today().strftime('%Y-%m-%d')
    return (ist_now  - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

def get_day_start(shop_id, date):
    ist_tz = pytz.timezone('Asia/Kolkata')
    for shift_time_range, shift in SHIFT_MAPPING_WITH_TIME.items():
        if shift == "A":
            start = shift_time_range[0]
            return ist_tz.localize(datetime.datetime.combine(date,start))
            

def get_day_end(shop_id, date):
    ist_tz = pytz.timezone('Asia/Kolkata')
    date = date + datetime.timedelta(days=1)
    for shift_time_range, shift in SHIFT_MAPPING_WITH_TIME.items():
        if shift == "C":
            end = shift_time_range[1]
            return ist_tz.localize(datetime.datetime.combine(date,end))
