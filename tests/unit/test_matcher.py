"""Unit tests for record matcher"""
import pytest
import pandas as pd
import time
from unittest.mock import patch
from src.validation.matcher import match_records, match_records_by_position, MATCHING_KEYS_BOND, CHUNK_SIZE


@pytest.fixture
def sample_left_df():
    """Create sample left DataFrame"""
    return pd.DataFrame({
        'receive_time': ['2026-01-15 10:00:00', '2026-01-15 10:00:01', '2026-01-15 10:00:02', '2026-01-15 10:00:03'],
        'exch_product_id': ['CGB01', 'CGB02', 'CGB03', 'CGB04'],
        'settle_speed': [0, 0, 1, 0],
        'business_date': ['2026.01.15'] * 4,
        'product_type': ['BOND'] * 4,
        'last_trade_price': [100.5, 101.0, 102.0, 103.5]
    })


@pytest.fixture
def sample_right_df():
    """Create sample right DataFrame"""
    return pd.DataFrame({
        'receive_time': ['2026-01-15 10:00:00', '2026-01-15 10:00:01', '2026-01-15 10:00:05', '2026-01-15 10:00:06'],
        'exch_product_id': ['CGB01', 'CGB02', 'CGB05', 'CGB06'],
        'settle_speed': [0, 0, 0, 0],
        'business_date': ['2026.01.15'] * 4,
        'product_type': ['BOND'] * 4,
        'last_trade_price': [100.5, 101.1, 105.0, 106.0]
    })


def test_match_records_simple(sample_left_df, sample_right_df):
    """Test simple record matching"""
    matched, left_only, right_only = match_records(sample_left_df, sample_right_df)

    # CGB01 and CGB02 should match (same receive_time, exch_product_id, settle_speed)
    assert len(matched) == 2

    # CGB03 and CGB04 are only in left
    assert len(left_only) == 2

    # CGB05 and CGB06 are only in right
    assert len(right_only) == 2


def test_match_records_all_matched():
    """Test when all records match"""
    left_df = pd.DataFrame({
        'receive_time': ['2026-01-15 10:00:00', '2026-01-15 10:00:01'],
        'exch_product_id': ['CGB01', 'CGB02'],
        'settle_speed': [0, 0],
        'price': [100.5, 101.0]
    })

    right_df = pd.DataFrame({
        'receive_time': ['2026-01-15 10:00:00', '2026-01-15 10:00:01'],
        'exch_product_id': ['CGB01', 'CGB02'],
        'settle_speed': [0, 0],
        'price': [100.5, 101.0]
    })

    matched, left_only, right_only = match_records(left_df, right_df)

    assert len(matched) == 2
    assert len(left_only) == 0
    assert len(right_only) == 0


def test_match_records_none_matched():
    """Test when no records match"""
    left_df = pd.DataFrame({
        'receive_time': ['2026-01-15 10:00:00'],
        'exch_product_id': ['CGB01'],
        'settle_speed': [0],
        'price': [100.5]
    })

    right_df = pd.DataFrame({
        'receive_time': ['2026-01-15 10:01:00'],
        'exch_product_id': ['CGB02'],
        'settle_speed': [0],
        'price': [101.0]
    })

    matched, left_only, right_only = match_records(left_df, right_df)

    assert len(matched) == 0
    assert len(left_only) == 1
    assert len(right_only) == 1


def test_match_records_duplicates():
    """Test handling of duplicate matching keys"""
    left_df = pd.DataFrame({
        'receive_time': ['2026-01-15 10:00:00', '2026-01-15 10:00:00'],
        'exch_product_id': ['CGB01', 'CGB01'],
        'settle_speed': [0, 0],
        'price': [100.5, 100.6]
    })

    right_df = pd.DataFrame({
        'receive_time': ['2026-01-15 10:00:00'],
        'exch_product_id': ['CGB01'],
        'settle_speed': [0],
        'price': [100.5]
    })

    matched, left_only, right_only = match_records(left_df, right_df)

    # Both left records should match the one right record
    assert len(matched) == 2
    assert len(left_only) == 0
    assert len(right_only) == 0


def test_match_records_empty_dataframes():
    """Test with empty DataFrames"""
    left_df = pd.DataFrame(columns= MATCHING_KEYS_BOND + ['price'])
    right_df = pd.DataFrame(columns= MATCHING_KEYS_BOND + ['price'])

    matched, left_only, right_only = match_records(left_df, right_df)

    assert len(matched) == 0
    assert len(left_only) == 0
    assert len(right_only) == 0


def test_match_records_chunked_processing(sample_left_df, sample_right_df):
    """Test chunked processing aggregation"""
    # Simulate chunked processing by splitting the data
    chunk_size = 2

    all_matched = []
    all_left_only = []
    all_right_only = []

    for i in range(0, len(sample_left_df), chunk_size):
        left_chunk = sample_left_df.iloc[i:i+chunk_size]
        for j in range(0, len(sample_right_df), chunk_size):
            right_chunk = sample_right_df.iloc[j:j+chunk_size]

            matched, left_only, right_only = match_records(left_chunk, right_chunk)
            all_matched.append(matched)
            all_left_only.append(left_only)
            all_right_only.append(right_only)

    # Aggregate results
    total_matched = pd.concat(all_matched, ignore_index=True)
    total_left_only = pd.concat(all_left_only, ignore_index=True)
    total_right_only = pd.concat(all_right_only, ignore_index=True)

    # Compare with non-chunked result
    expected_matched, expected_left_only, expected_right_only = match_records(
        sample_left_df, sample_right_df
    )

    assert len(total_matched) == len(expected_matched)
    assert len(total_left_only) == len(expected_left_only)
    assert len(total_right_only) == len(expected_right_only)


