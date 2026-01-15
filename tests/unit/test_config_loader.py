"""Unit tests for config loader"""
import pytest
from src.config.loader import load_config, validate_config, DolphinDBConfig, _load_instance_config
import configparser
import tempfile
import os


def test_load_valid_config():
    """Test loading a valid configuration file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write("""[instance_left]
host = localhost
port = 8848
username = admin
password = 123456
database = market_data

[instance_right]
host = 192.168.1.100
port = 8848
username = admin
password = 123456
database = market_data
""")
        f.flush()
        config_path = f.name

    try:
        config = load_config(config_path)
        assert 'left' in config
        assert 'right' in config
        assert config['left'].host == 'localhost'
        assert config['left'].port == 8848
        assert config['left'].username == 'admin'
        assert config['left'].password == '123456'
        assert config['left'].database == 'market_data'
    finally:
        os.unlink(config_path)


def test_load_config_missing_section():
    """Test error when [instance_left] or [instance_right] section is missing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write("""[instance_left]
host = localhost
port = 8848
username = admin
password = 123456
database = market_data
""")
        f.flush()
        config_path = f.name

    try:
        with pytest.raises(ValueError, match="Missing required section: \\[instance_right\\]"):
            load_config(config_path)
    finally:
        os.unlink(config_path)


def test_load_config_missing_field():
    """Test error when required field is missing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write("""[instance_left]
host = localhost
username = admin
password = 123456
database = market_data

[instance_right]
host = 192.168.1.100
port = 8848
username = admin
password = 123456
database = market_data
""")
        f.flush()
        config_path = f.name

    try:
        with pytest.raises(ValueError, match="Missing required field: port"):
            load_config(config_path)
    finally:
        os.unlink(config_path)


def test_load_config_invalid_port():
    """Test error when port is invalid"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write("""[instance_left]
host = localhost
port = abc
username = admin
password = 123456
database = market_data

[instance_right]
host = 192.168.1.100
port = 8848
username = admin
password = 123456
database = market_data
""")
        f.flush()
        config_path = f.name

    try:
        with pytest.raises(ValueError, match="Invalid port"):
            load_config(config_path)
    finally:
        os.unlink(config_path)


def test_validate_config_valid():
    """Test validating a valid configuration"""
    config = {
        'left': DolphinDBConfig('localhost', 8848, 'admin', '123456', 'market_data'),
        'right': DolphinDBConfig('192.168.1.100', 8848, 'admin', '123456', 'market_data')
    }
    validated = validate_config(config)
    assert validated == config


def test_validate_config_missing_side():
    """Test error when configuration is missing a side"""
    config = {
        'left': DolphinDBConfig('localhost', 8848, 'admin', '123456', 'market_data')
    }
    with pytest.raises(ValueError, match="must contain both 'left' and 'right'"):
        validate_config(config)


def test_config_not_found():
    """Test error when config file does not exist"""
    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        load_config('/nonexistent/path/config.ini')


def test_load_config_empty_field():
    """Test error when required field is empty"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write("""[instance_left]
host =
port = 8848
username = admin
password = 123456
database = market_data

[instance_right]
host = 192.168.1.100
port = 8848
username = admin
password = 123456
database = market_data
""")
        f.flush()
        config_path = f.name

    try:
        with pytest.raises(ValueError, match="Field 'host' cannot be empty"):
            load_config(config_path)
    finally:
        os.unlink(config_path)
