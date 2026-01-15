"""Configuration loader for DolphinDB connections"""
import configparser
from typing import Dict, NamedTuple


class DolphinDBConfig(NamedTuple):
    """DolphinDB connection configuration"""
    host: str
    port: int
    username: str
    password: str
    database: str


def load_config(config_path: str) -> Dict[str, DolphinDBConfig]:
    """
    Load and parse INI configuration file

    Args:
        config_path: Path to the INI configuration file

    Returns:
        Dictionary with 'left' and 'right' keys containing DolphinDBConfig objects

    Raises:
        FileNotFoundError: If config file does not exist
        ValueError: If INI format is invalid or required fields are missing
    """
    config = configparser.ConfigParser()

    try:
        config.read(config_path)
    except configparser.Error as e:
        raise ValueError(f"Invalid INI format in configuration file: {e}")

    # Validate sections exist
    if 'instance_left' not in config:
        raise ValueError("Missing required section: [instance_left]")
    if 'instance_right' not in config:
        raise ValueError("Missing required section: [instance_right]")

    # Load and validate left instance config
    left_config = _load_instance_config(config['instance_left'], 'instance_left')
    right_config = _load_instance_config(config['instance_right'], 'instance_right')

    return {
        'left': left_config,
        'right': right_config
    }


def _load_instance_config(section: configparser.SectionProxy, section_name: str) -> DolphinDBConfig:
    """
    Load and validate configuration for a single instance

    Args:
        section: ConfigParser section for the instance
        section_name: Name of the section (for error messages)

    Returns:
        DolphinDBConfig object with validated fields

    Raises:
        ValueError: If required fields are missing or invalid
    """
    required_fields = ['host', 'port', 'username', 'password', 'database']

    # Check all required fields are present
    for field in required_fields:
        if field not in section:
            raise ValueError(f"Missing required field: {field} in section [{section_name}]")

    # Validate port is integer in valid range
    try:
        port = int(section['port'])
        if not 1 <= port <= 65535:
            raise ValueError(f"Port must be between 1 and 65535, got {port}")
    except ValueError as e:
        raise ValueError(f"Invalid port in section [{section_name}]: {e}")

    # Validate other required fields are not empty
    host = section['host'].strip()
    username = section['username'].strip()
    password = section['password'].strip()
    database = section['database'].strip()

    if not host:
        raise ValueError(f"Field 'host' cannot be empty in section [{section_name}]")
    if not username:
        raise ValueError(f"Field 'username' cannot be empty in section [{section_name}]")
    if not password:
        raise ValueError(f"Field 'password' cannot be empty in section [{section_name}]")
    if not database:
        raise ValueError(f"Field 'database' cannot be empty in section [{section_name}]")

    return DolphinDBConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        database=database
    )


def validate_config(config_dict: Dict[str, DolphinDBConfig]) -> Dict[str, DolphinDBConfig]:
    """
    Validate loaded configuration object

    Args:
        config_dict: Configuration dictionary with 'left' and 'right' keys

    Returns:
        The validated configuration dictionary

    Raises:
        ValueError: If configuration is invalid
    """
    if 'left' not in config_dict or 'right' not in config_dict:
        raise ValueError("Configuration must contain both 'left' and 'right' instances")

    # Validate each instance configuration
    for side, config in config_dict.items():
        if not isinstance(config, DolphinDBConfig):
            raise ValueError(f"Invalid configuration type for {side} instance")

    return config_dict
