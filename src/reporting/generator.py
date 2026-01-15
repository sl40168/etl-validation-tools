"""Report generator for validation results"""
import os
from datetime import datetime
from typing import Dict
from ..validation.groups import ValidationGroup
from .formatter import format_number, format_column_differences, format_side_counts


def generate_report(
    validation_stats: Dict,
    group_info: ValidationGroup,
    validation_date: str,
    output_dir: str = "reports"
) -> str:
    """
    Generate Markdown validation report

    Args:
        validation_stats: Dictionary with validation statistics
        group_info: ValidationGroup object with group details
        validation_date: Business date in YYYYMMDD format
        output_dir: Output directory for reports

    Returns:
        Path to generated report file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    filename = f"validation_{group_info.product_type}_{group_info.tick_type}_{validation_date}.md"
    report_path = os.path.join(output_dir, filename)

    # Get current timestamp
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format validation date for display
    display_date = f"{validation_date[0:4]}-{validation_date[4:6]}-{validation_date[6:8]}"

    # Build report content
    content = f"""# Validation Report: {group_info.product_type}/{group_info.tick_type}

**Validation Date**: {display_date}
**Generated At**: {generated_at}

## Summary

| Metric | Left Instance | Right Instance |
|--------|---------------|----------------|
| Records Retrieved | {format_number(validation_stats['left_retrieved_count'])} | {format_number(validation_stats['right_retrieved_count'])} |

## Match Results

- **Matched Records**: {format_number(validation_stats['matched_count'])}
- **Unmatched Records**: {format_number(validation_stats['unmatched_count'])}

### Unmatched by Column

{format_column_differences(validation_stats['column_differences'])}

### Unmatched by Side

{format_side_counts(validation_stats['left_unmatched_count'], validation_stats['right_unmatched_count'])}
"""

    # Write report to file
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return report_path
