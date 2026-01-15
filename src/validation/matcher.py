"""Record matcher for comparing data from two DolphinDB instances"""
import pandas as pd
from typing import Tuple

# Matching keys (composite key for matching records)
# For BOND: use all three keys
# For BOND_FUT: settle_speed may not be present
MATCHING_KEYS_BOND = ['receive_time', 'exch_product_id', 'settle_speed']
MATCHING_KEYS_BOND_FUT = ['receive_time', 'exch_product_id']

# Columns excluded from matching
EXCLUDED_FROM_MATCH = ['_merge']

# Chunk size for processing
CHUNK_SIZE = 100000


def get_matching_keys(df: pd.DataFrame) -> list:
    """
    Get appropriate matching keys based on available columns

    Args:
        df: DataFrame to check for available columns

    Returns:
        List of matching keys that exist in the DataFrame
    """
    # Try BOND matching keys first (includes settle_speed)
    if all(key in df.columns for key in MATCHING_KEYS_BOND):
        return MATCHING_KEYS_BOND
    # Fallback to BOND_FUT matching keys (without settle_speed)
    elif all(key in df.columns for key in MATCHING_KEYS_BOND_FUT):
        return MATCHING_KEYS_BOND_FUT
    else:
        missing_bond = set(MATCHING_KEYS_BOND) - set(df.columns)
        missing_fut = set(MATCHING_KEYS_BOND_FUT) - set(df.columns)
        raise ValueError(
            f"DataFrame missing required matching keys. "
            f"For BOND missing: {missing_bond}, For BOND_FUT missing: {missing_fut}"
        )


def match_records(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    chunk_size: int = CHUNK_SIZE
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Match records from two DataFrames using composite key

    Args:
        left_df: DataFrame from left DolphinDB instance
        right_df: DataFrame from right DolphinDB instance
        chunk_size: Number of records to process per chunk (for large datasets)

    Returns:
        Tuple of (matched_pairs, left_only, right_only):
        - matched_pairs: DataFrame with matched records (has '_merge' column)
        - left_only: Records only in left DataFrame
        - right_only: Records only in right DataFrame
    """
    # Handle empty DataFrames - return empty results
    if left_df.empty and right_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Determine matching keys based on available columns
    matching_keys = get_matching_keys(left_df)

    # Ensure matching keys exist in right DataFrame too
    missing_keys = set(matching_keys) - set(right_df.columns)
    if missing_keys:
        raise ValueError(f"Right DataFrame missing matching keys: {missing_keys}")

    # Perform outer merge on composite key
    merged_df = pd.merge(
        left_df,
        right_df,
        on=matching_keys,
        how='outer',
        indicator=True,
        suffixes=('_x', '_y')
    )

    # Split into matched, left_only, and right_only
    matched = merged_df[merged_df['_merge'] == 'both'].copy()
    left_only = merged_df[merged_df['_merge'] == 'left_only'].copy()
    right_only = merged_df[merged_df['_merge'] == 'right_only'].copy()

    # Remove the _merge column from matched (not needed downstream)
    matched = matched.drop(columns=['_merge'])

    # For left_only, remove the '_y' suffixed columns (they are NaN)
    left_only = left_only[[col for col in left_only.columns if not col.endswith('_y')]]
    # Rename '_x' columns back to original names
    left_only.columns = [col.replace('_x', '') if col.endswith('_x') else col
                        for col in left_only.columns]

    # For right_only, remove the '_x' suffixed columns (they are NaN)
    right_only = right_only[[col for col in right_only.columns if not col.endswith('_x')]]
    # Rename '_y' columns back to original names
    right_only.columns = [col.replace('_y', '') if col.endswith('_y') else col
                        for col in right_only.columns]

    return matched, left_only, right_only


def match_records_chunked(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    chunk_size: int = CHUNK_SIZE
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Match records with chunked processing for memory management

    Args:
        left_df: DataFrame from left DolphinDB instance
        right_df: DataFrame from right DolphinDB instance
        chunk_size: Number of records to process per chunk

    Returns:
        Tuple of (matched_pairs, left_only, right_only):
        - matched_pairs: DataFrame with matched records
        - left_only: Records only in left DataFrame
        - right_only: Records only in right DataFrame
    """
    # If datasets are small enough, process all at once
    if len(left_df) <= chunk_size and len(right_df) <= chunk_size:
        return match_records(left_df, right_df)

    # For large datasets, process in chunks
    all_matched = []
    all_left_only = []
    all_right_only = []

    # Process left in chunks
    for i in range(0, len(left_df), chunk_size):
        left_chunk = left_df.iloc[i:i+chunk_size]

        # Process right in chunks
        for j in range(0, len(right_df), chunk_size):
            right_chunk = right_df.iloc[j:j+chunk_size]

            matched, left_only, right_only = match_records(left_chunk, right_chunk)

            if not matched.empty:
                all_matched.append(matched)
            if not left_only.empty:
                all_left_only.append(left_only)
            if not right_only.empty:
                all_right_only.append(right_only)

    # Concatenate results
    matched_df = pd.concat(all_matched, ignore_index=True) if all_matched else pd.DataFrame()
    left_only_df = pd.concat(all_left_only, ignore_index=True) if all_left_only else pd.DataFrame()
    right_only_df = pd.concat(all_right_only, ignore_index=True) if all_right_only else pd.DataFrame()

    return matched_df, left_only_df, right_only_df
