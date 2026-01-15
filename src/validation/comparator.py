"""Column comparator for precision-aware comparison"""
import pandas as pd
import numpy as np
from typing import List, Tuple, Set


# Volume fields (round to 0 decimals - integer precision)
VOLUME_FIELDS = [
    'last_trade_volume', 'last_trade_turnover', 'last_trade_interest',
    'pre_interest', 'total_volume', 'total_turnover', 'open_interest',
    'bid_0_tradable_volume', 'bid_1_tradable_volume', 'bid_2_tradable_volume',
    'bid_3_tradable_volume', 'bid_4_tradable_volume', 'bid_5_tradable_volume',
    'bid_0_volume', 'bid_1_volume', 'bid_2_volume', 'bid_3_volume',
    'bid_4_volume', 'bid_5_volume',
    'offer_0_tradable_volume', 'offer_1_tradable_volume', 'offer_2_tradable_volume',
    'offer_3_tradable_volume', 'offer_4_tradable_volume', 'offer_5_tradable_volume',
    'offer_0_volume', 'offer_1_volume', 'offer_2_volume', 'offer_3_volume',
    'offer_4_volume', 'offer_5_volume'
]

# Price fields (round to 5 decimals)
PRICE_FIELDS = [
    'last_trade_price', 'pre_close_price', 'pre_settle_price', 'open_price',
    'high_price', 'low_price', 'close_price', 'settle_price', 'upper_limit',
    'lower_limit',
    'bid_0_price', 'bid_1_price', 'bid_2_price', 'bid_3_price',
    'bid_4_price', 'bid_5_price',
    'offer_0_price', 'offer_1_price', 'offer_2_price', 'offer_3_price',
    'offer_4_price', 'offer_5_price'
]

# Yield fields (round to 5 decimals)
YIELD_FIELDS = [
    'last_trade_yield',
    'bid_0_yield', 'bid_1_yield', 'bid_2_yield', 'bid_3_yield',
    'bid_4_yield', 'bid_5_yield',
    'offer_0_yield', 'offer_1_yield', 'offer_2_yield', 'offer_3_yield',
    'offer_4_yield', 'offer_5_yield'
]

# Fields excluded from comparison
EXCLUDED_FROM_COMPARISON = ['create_time', 'store_time', '_merge']


def compare_columns(
    left_record: pd.Series,
    right_record: pd.Series
) -> List[str]:
    """
    Compare 84 columns between two records with precision-aware rounding

    Args:
        left_record: Record from left instance (pd.Series)
        right_record: Record from right instance (pd.Series)

    Returns:
        List of column names where values differ
    """
    # Get common columns (excluding matching keys and excluded fields)
    common_columns = set(left_record.index) & set(right_record.index)

    # Exclude fields that should not be compared
    comparison_columns = [
        col for col in common_columns
        if col not in EXCLUDED_FROM_COMPARISON
    ]

    differences = []

    for col in comparison_columns:
        left_val = left_record[col]
        right_val = right_record[col]

        # Handle NaN values
        if pd.isna(left_val) and pd.isna(right_val):
            continue  # Both NaN, considered equal
        elif pd.isna(left_val) or pd.isna(right_val):
            differences.append(col)  # One is NaN, different
            continue

        # Apply precision-aware comparison
        if col in VOLUME_FIELDS:
            # Round to integer (0 decimals)
            if int(round(left_val, 0)) != int(round(right_val, 0)):
                differences.append(col)
        elif col in PRICE_FIELDS or col in YIELD_FIELDS:
            # Round to 5 decimals
            if round(left_val, 5) != round(right_val, 5):
                differences.append(col)
        else:
            # Exact match for other fields
            if left_val != right_val:
                differences.append(col)

    return differences


def compare_dataframes(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame
) -> dict:
    """
    Compare entire DataFrames and collect column differences

    Args:
        left_df: DataFrame from left instance (matched pairs with '_x' suffix)
        right_df: DataFrame from right instance (matched pairs with '_y' suffix)

    Returns:
        Dictionary with column name -> count of differences
    """
    column_differences = {}

    # Process each matched pair
    for i in range(len(left_df)):
        left_record = left_df.iloc[i]
        right_record = right_df.iloc[i]

        # Clean up column names (remove '_x' and '_y' suffixes)
        left_clean = left_record.copy()
        right_clean = right_record.copy()

        left_clean.index = [idx.replace('_x', '') if idx.endswith('_x') else idx
                          for idx in left_clean.index]
        right_clean.index = [idx.replace('_y', '') if idx.endswith('_y') else idx
                           for idx in right_clean.index]

        # Compare columns
        differences = compare_columns(left_clean, right_clean)

        # Count differences
        for col in differences:
            column_differences[col] = column_differences.get(col, 0) + 1

    return column_differences


def compare_matched_pairs(
    matched_df: pd.DataFrame
) -> dict:
    """
    Compare matched pairs DataFrame and return column differences

    Args:
        matched_df: DataFrame from merge operation with '_x' and '_y' suffixes

    Returns:
        Dictionary with column name -> count of differences
    """
    column_differences = {}

    # Process each matched pair (row)
    for _, row in matched_df.iterrows():
        # Extract left and right records
        left_record = row.filter(like='_x').copy()
        right_record = row.filter(like='_y').copy()

        # Clean up column names
        left_record.index = [idx.replace('_x', '') for idx in left_record.index]
        right_record.index = [idx.replace('_y', '') for idx in right_record.index]

        # Compare columns
        differences = compare_columns(left_record, right_record)

        # Count differences
        for col in differences:
            column_differences[col] = column_differences.get(col, 0) + 1

    return column_differences
