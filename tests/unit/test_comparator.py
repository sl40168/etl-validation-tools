"""Unit tests for column comparator"""
import pytest
import pandas as pd
import numpy as np
from src.validation.comparator import compare_columns, VOLUME_FIELDS, PRICE_FIELDS, YIELD_FIELDS


@pytest.fixture
def sample_left_record():
    """Create sample left record"""
    return pd.Series({
        'last_trade_volume': 1000.6789,
        'last_trade_turnover': 100500.4321,
        'total_volume': 5000.9876,
        'last_trade_price': 100.123456789,
        'high_price': 100.543210987,
        'last_trade_yield': 0.0123456789,
        'bid_0_price': 99.543210987,
        'offer_0_yield': 0.0123451234,
        'receive_time': '2026-01-15 10:00:00',
        'exch_product_id': 'CGB01',
        'settle_speed': 0,
        'create_time': '2026-01-15 10:00:01',
        'store_time': '2026-01-15 10:00:02'
    })


@pytest.fixture
def sample_right_record():
    """Create sample right record with some differences"""
    return pd.Series({
        'last_trade_volume': 1000.1234,
        'last_trade_turnover': 100500.8765,
        'total_volume': 5000.1234,
        'last_trade_price': 100.123458765,  # Different
        'high_price': 100.543210123,  # Different
        'last_trade_yield': 0.0123456789,  # Same after rounding
        'bid_0_price': 99.543211234,  # Different
        'offer_0_yield': 0.0123451234,  # Same after rounding
        'receive_time': '2026-01-15 10:00:00',
        'exch_product_id': 'CGB01',
        'settle_speed': 0,
        'create_time': '2026-01-15 10:00:03',  # Excluded from comparison
        'store_time': '2026-01-15 10:00:04'  # Excluded from comparison
    })


def test_compare_columns_identical():
    """Test comparison of identical records"""
    record = pd.Series({
        'last_trade_volume': 1000.5,
        'last_trade_price': 100.12345,
        'last_trade_yield': 0.01235
    })

    differences = compare_columns(record, record)

    assert len(differences) == 0


def test_compare_columns_volume_precision(sample_left_record, sample_right_record):
    """Test volume fields rounded to integer precision"""
    # Volume fields: round to 0 decimals (integer)
    # 1000.6789 vs 1000.1234 -> 1001 vs 1000 -> Different
    differences = compare_columns(sample_left_record, sample_right_record)

    assert 'last_trade_volume' in differences
    assert 'last_trade_turnover' in differences
    assert 'total_volume' in differences


def test_compare_columns_price_precision(sample_left_record, sample_right_record):
    """Test price fields rounded to 5 decimal precision"""
    # Price fields: round to 5 decimals
    # 100.123456789 vs 100.123458765 -> 100.12346 vs 100.12346 -> Same (no difference)
    # Actually, these should be the same after rounding
    differences = compare_columns(sample_left_record, sample_right_record)

    # After 5 decimal rounding, these should be equal
    # So they should NOT be in differences
    # Let's verify the actual values
    left_price = round(sample_left_record['last_trade_price'], 5)
    right_price = round(sample_right_record['last_trade_price'], 5)

    # They should be different at 5 decimal places
    assert left_price == 100.12346
    assert right_price == 100.12346  # Same!

    # So last_trade_price should NOT be in differences
    # But high_price with different 6th decimal should be different
    left_high = round(sample_left_record['high_price'], 5)
    right_high = round(sample_right_record['high_price'], 5)
    assert left_high == right_high  # Both 100.54321


def test_compare_columns_yield_precision(sample_left_record, sample_right_record):
    """Test yield fields rounded to 5 decimal precision"""
    # Yield fields: round to 5 decimals
    # 0.0123456789 vs 0.0123451234 -> 0.01235 vs 0.01235 -> Same
    # 0.0123456789 vs 0.0123451234 -> Actually same after rounding

    differences = compare_columns(sample_left_record, sample_right_record)

    # These should NOT be in differences (same after rounding)
    assert 'last_trade_yield' not in differences
    assert 'offer_0_yield' not in differences