def test_match_records_settle_speed_difference():
    """Test that different settle_speed values do not match"""
    left_df = pd.DataFrame({
        'receive_time': ['2026-01-15 10:00:00'],
        'exch_product_id': ['CGB01'],
        'settle_speed': [0],
        'price': [100.5]
    })

    right_df = pd.DataFrame({
        'receive_time': ['2026-01-15 10:00:00'],
        'exch_product_id': ['CGB01'],
        'settle_speed': [1],
        'price': [100.5]
    })

    matched, left_only, right_only = match_records(left_df, right_df)

    # Should not match because settle_speed differs
    assert len(matched) == 0
    assert len(left_only) == 1
    assert len(right_only) == 1


# Tests for position-based matching (NEW)


def test_position_based_matching_equal_size():
    """Verify matching when both DataFrames have same size"""
    left_df = pd.DataFrame({
        'receive_time': pd.to_datetime(['2026-01-15 10:00:00', '2026-01-15 10:05:00', '2026-01-15 10:10:00']),
        'exch_product_id': ['CGB01', 'CGB02', 'CGB03'],
        'settle_speed': ['T+0', 'T+0', 'T+1'],
        'price': [100.5, 101.0, 102.0]
    })

    right_df = pd.DataFrame({
        'receive_time': pd.to_datetime(['2026-01-15 10:00:00', '2026-01-15 10:05:00', '2026-01-15 10:10:00']),
        'exch_product_id': ['CGB01', 'CGB02', 'CGB03'],
        'settle_speed': ['T+0', 'T+0', 'T+1'],
        'price': [100.5, 101.0, 102.0]
    })

    matched, left_only, right_only = match_records_by_position(left_df, right_df)

    # All records should match (same size)
    assert len(matched) == 3
    assert len(left_only) == 0
    assert len(right_only) == 0

    # Verify matched structure (MultiIndex columns)
    assert len(matched.columns) == len(left_df.columns) * 2
    assert ('left', 'price') in matched.columns
    assert ('right', 'price') in matched.columns


def test_position_based_matching_unequal_size():
    """Verify unpaired records when DataFrames have different sizes"""
    left_df = pd.DataFrame({
        'receive_time': pd.to_datetime(['2026-01-15 10:00:00', '2026-01-15 10:05:00', '2026-01-15 10:10:00']),
        'exch_product_id': ['CGB01', 'CGB02', 'CGB03'],
        'price': [100.5, 101.0, 102.0]
    })

    right_df = pd.DataFrame({
        'receive_time': pd.to_datetime(['2026-01-15 10:00:00', '2026-01-15 10:05:00']),
        'exch_product_id': ['CGB01', 'CGB02'],
        'price': [100.5, 101.0]
    })

    matched, left_only, right_only = match_records_by_position(left_df, right_df)

    # First 2 records should match
    assert len(matched) == 2
    # 1 record only in left
    assert len(left_only) == 1
    assert left_only['exch_product_id'].values[0] == 'CGB03'
    # No records only in right
    assert len(right_only) == 0


def test_position_based_matching_empty_dataframes():
    """Verify handling of empty DataFrames"""
    # Both empty
    left_df_empty = pd.DataFrame(columns=['receive_time', 'exch_product_id', 'price'])
    right_df_empty = pd.DataFrame(columns=['receive_time', 'exch_product_id', 'price'])

    matched, left_only, right_only = match_records_by_position(left_df_empty, right_df_empty)

    assert len(matched) == 0
    assert len(left_only) == 0
    assert len(right_only) == 0

    # One empty
    left_df = pd.DataFrame({
        'receive_time': pd.to_datetime(['2026-01-15 10:00:00']),
        'exch_product_id': ['CGB01'],
        'price': [100.5]
    })

    right_df_empty2 = pd.DataFrame(columns=['receive_time', 'exch_product_id', 'price'])

    matched, left_only, right_only = match_records_by_position(left_df, right_df_empty2)

    # No matches, all left records are unpaired
    assert len(matched) == 0
    assert len(left_only) == 1
    assert len(right_only) == 0


def test_position_based_matching_performance():
    """Verify <10 second performance for 10,000 records"""
    # Create large datasets
    n = 10000
    left_df = pd.DataFrame({
        'receive_time': pd.to_datetime([f'2026-01-15 10:{i//60:02d}:{i%60:02d}' for i in range(n)]),
        'exch_product_id': [f'CGB{i%100:03d}' for i in range(n)],
        'settle_speed': ['T+0' if i % 2 == 0 else 'T+1' for i in range(n)],
        'price': [100 + i * 0.001 for i in range(n)]
    })

    right_df = pd.DataFrame({
        'receive_time': pd.to_datetime([f'2026-01-15 10:{i//60:02d}:{i%60:02d}' for i in range(n)]),
        'exch_product_id': [f'CGB{i%100:03d}' for i in range(n)],
        'settle_speed': ['T+0' if i % 2 == 0 else 'T+1' for i in range(n)],
        'price': [100 + i * 0.001 for i in range(n)]
    })

    # Measure execution time
    start_time = time.time()
    matched, left_only, right_only = match_records_by_position(left_df, right_df)
    elapsed_time = time.time() - start_time

    # Verify results
    assert len(matched) == n
    assert len(left_only) == 0
    assert len(right_only) == 0

    # Verify performance target
    assert elapsed_time < 10.0, f"Position-based matching took {elapsed_time:.2f}s, expected <10s"

    print(f"Position-based matching for {n} records: {elapsed_time:.2f}s (<10s target met)")
