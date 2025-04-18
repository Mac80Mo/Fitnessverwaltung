from datetime import datetime, date
import pytz

germany_tz = pytz.timezone('Europe/Berlin')

def format_date_local(dt):
    # Falls nur ein reines Datum (z. B. aus .date()) → zu datetime machen
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.min.time())

    return dt.astimezone(germany_tz).strftime('%d.%m.%Y')

def sort_date_labels(date_str_list):
    return sorted(date_str_list, key=lambda d: datetime.strptime(d, '%d.%m.%Y'))