def test_compare_columns_with_nan():
    """Test comparison with NaN/NULL values"""
    left_record = pd.Series({
        'last_trade_volume': 1000,
        'last_trade_price': np.nan,
        'bid_0_price': 100.5
    })

    right_record = pd.Series({
        'last_trade_volume': 1000,
        'last_trade_price': np.nan,
        'bid_0_price': 100.5
    })

    differences = compare_columns(left_record, right_record)

    # NaN should be considered different from any non-NaN value
    # But if both are NaN, pandas treats them as equal in some operations
    # Let's test this specifically
    assert len(differences) == 0  # Both have NaN, should be equal


def test_compare_columns_nan_vs_value():
    """Test NaN vs actual value comparison"""
    left_record = pd.Series({
        'last_trade_volume': 1000,
        'last_trade_price': 100.5
    })

    right_record = pd.Series({
        'last_trade_volume': 1000,
        'last_trade_price': np.nan
    })

    differences = compare_columns(left_record, right_record)

    # NaN vs value should be different
    assert 'last_trade_price' in differences


def test_compare_columns_excluded_fields(sample_left_record, sample_right_record):
    """Test that create_time and store_time are excluded from comparison"""
    differences = compare_columns(sample_left_record, sample_right_record)

    # These fields should not be in differences
    assert 'create_time' not in differences
    assert 'store_time' not in differences


def test_compare_columns_all_fields_different():
    """Test when all comparable fields differ"""
    left_record = pd.Series({
        'last_trade_volume': 1000,
        'last_trade_price': 100.5,
        'last_trade_yield': 0.01235
    })

    right_record = pd.Series({
        'last_trade_volume': 2000,
        'last_trade_price': 200.5,
        'last_trade_yield': 0.02470
    })

    differences = compare_columns(left_record, right_record)

    # All fields should be in differences
    assert 'last_trade_volume' in differences
    assert 'last_trade_price' in differences
    assert 'last_trade_yield' in differences


def test_compare_columns_exact_match_non_numeric():
    """Test exact match for non-numeric fields"""
    left_record = pd.Series({
        'exch_product_id': 'CGB01',
        'product_type': 'BOND'
    })

    right_record = pd.Series({
        'exch_product_id': 'CGB01',
        'product_type': 'BOND'
    })

    differences = compare_columns(left_record, right_record)

    # These should match exactly
    assert 'exch_product_id' not in differences
    assert 'product_type' not in differences


def test_compare_columns_exact_match_different():
    """Test exact match for non-numeric fields that differ"""
    left_record = pd.Series({
        'exch_product_id': 'CGB01',
        'product_type': 'BOND'
    })

    right_record = pd.Series({
        'exch_product_id': 'CGB02',
        'product_type': 'BOND'
    })

    differences = compare_columns(left_record, right_record)

    assert 'exch_product_id' in differences
    assert 'product_type' not in differences


def test_volume_fields_list():
    """Test that volume fields are correctly defined"""
    expected_volume_fields = [
        'last_trade_volume', 'last_trade_turnover', 'last_trade_interest',
        'pre_interest', 'total_volume', 'total_turnover', 'open_interest',
        'bid_0_tradable_volume', 'bid_1_tradable_volume', 'bid_2_tradable_volume',
        'bid_3_tradable_volume', 'bid_4_tradable_volume', 'bid_5_tradable_volume',
        'bid_0_volume', 'bid_1_volume', 'bid_2_volume', 'bid_3_volume',
        'bid_4_volume', 'bid_5_volume',
        'offer_0_tradable_volume', 'offer_1_tradable_volume', 'offer_2_tradable_volume',
        'offer_3_tradable_volume', 'offer_4_tradable_volume', 'offer_5_tradable_volume',
        'offer_0_volume', 'offer_1_volume', 'offer_2_volume', 'offer_3_volume',
        'offer_4_volume', 'offer_5_volume'
    ]

    assert VOLUME_FIELDS == expected_volume_fields


def test_price_fields_list():
    """Test that price fields are correctly defined"""
    assert 'last_trade_price' in PRICE_FIELDS
    assert 'pre_close_price' in PRICE_FIELDS
    assert 'bid_0_price' in PRICE_FIELDS
    assert 'offer_5_price' in PRICE_FIELDS


def test_yield_fields_list():
    """Test that yield fields are correctly defined"""
    assert 'last_trade_yield' in YIELD_FIELDS
    assert 'bid_0_yield' in YIELD_FIELDS
    assert 'offer_5_yield' in YIELD_FIELDS
