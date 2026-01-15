"""Integration tests for validation workflow"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock, call
from src.config.loader import load_config, validate_config, DolphinDBConfig
from src.db.connection import ConnectionWrapper, test_connection
from src.validation.matcher import match_records
from src.validation.comparator import compare_columns
import tempfile
import os


@pytest.fixture
def mock_config_dict():
    """Create mock configuration dictionary"""
    return {
        'left': DolphinDBConfig('localhost', 8848, 'admin', '123456', 'market_data'),
        'right': DolphinDBConfig('localhost', 8849, 'admin', '123456', 'market_data')
    }


@pytest.fixture
def sample_left_data():
    """Create sample left data"""
    return pd.DataFrame({
        'receive_time': ['2026-01-15 10:00:00', '2026-01-15 10:00:01', '2026-01-15 10:00:02'],
        'exch_product_id': ['CGB01', 'CGB02', 'CGB03'],
        'settle_speed': [0, 0, 1],
        'business_date': ['2026.01.15'] * 3,
        'product_type': ['BOND'] * 3,
        'tick_type': ['TRADE'] * 3,
        'last_trade_price': [100.5, 101.0, 102.0],
        'last_trade_volume': [1000, 2000, 3000],
        'total_volume': [1000, 2000, 3000],
        'create_time': ['2026-01-15 10:00:01'] * 3,
        'store_time': ['2026-01-15 10:00:02'] * 3
    })


@pytest.fixture
def sample_right_data():
    """Create sample right data with some differences"""
    return pd.DataFrame({
        'receive_time': ['2026-01-15 10:00:00', '2026-01-15 10:00:01', '2026-01-15 10:00:04'],
        'exch_product_id': ['CGB01', 'CGB02', 'CGB04'],
        'settle_speed': [0, 0, 0],
        'business_date': ['2026.01.15'] * 3,
        'product_type': ['BOND'] * 3,
        'tick_type': ['TRADE'] * 3,
        'last_trade_price': [100.5, 101.1, 105.0],  # CGB02 has different price
        'last_trade_volume': [1000, 2000, 4000],
        'total_volume': [1000, 2000, 4000],
        'create_time': ['2026-01-15 10:00:03'] * 3,
        'store_time': ['2026-01-15 10:00:04'] * 3
    })


def test_end_to_end_validation_workflow_single_group(sample_left_data, sample_right_data):
    """Test end-to-end validation for a single validation group"""
    # Step 1: Match records
    matched_pairs, left_only, right_only = match_records(sample_left_data, sample_right_data)

    assert len(matched_pairs) == 2  # CGB01 and CGB02 match
    assert len(left_only) == 1  # CGB03
    assert len(right_only) == 1  # CGB04

    # Step 2: Compare columns for matched pairs
    all_differences = {}
    for _, row in matched_pairs.iterrows():
        left_record = row.filter(like='_x').dropna()
        right_record = row.filter(like='_y').dropna()

        # Remove the suffixes for comparison
        left_record_clean = left_record.copy()
        right_record_clean = right_record.copy()
        left_record_clean.index = left_record_clean.index.str.replace('_x$', '', regex=True)
        right_record_clean.index = right_record_clean.index.str.replace('_y$', '', regex=True)

        differences = compare_columns(left_record_clean, right_record_clean)
        for diff in differences:
            all_differences[diff] = all_differences.get(diff, 0) + 1

    # CGB02 should have last_trade_price difference (100.0 vs 101.1)
    assert 'last_trade_price' in all_differences
    assert all_differences['last_trade_price'] == 1


@patch('src.db.connection.ddb.Session')
def test_validation_workflow_with_mocked_connections(mock_session_class, mock_config_dict):
    """Test validation workflow with mocked DolphinDB connections"""
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write("""[instance_left]
host = localhost
port = 8848
username = admin
password = 123456
database = market_data

[instance_right]
host = localhost
port = 8849
username = admin
password = 123456
database = market_data
""")
        f.flush()
        config_path = f.name

    try:
        # Load configuration
        config = load_config(config_path)
        validated_config = validate_config(config)

        # Test connections
        with patch.object(ConnectionWrapper, 'connect') as mock_connect:
            mock_session = Mock()
            mock_connect.return_value = mock_session
            mock_session.run.return_value = None

            test_connection(validated_config['left'])
            test_connection(validated_config['right'])

    finally:
        os.unlink(config_path)


def test_aggregate_statistics_across_chunks(sample_left_data, sample_right_data):
    """Test aggregating statistics across multiple chunks"""
    # Simulate chunked processing (2 chunks)
    chunk_size = 2

    total_matched_count = 0
    total_unmatched_count = 0
    all_column_differences = {}
    left_retrieved_count = len(sample_left_data)
    right_retrieved_count = len(sample_right_data)

    # Process in chunks
    for i in range(0, len(sample_left_data), chunk_size):
        for j in range(0, len(sample_right_data), chunk_size):
            left_chunk = sample_left_data.iloc[i:i+chunk_size]
            right_chunk = sample_right_data.iloc[j:j+chunk_size]

            matched, left_only, right_only = match_records(left_chunk, right_chunk)

            total_matched_count += len(matched)
            total_unmatched_count += len(left_only) + len(right_only)

            # Compare matched pairs
            for _, row in matched.iterrows():
                left_record = row.filter(like='_x').dropna()
                right_record = row.filter(like='_y').dropna()

                left_record_clean = left_record.copy()
                right_record_clean = right_record.copy()
                left_record_clean.index = left_record_clean.index.str.replace('_x$', '', regex=True)
                right_record_clean.index = right_record_clean.index.str.replace('_y$', '', regex=True)

                differences = compare_columns(left_record_clean, right_record_clean)
                for diff in differences:
                    all_column_differences[diff] = all_column_differences.get(diff, 0) + 1

    # Verify statistics
    assert left_retrieved_count == 3
    assert right_retrieved_count == 3
    assert total_matched_count == 4  # CGB01 matches twice, CGB02 matches twice
    assert total_unmatched_count == 2  # CGB03 (left), CGB04 (right)


def test_validation_statistics_accuracy(sample_left_data, sample_right_data):
    """Test accuracy of validation statistics"""
    matched, left_only, right_only = match_records(sample_left_data, sample_right_data)

    left_retrieved = len(sample_left_data)
    right_retrieved = len(sample_right_data)
    matched_count = len(matched)
    left_unmatched_count = len(left_only)
    right_unmatched_count = len(right_only)

    # Verify consistency
    assert left_retrieved >= matched_count
    assert right_retrieved >= matched_count
    assert matched_count + left_unmatched_count == left_retrieved
    assert matched_count + right_unmatched_count == right_retrieved


def test_empty_validation_result():
    """Test validation with empty datasets"""
    left_data = pd.DataFrame(columns=[
        'receive_time', 'exch_product_id', 'settle_speed', 'last_trade_price'
    ])
    right_data = pd.DataFrame(columns=[
        'receive_time', 'exch_product_id', 'settle_speed', 'last_trade_price'
    ])

    matched, left_only, right_only = match_records(left_data, right_data)

    assert len(matched) == 0
    assert len(left_only) == 0
    assert len(right_only) == 0
