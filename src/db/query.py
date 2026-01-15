"""Query executor for DolphinDB with chunked retrieval"""
import pandas as pd
from typing import Optional
from dolphindb.session import Session
from ..config.loader import DolphinDBConfig
from .connection import ConnectionWrapper
from ..utils.date_helpers import format_date_for_sql, construct_time_range


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
    Execute SQL query for market price table with optional filters and sorting

    Query results are sorted by receive_time, exch_product_id, settle_speed at database level
    for consistent ordering across both DolphinDB instances.

    For BOND_FUT product type, only records within trading hours (09:30:00-15:00:00) are included.

    Args:
        session: DolphinDB session
        database: Database name
        table_name: Table name (note: "market_price" in specification)
        business_date: Business date in YYYY.MM.DD format
        product_type: Optional product_type filter
        tick_type: Optional tick_type filter
        chunk_size: Number of records to retrieve per chunk

    Returns:
        DataFrame with query results, sorted by receive_time, exch_product_id, settle_speed

    Raises:
        Exception: If query execution fails
    """
    # Build SQL query with filters
    where_clauses = [f"business_date = {business_date}"]

    if product_type is not None:
        where_clauses.append(f"product_type = `{product_type}")

    # Add time filter for BOND_FUT (trading hours: 09:30:00-15:00:00)
    if product_type == "BOND_FUT":
        start_dt, end_dt = construct_time_range(business_date)
        where_clauses.append(f"receive_time > {start_dt}")
        where_clauses.append(f"receive_time < {end_dt}")

    if tick_type is not None:
        where_clauses.append(f"tick_type = `{tick_type}")

    where_clause = " and ".join(where_clauses)

    # Add ORDER BY clause for consistent sorting across instances
    order_by_clause = "order by receive_time, exch_product_id, settle_speed"

    # Execute query using DolphinDB's loadTable function
    query = f"select * from loadTable(\"{database}\", \"{table_name}\") where {where_clause} {order_by_clause}"

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

    Query results are sorted by receive_time, exch_product_id, settle_speed at database level
    for consistent ordering across both DolphinDB instances.

    For BOND_FUT product type, only records within trading hours (09:30:00-15:00:00) are included.

    Args:
        session: DolphinDB session
        database: Database name
        table_name: Table name
        business_date: Business date in YYYY.MM.DD format
        product_type: Optional product_type filter
        tick_type: Optional tick_type filter
        chunk_size: Not used (kept for API compatibility)

    Yields:
        Single DataFrame with all query results, sorted by receive_time, exch_product_id, settle_speed

    Raises:
        Exception: If query execution fails
    """
    # Build SQL query with filters
    where_clauses = [f"business_date = {business_date}"]

    if product_type is not None:
        where_clauses.append(f"product_type = `{product_type}")

    # Add time filter for BOND_FUT (trading hours: 09:30:00-15:00:00)
    if product_type == "BOND_FUT":
        start_dt, end_dt = construct_time_range(business_date)
        where_clauses.append(f"receive_time > {start_dt}")
        where_clauses.append(f"receive_time < {end_dt}")

    if tick_type is not None:
        where_clauses.append(f"tick_type = `{tick_type}")

    where_clause = " and ".join(where_clauses)

    # Add ORDER BY clause for consistent sorting across instances
    order_by_clause = "order by receive_time, exch_product_id, settle_speed"

    # Execute query to get all data
    query = f"select * from loadTable(\"{database}\", \"{table_name}\") where {where_clause} {order_by_clause}"

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
