# date_util.py
from datetime import datetime
import dateparser

def convert_to_sql_dates(start_text, end_text=None):
    """
    Convert fuzzy natural language dates to SQL-friendly format (YYYY-MM-DD HH:MM:SS).
    If end_text is not provided, defaults to the current datetime.
    """
    now = datetime.now()
    start = dateparser.parse(start_text)
    end = dateparser.parse(end_text) if end_text else now

    if not start:
        raise ValueError(f"Could not parse start_date: '{start_text}'")

    return (
        start.strftime("%Y-%m-%d %H:%M:%S"),
        end.strftime("%Y-%m-%d %H:%M:%S")
    )
