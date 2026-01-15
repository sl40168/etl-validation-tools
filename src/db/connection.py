"""DolphinDB connection wrapper with retry logic"""
import sys
from typing import Optional
from dolphindb.session import Session
from ..config.loader import DolphinDBConfig
from ..utils.retry import retry_on_specific_exceptions


class ConnectionWrapper:
    """Wrapper for DolphinDB connection with retry logic"""

    def __init__(self, config: DolphinDBConfig):
        """
        Initialize connection wrapper

        Args:
            config: DolphinDB configuration
        """
        self.config = config
        self.session: Optional[Session] = None

    @retry_on_specific_exceptions(
        Exception,
        max_attempts=3
    )
    def connect(self) -> Session:
        """
        Establish connection to DolphinDB with retry logic

        Returns:
            Connected DolphinDB Session object

        Raises:
            Exception: If connection fails after retries
        """
        self.session = Session(
            host=self.config.host,
            port=self.config.port,
            userid=self.config.username,
            password=self.config.password
        )
        return self.session

    @retry_on_specific_exceptions(
        Exception,
        max_attempts=3
    )
    def test_connection(self) -> bool:
        """
        Test connection to DolphinDB

        Returns:
            True if connection successful

        Raises:
            Exception: If connection fails after retries
        """
        if self.session is None:
            self.connect()

        # Execute a simple query to test connection
        try:
            self.session.run("1+1")
            return True
        except Exception as e:
            raise Exception(f"Connection test failed: {e}")

    def close(self) -> None:
        """Close the connection"""
        if self.session is not None:
            self.session.close()
            self.session = None

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def verify_connection(config: DolphinDBConfig) -> bool:
    """
    Verify connection to DolphinDB instance

    Args:
        config: DolphinDB configuration

    Returns:
        True if connection successful

    Raises:
        Exception: If connection fails after retries
    """
    with ConnectionWrapper(config) as conn:
        return conn.test_connection()
