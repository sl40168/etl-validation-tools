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
