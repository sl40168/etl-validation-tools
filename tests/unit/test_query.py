"""Unit tests for query executor"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from src.db.query import execute_query, execute_query_with_chunks, retrieve_data, CHUNK_SIZE
from src.config.loader import DolphinDBConfig


@pytest.fixture
def mock_session():
    """Create a mock DolphinDB session"""
    session = Mock(spec=object)
    return session


@pytest.fixture
def mock_config():
    """Create a mock DolphinDB configuration"""
    return DolphinDBConfig(
        host='localhost',
        port=8848,
        username='admin',
        password='123456',
        database='market_data'
    )


def test_execute_query_no_filters(mock_session):
    """Test executing query without filters"""
    # Mock query result
    mock_df = pd.DataFrame({
        'business_date': ['2026.01.15'],
        'exch_product_id': ['CGB01'],
        'product_type': ['BOND'],
        'tick_type': ['TRADE']
    })
    mock_session.run.return_value = mock_df

    result = execute_query(
        session=mock_session,
        database='market_data',
        table_name='marekt_price',
        business_date='2026.01.15'
    )

    pd.testing.assert_frame_equal(result, mock_df)
    mock_session.run.assert_called_once()


def test_execute_query_with_filters(mock_session):
    """Test executing query with product_type and tick_type filters"""
    mock_df = pd.DataFrame({
        'business_date': ['2026.01.15'],
        'exch_product_id': ['CGB01'],
        'product_type': ['BOND'],
        'tick_type': ['TRADE']
    })
    mock_session.run.return_value = mock_df

    result = execute_query(
        session=mock_session,
        database='market_data',
        table_name='marekt_price',
        business_date='2026.01.15',
        product_type='BOND',
        tick_type='TRADE'
    )

    pd.testing.assert_frame_equal(result, mock_df)
    # Verify filters are in the query
    call_args = mock_session.run.call_args[0][0]
    assert 'product_type == `BOND`' in call_args
    assert 'tick_type == `TRADE`' in call_args


def test_execute_query_error(mock_session):
    """Test error when query execution fails"""
    mock_session.run.side_effect = Exception("Query failed")

    with pytest.raises(Exception, match="Query execution failed"):
        execute_query(
            session=mock_session,
            database='market_data',
            table_name='marekt_price',
            business_date='2026.01.15'
        )


def test_execute_query_with_chunks(mock_session):
    """Test chunked query execution"""
    # Mock count query
    mock_count_df = pd.DataFrame({'': [200000]})  # 200k total records
    # Mock chunk queries
    mock_chunk1 = pd.DataFrame({'col': list(range(100000))})
    mock_chunk2 = pd.DataFrame({'col': list(range(100000, 200000))})

    call_count = [0]

    def mock_run(query):
        call_count[0] += 1
        if 'count' in query:
            return mock_count_df
        elif 'offset 0' in query:
            return mock_chunk1
        elif 'offset 100000' in query:
            return mock_chunk2
        else:
            raise ValueError("Unexpected query")

    mock_session.run.side_effect = mock_run

    chunks = list(execute_query_with_chunks(
        session=mock_session,
        database='market_data',
        table_name='marekt_price',
        business_date='2026.01.15',
        chunk_size=100000
    ))

    assert len(chunks) == 2
    pd.testing.assert_frame_equal(chunks[0], mock_chunk1)
    pd.testing.assert_frame_equal(chunks[1], mock_chunk2)


def test_execute_query_with_chunks_empty_result(mock_session):
    """Test chunked query when no data exists"""
    mock_count_df = pd.DataFrame({'': [0]})  # No records
    mock_session.run.return_value = mock_count_df

    chunks = list(execute_query_with_chunks(
        session=mock_session,
        database='market_data',
        table_name='marekt_price',
        business_date='2026.01.15',
        chunk_size=100000
    ))

    assert len(chunks) == 0


@patch('src.db.query.ConnectionWrapper')
def test_retrieve_data(mock_connection_wrapper_class, mock_config):
    """Test retrieve_data with automatic connection management"""
    mock_wrapper = MagicMock()
    mock_connection_wrapper_class.return_value.__enter__.return_value = mock_wrapper

    mock_session = Mock()
    mock_wrapper.connect.return_value = mock_session

    mock_df = pd.DataFrame({'col': [1, 2, 3]})
    mock_session.run.return_value = mock_df

    chunks = list(retrieve_data(
        config=mock_config,
        database='market_data',
        table_name='marekt_price',
        business_date='2026.01.15'
    ))

    assert len(chunks) == 1
    pd.testing.assert_frame_equal(chunks[0], mock_df)


def test_count_query_failure(mock_session):
    """Test error when count query fails"""
    mock_session.run.side_effect = Exception("Count query failed")

    with pytest.raises(Exception, match="Count query failed"):
        list(execute_query_with_chunks(
            session=mock_session,
            database='market_data',
            table_name='marekt_price',
            business_date='2026.01.15',
            chunk_size=100000
        ))


def test_chunk_query_failure(mock_session):
    """Test error when chunk query fails"""
    mock_count_df = pd.DataFrame({'': [200000]})
    mock_session.run.side_effect = [mock_count_df, Exception("Chunk query failed")]

    with pytest.raises(Exception, match="Chunk query failed"):
        list(execute_query_with_chunks(
            session=mock_session,
            database='market_data',
            table_name='marekt_price',
            business_date='2026.01.15',
            chunk_size=100000
        ))
