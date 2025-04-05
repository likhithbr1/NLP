# date_util.py
from datetime import datetime
import dateparser

def convert_to_sql_dates(start_text, end_text=None):
    now = datetime.now()

    settings = {
        'PREFER_DATES_FROM': 'past',
        'RELATIVE_BASE': now,
    }

    start = dateparser.parse(start_text, settings=settings)
    end = dateparser.parse(end_text, settings=settings) if end_text else now

    if not start:
        raise ValueError(f"Could not parse start_date: '{start_text}'")

    return (
        start.strftime("%Y-%m-%d %H:%M:%S"),
        end.strftime("%Y-%m-%d %H:%M:%S")
    )
