"""Integration tests for record matching flow with sorted records"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from src.db.query import execute_query
from src.validation.matcher import match_records_by_position, match_records_by_position_chunked


@pytest.fixture
def mock_sorted_left_data():
    """Create mock sorted data from left DolphinDB instance"""
    return pd.DataFrame({
        'business_date': ['2026.01.15'] * 5,
        'exch_product_id': ['CGB01', 'CGB01', 'CGB02', 'CGB03', 'CGB04'],
        'product_type': ['BOND'] * 5,
        'receive_time': pd.to_datetime([
            '2026-01-15 10:00:00',
            '2026-01-15 10:05:00',
            '2026-01-15 10:10:00',
            '2026-01-15 10:15:00',
            '2026-01-15 10:20:00'
        ]),
        'settle_speed': ['T+0', 'T+0', 'T+0', 'T+1', 'T+1'],
        'last_trade_price': [100.5, 101.0, 99.5, 102.0, 98.5],
        'last_trade_volume': [1000, 2000, 1500, 3000, 2500]
    })


@pytest.fixture
def mock_sorted_right_data():
    """Create mock sorted data from right DolphinDB instance"""
    return pd.DataFrame({
        'business_date': ['2026.01.15'] * 5,
        'exch_product_id': ['CGB01', 'CGB01', 'CGB02', 'CGB03', 'CGB04'],
        'product_type': ['BOND'] * 5,
        'receive_time': pd.to_datetime([
            '2026-01-15 10:00:00',
            '2026-01-15 10:05:00',
            '2026-01-15 10:10:00',
            '2026-01-15 10:15:00',
            '2026-01-15 10:20:00'
        ]),
        'settle_speed': ['T+0', 'T+0', 'T+0', 'T+1', 'T+1'],
        'last_trade_price': [100.5, 101.0, 99.5, 102.0, 98.5],
        'last_trade_volume': [1000, 2000, 1500, 3000, 2500]
    })


def test_sorted_records_matching(mock_sorted_left_data, mock_sorted_right_data):
    """Verify end-to-end flow with sorted records"""
    # Mock sessions
    mock_left_session = Mock(spec=object)
    mock_right_session = Mock(spec=object)

    mock_left_session.run.return_value = mock_sorted_left_data
    mock_right_session.run.return_value = mock_sorted_right_data

    # Execute queries
    left_df = execute_query(
        session=mock_left_session,
        database='market_data',
        table_name='market_price',
        business_date='2026.01.15',
        product_type='BOND'
    )

    right_df = execute_query(
        session=mock_right_session,
        database='market_data',
        table_name='market_price',
        business_date='2026.01.15',
        product_type='BOND'
    )

    # Verify queries have ORDER BY clause
    left_query = mock_left_session.run.call_args[0][0]
    right_query = mock_right_session.run.call_args[0][0]
    assert 'order by receive_time, exch_product_id, settle_speed' in left_query
    assert 'order by receive_time, exch_product_id, settle_speed' in right_query

    # Verify data is sorted
    assert (left_df['receive_time'].diff().dropna() >= pd.Timedelta(0)).all()
    assert (right_df['receive_time'].diff().dropna() >= pd.Timedelta(0)).all()

    # Match records by position
    matched, left_only, right_only = match_records_by_position(left_df, right_df)

    # Verify all records are matched (no unpaired)
    assert len(matched) == 5
    assert len(left_only) == 0
    assert len(right_only) == 0

    # Verify matched structure
    assert matched.shape[0] == 5
    # MultiIndex columns: ('left', col) and ('right', col)
    assert len(matched.columns) == len(left_df.columns) * 2


def test_bond_fut_time_filtering():
    """Verify BOND_FUT records outside trading hours are excluded"""
    # Mock session
    mock_session = Mock(spec=object)

    # Create mock data with records inside and outside trading hours
    # Trading hours: 09:30:00 - 15:00:00
    mock_bond_fut_data = pd.DataFrame({
        'business_date': ['2026.01.15'] * 3,
        'exch_product_id': ['TF01', 'TF02', 'TF03'],
        'product_type': ['BOND_FUT'] * 3,
        'receive_time': pd.to_datetime([
            '2026-01-15 10:00:00',  # Inside trading hours
            '2026-01-15 10:30:00',  # Inside trading hours
            '2026-01-15 16:00:00'   # Outside trading hours (should be excluded)
        ]),
        'settle_speed': ['T+0', 'T+0', 'T+1'],
        'last_trade_price': [100.5, 101.0, 102.0],
        'last_trade_volume': [1000, 2000, 3000]
    })

    # Only return filtered data (records within trading hours)
    # This simulates the database filtering out the 16:00:00 record
    filtered_data = mock_bond_fut_data[
        (mock_bond_fut_data['receive_time'].dt.hour >= 9) &
        (mock_bond_fut_data['receive_time'].dt.hour < 15) |
        ((mock_bond_fut_data['receive_time'].dt.hour == 15) &
         (mock_bond_fut_data['receive_time'].dt.minute == 0) &
         (mock_bond_fut_data['receive_time'].dt.second == 0))
    ]
    mock_session.run.return_value = filtered_data

    # Execute query for BOND_FUT
    result_df = execute_query(
        session=mock_session,
        database='market_data',
        table_name='market_price',
        business_date='2026.01.15',
        product_type='BOND_FUT'
    )

    # Verify time filter is in query
    call_args = mock_session.run.call_args[0][0]
    assert "receive_time > datetime('2026.01.15 09:30:00')" in call_args
    assert "receive_time < datetime('2026.01.15 15:00:00')" in call_args

    # Verify only records within trading hours are returned
    # The 16:00:00 record should be filtered out by the database
    assert len(result_df) == 2
    assert all(result_df['receive_time'].dt.hour < 15)

    print("BOND_FUT time filtering test passed:")
    print(f"  - Query contains time range filter")
    print(f"  - Only {len(result_df)} records returned (within 09:30-15:00)")
    print(f"  - Records outside trading hours excluded")


def test_full_position_matching_flow():
    """Verify end-to-end position-based matching flow"""
    # Mock sessions
    mock_left_session = Mock(spec=object)
    mock_right_session = Mock(spec=object)

    # Create mock sorted data
    mock_data = pd.DataFrame({
        'business_date': ['2026.01.15'] * 5,
        'exch_product_id': ['CGB01', 'CGB02', 'CGB03', 'CGB04', 'CGB05'],
        'product_type': ['BOND'] * 5,
        'receive_time': pd.to_datetime([
            '2026-01-15 10:00:00',
            '2026-01-15 10:05:00',
            '2026-01-15 10:10:00',
            '2026-01-15 10:15:00',
            '2026-01-15 10:20:00'
        ]),
        'settle_speed': ['T+0', 'T+0', 'T+0', 'T+1', 'T+1'],
        'last_trade_price': [100.5, 101.0, 99.5, 102.0, 98.5],
        'last_trade_volume': [1000, 2000, 1500, 3000, 2500]
    })

    mock_left_session.run.return_value = mock_data.copy()
    mock_right_session.run.return_value = mock_data.copy()

    # Execute queries
    left_df = execute_query(
        session=mock_left_session,
        database='market_data',
        table_name='market_price',
        business_date='2026.01.15',
        product_type='BOND'
    )

    right_df = execute_query(
        session=mock_right_session,
        database='market_data',
        table_name='market_price',
        business_date='2026.01.15',
        product_type='BOND'
    )

    # Verify ORDER BY is in queries
    left_query = mock_left_session.run.call_args[0][0]
    right_query = mock_right_session.run.call_args[0][0]
    assert 'order by receive_time, exch_product_id, settle_speed' in left_query
    assert 'order by receive_time, exch_product_id, settle_speed' in right_query

    # Match records by position
    matched, left_only, right_only = match_records_by_position(left_df, right_df)

    # Verify all records are matched
    assert len(matched) == 5
    assert len(left_only) == 0
    assert len(right_only) == 0

    # Verify position matching (record i in left matches record i in right)
    for i in range(len(matched)):
        left_price = matched[('left', 'last_trade_price')].iloc[i]
        right_price = matched[('right', 'last_trade_price')].iloc[i]
        assert left_price == right_price, f"Position {i}: {left_price} != {right_price}"

    print("Full position-based matching flow test passed:")
    print(f"  - Queries have ORDER BY clause")
    print(f"  - {len(matched)} records matched by position")
    print(f"  - No unpaired records")
    print(f"  - Position N in left matches position N in right")


def test_position_matching_with_unpaired_records():
    """Verify position-based matching with unequal dataset sizes"""
    # Mock sessions
    mock_left_session = Mock(spec=object)
    mock_right_session = Mock(spec=object)

    # Left has 3 records, right has 2 records
    left_data = pd.DataFrame({
        'business_date': ['2026.01.15'] * 3,
        'exch_product_id': ['CGB01', 'CGB02', 'CGB03'],
        'product_type': ['BOND'] * 3,
        'receive_time': pd.to_datetime(['2026-01-15 10:00:00', '2026-01-15 10:05:00', '2026-01-15 10:10:00']),
        'settle_speed': ['T+0', 'T+0', 'T+1'],
        'last_trade_price': [100.5, 101.0, 102.0],
        'last_trade_volume': [1000, 2000, 3000]
    })

    right_data = pd.DataFrame({
        'business_date': ['2026.01.15'] * 2,
        'exch_product_id': ['CGB01', 'CGB02'],
        'product_type': ['BOND'] * 2,
        'receive_time': pd.to_datetime(['2026-01-15 10:00:00', '2026-01-15 10:05:00']),
        'settle_speed': ['T+0', 'T+0'],
        'last_trade_price': [100.5, 101.0],
        'last_trade_volume': [1000, 2000]
    })

    mock_left_session.run.return_value = left_data
    mock_right_session.run.return_value = right_data

    # Execute queries
    left_df = execute_query(
        session=mock_left_session,
        database='market_data',
        table_name='market_price',
        business_date='2026.01.15',
        product_type='BOND'
    )

    right_df = execute_query(
        session=mock_right_session,
        database='market_data',
        table_name='market_price',
        business_date='2026.01.15',
        product_type='BOND'
    )

    # Match records by position
    matched, left_only, right_only = match_records_by_position(left_df, right_df)

    # Verify matching results
    assert len(matched) == 2, f"Expected 2 matched pairs, got {len(matched)}"
    assert len(left_only) == 1, f"Expected 1 left-only record, got {len(left_only)}"
    assert len(right_only) == 0, f"Expected 0 right-only records, got {len(right_only)}"

    # Verify unpaired record is the last one
    assert left_only['exch_product_id'].values[0] == 'CGB03'

    print("Position matching with unpaired records test passed:")
    print(f"  - {len(matched)} records matched by position")
    print(f"  - {len(left_only)} unpaired left record(s)")
    print(f"  - {len(right_only)} unpaired right record(s)")
