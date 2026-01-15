"""Query executor for DolphinDB with chunked retrieval"""
import pandas as pd
from typing import Optional
from dolphindb.session import Session
from ..config.loader import DolphinDBConfig
from .connection import ConnectionWrapper
from ..utils.date_helpers import format_date_for_sql


CHUNK_SIZE = 100000  # Number of records to retrieve per chunk


def execute_query(
    session: Session,
    database: str,
    table_name: str,
    business_date: str,
    product_type: Optional[str] = None,
    tick_type: Optional[str] = None,
    chunk_size: int = CHUNK_SIZE
) -> pd.DataFrame:
    """
    Execute SQL query for market price table with optional filters

    Args:
        session: DolphinDB session
        database: Database name
        table_name: Table name (note: "market_price" in specification)
        business_date: Business date in YYYY.MM.DD format
        product_type: Optional product_type filter
        tick_type: Optional tick_type filter
        chunk_size: Number of records to retrieve per chunk

    Returns:
        DataFrame with query results

    Raises:
        Exception: If query execution fails
    """
    # Build SQL query with filters
    where_clauses = [f"business_date = {business_date}"]

    if product_type is not None:
        where_clauses.append(f"product_type = `{product_type}")

    if tick_type is not None:
        where_clauses.append(f"tick_type = `{tick_type}")

    where_clause = " and ".join(where_clauses)

    # Execute query using DolphinDB's loadTable function
    query = f"select * from loadTable(\"{database}\", \"{table_name}\") where {where_clause}"

    try:
        result_df = session.run(query)
        return result_df
    except Exception as e:
        raise Exception(f"Query execution failed: {e}")


def execute_query_with_chunks(
    session: Session,
    database: str,
    table_name: str,
    business_date: str,
    product_type: Optional[str] = None,
    tick_type: Optional[str] = None,
    chunk_size: int = CHUNK_SIZE
):
    """
    Execute SQL query and return all data at once (no chunking)

    Args:
        session: DolphinDB session
        database: Database name
        table_name: Table name
        business_date: Business date in YYYY.MM.DD format
        product_type: Optional product_type filter
        tick_type: Optional tick_type filter
        chunk_size: Not used (kept for API compatibility)

    Yields:
        Single DataFrame with all query results

    Raises:
        Exception: If query execution fails
    """
    # Build SQL query with filters
    where_clauses = [f"business_date = {business_date}"]

    if product_type is not None:
        where_clauses.append(f"product_type = `{product_type}")

    if tick_type is not None:
        where_clauses.append(f"tick_type = `{tick_type}")

    where_clause = " and ".join(where_clauses)

    # Execute query to get all data
    query = f"select * from loadTable(\"{database}\", \"{table_name}\") where {where_clause}"

    try:
        result_df = session.run(query)
        if not result_df.empty:
            yield result_df
    except Exception as e:
        raise Exception(f"Query execution failed: {e}")


def retrieve_data(
    config: DolphinDBConfig,
    database: str,
    table_name: str,
    business_date: str,
    product_type: Optional[str] = None,
    tick_type: Optional[str] = None,
    chunk_size: int = CHUNK_SIZE
):
    """
    Retrieve data from DolphinDB with automatic connection management

    Args:
        config: DolphinDB configuration
        database: Database name
        table_name: Table name
        business_date: Business date in YYYY.MM.DD format
        product_type: Optional product_type filter
        tick_type: Optional tick_type filter
        chunk_size: Number of records to retrieve per chunk

    Yields:
        DataFrame chunks with query results
    """
    with ConnectionWrapper(config) as conn:
        session = conn.connect()

        for chunk in execute_query_with_chunks(
            session,
            database,
            table_name,
            business_date,
            product_type,
            tick_type,
            chunk_size
        ):
            yield chunk
