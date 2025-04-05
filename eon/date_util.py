import re
from datetime import datetime, timedelta
import dateparser

def convert_to_sql_dates(start_text, end_text=None):
    now = datetime.now()

    # --- Handle custom relative expressions like "last 5 hours", "last 3 days"
    match = re.match(r"last\s+(\d+)\s+(hours?|days?|minutes?)", start_text.lower())
    if match:
        value, unit = match.groups()
        value = int(value)

        if "hour" in unit:
            start = now - timedelta(hours=value)
        elif "minute" in unit:
            start = now - timedelta(minutes=value)
        elif "day" in unit:
            start = now - timedelta(days=value)
        else:
            raise ValueError(f"Unsupported unit in start_date: {unit}")
        end = now

    else:
        # Fall back to dateparser
        settings = {
            'PREFER_DATES_FROM': 'past',
            'RELATIVE_BASE': now
        }

        start = dateparser.parse(start_text, settings=settings)
        end = dateparser.parse(end_text, settings=settings) if end_text else now

        if not start:
            raise ValueError(f"Could not parse start_date: '{start_text}'")

    return (
        start.strftime("%Y-%m-%d %H:%M:%S"),
        end.strftime("%Y-%m-%d %H:%M:%S")
    )
