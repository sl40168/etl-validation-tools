"""Date parsing and formatting utilities"""
from datetime import datetime
from typing import Optional


def parse_date(date_str: str) -> datetime:
    """
    Parse date string in YYYYMMDD format to datetime object

    Args:
        date_str: Date string in YYYYMMDD format (e.g., "20260115")

    Returns:
        datetime object representing the date

    Raises:
        ValueError: If date format is invalid or date does not exist
    """
    if not date_str or len(date_str) != 8:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYYMMDD (e.g., 20260115)")

    if not date_str.isdigit():
        raise ValueError(f"Invalid date format: {date_str}. Date must be numeric only")

    try:
        return datetime.strptime(date_str, "%Y%m%d")
    except ValueError as e:
        raise ValueError(f"Invalid date: {date_str}. {e}")


def format_date_for_sql(date_obj: datetime) -> str:
    """
    Format datetime object to YYYY.MM.DD format for SQL queries

    Args:
        date_obj: datetime object

    Returns:
        Date string in YYYY.MM.DD format (e.g., "2026.01.15")
    """
    return date_obj.strftime("%Y.%m.%d")


def parse_and_format_date(date_str: str) -> str:
    """
    Parse date string in YYYYMMDD format and format as YYYY.MM.DD for SQL

    Args:
        date_str: Date string in YYYYMMDD format (e.g., "20260115")

    Returns:
        Date string in YYYY.MM.DD format (e.g., "2026.01.15")

    Raises:
        ValueError: If date format is invalid or date does not exist
    """
    date_obj = parse_date(date_str)
    return format_date_for_sql(date_obj)


def construct_time_range(
    business_date: str,
    start_time: str = "09:30:00",
    end_time: str = "15:00:00"
) -> tuple[str, str]:
    """
    Construct datetime strings for time range filtering in SQL queries

    Args:
        business_date: Date in YYYY.MM.DD format
        start_time: Start time in HH:MM:SS format (default: "09:30:00")
        end_time: End time in HH:MM:SS format (default: "15:00:00")

    Returns:
        Tuple of (start_datetime, end_datetime) strings ready for SQL queries
        Format: ("datetime('YYYY.MM.DD HH:MM:SS')", "datetime('YYYY.MM.DD HH:MM:SS')")

    Raises:
        ValueError: If date/time format is invalid
    """
    # Validate business_date format
    if not business_date:
        raise ValueError("business_date cannot be empty")

    try:
        # Just validate format, not actual date value
        datetime.strptime(business_date, "%Y.%m.%d")
    except ValueError:
        raise ValueError(f"Invalid business_date format: {business_date}. Expected YYYY.MM.DD format")

    # Validate time format
    for time_val, name in [(start_time, "start_time"), (end_time, "end_time")]:
        try:
            datetime.strptime(time_val, "%H:%M:%S")
        except ValueError:
            raise ValueError(f"Invalid {name} format: {time_val}. Expected HH:MM:SS format")

    # Construct datetime strings for SQL
    start_dt = f"datetime('{business_date} {start_time}')"
    end_dt = f"datetime('{business_date} {end_time}')"

    return start_dt, end_dt
