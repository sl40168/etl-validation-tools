"""Report statistics formatting utilities"""
from typing import Dict


def format_number(value: int) -> str:
    """
    Format integer with thousands separators

    Args:
        value: Integer value to format

    Returns:
        Formatted string with commas (e.g., "45,234")
    """
    return "{:,}".format(value)


def format_column_differences(column_differences: Dict[str, int]) -> str:
    """
    Convert column differences dictionary to Markdown table

    Args:
        column_differences: Dictionary of column name -> count of differences

    Returns:
        Markdown table string
    """
    if not column_differences:
        return "No column differences found."

    # Sort by count descending
    sorted_diffs = sorted(column_differences.items(), key=lambda x: x[1], reverse=True)

    # Build table
    lines = []
    lines.append("| Column Name | Differences |")
    lines.append("|-------------|-------------|")

    for column, count in sorted_diffs:
        lines.append(f"| {column} | {format_number(count)} |")

    return "\n".join(lines)


def format_side_counts(left_unmatched: int, right_unmatched: int) -> str:
    """
    Format side-specific unmatched counts as Markdown table

    Args:
        left_unmatched: Count of unmatched records in left instance
        right_unmatched: Count of unmatched records in right instance

    Returns:
        Markdown table string
    """
    lines = []
    lines.append("| Side | Records |")
    lines.append("|------|---------|")
    lines.append(f"| Left Only | {format_number(left_unmatched)} |")
    lines.append(f"| Right Only | {format_number(right_unmatched)} |")

    return "\n".join(lines)
