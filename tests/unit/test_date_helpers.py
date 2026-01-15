"""Unit tests for date helpers"""
import pytest
from src.utils.date_helpers import parse_date, format_date_for_sql, parse_and_format_date
from datetime import datetime


def test_parse_valid_date():
    """Test parsing a valid date in YYYYMMDD format"""
    result = parse_date("20260115")
    expected = datetime(2026, 1, 15)
    assert result == expected


def test_parse_invalid_format():
    """Test error when date format is invalid"""
    with pytest.raises(ValueError, match="Invalid date format"):
        parse_date("2026-01-15")


def test_parse_invalid_length():
    """Test error when date has wrong length"""
    with pytest.raises(ValueError, match="Invalid date format"):
        parse_date("2026015")


def test_parse_non_numeric():
    """Test error when date contains non-numeric characters"""
    with pytest.raises(ValueError, match="Date must be numeric only"):
        parse_date("20260ab5")


def test_parse_nonexistent_date():
    """Test error when date does not exist (e.g., February 30)"""
    with pytest.raises(ValueError, match="Invalid date"):
        parse_date("20260230")


def test_parse_invalid_month():
    """Test error when month is invalid (13)"""
    with pytest.raises(ValueError, match="Invalid date"):
        parse_date("20261301")


def test_parse_invalid_day():
    """Test error when day is invalid (32)"""
    with pytest.raises(ValueError, match="Invalid date"):
        parse_date("20260132")


def test_format_date_for_sql():
    """Test formatting date for SQL queries"""
    date_obj = datetime(2026, 1, 15)
    result = format_date_for_sql(date_obj)
    assert result == "2026.01.15"


def test_parse_and_format_date():
    """Test parsing and formatting date in one step"""
    result = parse_and_format_date("20260115")
    assert result == "2026.01.15"


def test_parse_leap_year():
    """Test parsing a valid leap year date"""
    result = parse_date("20240229")
    expected = datetime(2024, 2, 29)
    assert result == expected


def test_parse_non_leap_year():
    """Test error for invalid leap year date"""
    with pytest.raises(ValueError, match="Invalid date"):
        parse_date("20230229")
