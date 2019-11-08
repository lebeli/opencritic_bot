from datetime import datetime
from datetime import timezone


MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Oct', 'Sep', 'Nov', 'Dec']


def utc_time_now():
    return datetime.now(tz=timezone.utc)


def get_date_str(dt):
    return "^^{} ^^{}, ^^{}".format(MONTHS[dt.month - 1], dt.day, dt.year)
