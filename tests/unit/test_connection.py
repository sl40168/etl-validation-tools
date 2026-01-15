"""Unit tests for connection wrapper"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.db.connection import ConnectionWrapper, test_connection
from src.config.loader import DolphinDBConfig
import dolphindb.session as ddb


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


def test_connection_wrapper_init(mock_config):
    """Test connection wrapper initialization"""
    wrapper = ConnectionWrapper(mock_config)
    assert wrapper.config == mock_config
    assert wrapper.session is None


@patch('src.db.connection.ddb.Session')
def test_connection_wrapper_connect_success(mock_session_class, mock_config):
    """Test successful connection"""
    mock_session = Mock()
    mock_session_class.return_value = mock_session

    wrapper = ConnectionWrapper(mock_config)
    session = wrapper.connect()

    assert session == mock_session
    assert wrapper.session == mock_session
    mock_session_class.assert_called_once_with(
        host='localhost',
        port=8848,
        username='admin',
        password='123456'
    )


@patch('src.db.connection.ddb.Session')
def test_connection_wrapper_connect_retry(mock_session_class, mock_config):
    """Test connection retry on failure"""
    mock_session = Mock()
    # Fail first two times, succeed third time
    call_count = [0]

    def create_session(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] < 3:
            raise ddb.OperationalError("Connection failed")
        return mock_session

    mock_session_class.side_effect = create_session

    wrapper = ConnectionWrapper(mock_config)
    session = wrapper.connect()

    assert session == mock_session
    assert call_count[0] == 3


@patch('src.db.connection.ddb.Session')
def test_connection_wrapper_connect_failure_after_retries(mock_session_class, mock_config):
    """Test connection failure after all retries"""
    mock_session_class.side_effect = ddb.OperationalError("Persistent failure")

    wrapper = ConnectionWrapper(mock_config)

    with pytest.raises(ddb.OperationalError, match="Persistent failure"):
        wrapper.connect()


@patch('src.db.connection.ddb.Session')
def test_test_connection_success(mock_session_class, mock_config):
    """Test successful connection test"""
    mock_session = Mock()
    mock_session.run.return_value = None
    mock_session_class.return_value = mock_session

    result = test_connection(mock_config)
    assert result is True
    mock_session.run.assert_called_with("1+1")


@patch('src.db.connection.ddb.Session')
def test_test_connection_failure(mock_session_class, mock_config):
    """Test connection test failure"""
    mock_session = Mock()
    mock_session.run.side_effect = Exception("Query failed")
    mock_session_class.return_value = mock_session

    with pytest.raises(ddb.OperationalError, match="Connection test failed"):
        test_connection(mock_config)


def test_connection_wrapper_context_manager(mock_config):
    """Test connection wrapper as context manager"""
    with patch('src.db.connection.ddb.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        with ConnectionWrapper(mock_config) as wrapper:
            assert wrapper.session == mock_session

        # Verify connection was closed
        mock_session.close.assert_called_once()


def test_connection_wrapper_close(mock_config):
    """Test closing connection"""
    with patch('src.db.connection.ddb.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        wrapper = ConnectionWrapper(mock_config)
        wrapper.connect()
        wrapper.close()

        assert wrapper.session is None
        mock_session.close.assert_called_once()
