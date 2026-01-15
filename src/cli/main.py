"""CLI entry point for ETL validation tool"""
import argparse
import sys
import pandas as pd
from datetime import datetime
from typing import Optional

from ..config.loader import load_config, validate_config, DolphinDBConfig
from ..db.connection import ConnectionWrapper, verify_connection
from ..utils.date_helpers import parse_date, parse_and_format_date
from ..validation.groups import VALIDATION_GROUPS, get_validation_groups

VERSION = "1.0.0"


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for CLI

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="DolphinDB ETL Data Validation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m etl_validator --config config/db_connections.ini --date 20260115
  python -m etl_validator --config config/db_connections.ini --date 20260115 --step 1

Validation Steps:
  1  BOND TRADE data
  2  BOND QUOTE data
  3  BOND_FUT SNAPSHOT data
        """
    )

    parser.add_argument(
        '--config',
        required=True,
        help='Path to INI configuration file with DolphinDB connection details'
    )

    parser.add_argument(
        '--date',
        required=True,
        help='Business date to validate (format: YYYYMMDD)'
    )

    parser.add_argument(
        '--step',
        type=int,
        choices=[1, 2, 3],
        help='Optional: Execute only validation step N (1=BOND TRADE, 2=BOND QUOTE, 3=BOND_FUT SNAPSHOT)'
    )

    parser.add_argument(
        '--matching-strategy',
        choices=['position', 'composite'],
        default='position',
        help='Strategy for matching records from left/right sources (default: position). '
             'Use "position" for pre-sorted data, "composite" for backward compatibility.'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'etl-validator version {VERSION}'
    )

    return parser


def validate_arguments(args: argparse.Namespace) -> None:
    """
    Validate command-line arguments

    Args:
        args: Parsed arguments

    Raises:
        ValueError: If arguments are invalid
    """
    # Validate date format
    try:
        parse_date(args.date)
    except ValueError as e:
        raise ValueError(f"Invalid date: {e}")

    # Validate step (if provided)
    if args.step is not None:
        if args.step not in [1, 2, 3]:
            raise ValueError(f"Invalid step number: {args.step}. Must be 1, 2, or 3")


def load_and_validate_config(config_path: str) -> dict:
    """
    Load and validate configuration file

    Args:
        config_path: Path to configuration file

    Returns:
        Validated configuration dictionary

    Raises:
        FileNotFoundError: If config file not found
        ValueError: If config is invalid
    """
    try:
        config = load_config(config_path)
        return validate_config(config)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except ValueError as e:
        raise ValueError(f"Invalid configuration: {e}")


def verify_connections(config_dict: dict) -> None:
    """
    Verify connections to both DolphinDB instances

    Args:
        config_dict: Configuration dictionary with 'left' and 'right' keys

    Raises:
        Exception: If connection test fails
    """
    try:
        verify_connection(config_dict['left'])
        verify_connection(config_dict['right'])
    except Exception as e:
        raise Exception(f"Connection test failed: {e}")


def validate_step(
    config_dict: dict,
    validation_date: str,
    step_number: int,
    product_type: str,
    tick_type: str,
    description: str
) -> dict:
    """
    Execute validation for a single step

    Args:
        config_dict: Configuration dictionary
        validation_date: Business date in YYYY.MM.DD format
        step_number: Step number (1, 2, or 3)
        product_type: Product type
        tick_type: Tick type
        description: Step description

    Returns:
        Dictionary with validation statistics

    Raises:
        Exception: If validation fails
    """
    from ..db.query import retrieve_data
    from ..validation.matcher import match_records
    from ..validation.comparator import compare_matched_pairs
    from ..reporting.generator import generate_report
    from ..validation.groups import ValidationGroup

    print(f"[Step {step_number}/3] Validating {product_type}/{tick_type}...")
    print(f"  Description: {description}")

    # Initialize statistics
    stats = {
        'step': step_number,
        'product_type': product_type,
        'tick_type': tick_type,
        'left_retrieved_count': 0,
        'right_retrieved_count': 0,
        'matched_count': 0,
        'unmatched_count': 0,
        'column_differences': {},
        'left_unmatched_count': 0,
        'right_unmatched_count': 0
    }

    # Retrieve data from left instance
    left_chunks = list(retrieve_data(
        config_dict['left'],
        config_dict['left'].database,
        'market_price',
        validation_date,
        product_type,
        tick_type
    ))

    # Retrieve data from right instance
    right_chunks = list(retrieve_data(
        config_dict['right'],
        config_dict['right'].database,
        'market_price',
        validation_date,
        product_type,
        tick_type
    ))

    # Aggregate retrieved counts
    left_df = pd.concat(left_chunks, ignore_index=True) if left_chunks else pd.DataFrame()
    right_df = pd.concat(right_chunks, ignore_index=True) if right_chunks else pd.DataFrame()

    stats['left_retrieved_count'] = len(left_df)
    stats['right_retrieved_count'] = len(right_df)

    # Match records (using chunked processing)
    matched, left_only, right_only = match_records(left_df, right_df)

    stats['matched_count'] = len(matched)
    stats['unmatched_count'] = len(left_only) + len(right_only)
    stats['left_unmatched_count'] = len(left_only)
    stats['right_unmatched_count'] = len(right_only)

    # Compare columns for matched pairs
    stats['column_differences'] = compare_matched_pairs(matched)

    # Generate report
    group_info = ValidationGroup(
        step=step_number,
        product_type=product_type,
        tick_type=tick_type,
        description=description
    )

    # Extract validation_date in YYYYMMDD format from SQL date (YYYY.MM.DD)
    validation_date_ymd = validation_date.replace('.', '')

    report_path = generate_report(
        stats,
        group_info,
        validation_date_ymd,
        output_dir='reports'
    )

    # Print progress
    print(f"  Retrieved: {stats['left_retrieved_count']:,} records from left, "
          f"{stats['right_retrieved_count']:,} records from right")
    print(f"  Matched: {stats['matched_count']:,} pairs")
    print(f"  Unmatched: {stats['unmatched_count']:,} records")
    print(f"  Report generated: {report_path}")

    return stats


def main() -> int:
    """
    Main entry point for CLI

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()

    try:
        args = parser.parse_args()
        validate_arguments(args)
    except SystemExit:
        # --help or --version was called
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    # Load configuration
    try:
        config_dict = load_and_validate_config(args.config)
        print(f"Configuration loaded from: {args.config}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Test connections
    try:
        verify_connections(config_dict)
        print("Connection tests passed")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 3

    # Format date for SQL queries
    try:
        formatted_date = parse_and_format_date(args.date)
    except ValueError as e:
        print(f"Error: Invalid date format: {e}", file=sys.stderr)
        return 2

    print(f"Starting validation for date: {args.date}")
    print()

    # Get validation groups
    try:
        groups = get_validation_groups(args.step)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    # Execute validation for each group
    results = []
    for group in groups:
        try:
            stats = validate_step(
                config_dict,
                formatted_date,
                group.step,
                group.product_type,
                group.tick_type,
                group.description
            )
            results.append(stats)
        except Exception as e:
            print(f"Error: Validation failed for step {group.step}: {e}", file=sys.stderr)
            return 5

    print()
    print("Validation complete.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
