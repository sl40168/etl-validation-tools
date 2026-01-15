# Research: Group-Based Column Validation

**Feature**: [001-group-based-validation](./spec.md) | **Date**: 2026-01-15

## Overview

This document consolidates research findings for implementing group-based column validation. The feature builds on the existing 001-etl-validation implementation, leveraging proven patterns for DolphinDB integration, pandas vectorized operations, and precision-aware comparison. All technical decisions are based on research findings from 001-etl-validation and aligned with the project constitution.

---

## Research Tasks & Decisions

### 1. Group Definition Structure

**Task**: Design data structure for defining validation groups with their required columns

**Decision**: Use Python dict-based configuration with group tuples as keys and column lists as values

**Rationale**:
- Simple and maintainable (no external dependencies)
- Easy to extend by adding new group entries
- Maps directly to CLI `--step` parameter (1, 2, 3)
- Supports rapid lookup during validation

**Implementation Notes**:
```python
VALIDATION_GROUPS = {
    (1, "BOND", "TRADE"): [
        "business_date", "exch_product_id", "product_type", "exchange", "source",
        "settle_speed", "last_trade_price", "last_trade_yield", "last_trade_yield_type",
        "last_trade_volume", "last_trade_turnover", "last_trade_interest",
        "last_trade_side", "level", "status"
    ],
    (2, "BOND", "QUOTE"): [
        # Base columns
        "business_date", "exch_product_id", "product_type", "exchange", "source",
        "settle_speed",
        # Bid/offer levels 0-5 (each level has 10 fields)
        "bid_0_price", "bid_0_yield", "bid_0_yield_type",
        "bid_0_tradable_volume", "bid_0_volume",
        "offer_0_price", "offer_0_yield", "offer_0_yield_type",
        "offer_0_tradable_volume", "offer_0_volume",
        # ... (repeat for levels 1-5)
    ],
    (3, "BOND_FUT", "SNAPSHOT"): [
        # Base columns + trade data
        "business_date", "exch_product_id", "product_type", "exchange", "source",
        "settle_speed", "last_trade_price", "last_trade_yield", "last_trade_yield_type",
        "last_trade_volume", "last_trade_turnover", "last_trade_interest",
        "last_trade_side", "level", "status",
        # Market summary data
        "pre_close_price", "pre_settle_price", "pre_interest",
        "open_price", "high_price", "low_price", "close_price", "settle_price",
        "upper_limit", "lower_limit",
        "total_volume", "total_turnover", "open_interest",
        # Quote data (levels 0-1 only)
        "bid_0_price", "bid_0_yield", "bid_0_yield_type",
        "bid_0_tradable_volume", "bid_0_volume",
        "offer_0_price", "offer_0_yield", "offer_0_yield_type",
        "offer_0_tradable_volume", "offer_0_volume",
        # Level 1 (same fields)
        "bid_1_price", "bid_1_yield", "bid_1_yield_type",
        "bid_1_tradable_volume", "bid_1_volume",
        "offer_1_price", "offer_1_yield", "offer_1_yield_type",
        "offer_1_tradable_volume", "offer_1_volume",
    ],
}

# CLI parameter mapping
STEP_TO_GROUP = {
    1: (1, "BOND", "TRADE"),
    2: (2, "BOND", "QUOTE"),
    3: (3, "BOND_FUT", "SNAPSHOT"),
}
```

**Alternatives Considered**:
- **JSON/YAML configuration file**: Rejected due to additional file I/O overhead and lower maintainability
- **Database table for groups**: Rejected - violates standalone principle, adds complexity
- **Python class hierarchy**: Rejected - over-engineering, simple dict is sufficient

---

### 2. CLI Parameter Extension

**Task**: Extend existing CLI to support `--step` parameter for group selection

**Decision**: Extend existing `argparse` configuration in CLI module

**Rationale**:
- Consistent with existing CLI design
- Simple addition (single optional parameter)
- Integrates seamlessly with existing `--config` and `--date` parameters

**Implementation Notes**:
```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="ETL Data Validation Tool with Group-Based Column Validation"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to INI configuration file with DolphinDB connection details"
    )
    parser.add_argument(
        "--date",
        required=True,
        help="Business date in YYYYMMDD format"
    )
    parser.add_argument(
        "--step",
        type=int,
        choices=[1, 2, 3],
        default=None,
        help="Validation step: 1=BOND TRADE, 2=BOND QUOTE, 3=BOND_FUT SNAPSHOT. "
             "If not specified, runs all steps sequentially."
    )
    return parser.parse_args()
```

**Alternatives Considered**:
- **Separate commands for each group** (e.g., `validate-trade`, `validate-quote`): Rejected - requires code duplication
- **Group name strings** (e.g., `--group BOND_TRADE`): Rejected - integers are simpler and match existing step numbering

---

### 3. Column Validation Logic

**Task**: Implement column presence and type validation for specified groups

**Decision**: pandas DataFrame column checks with configurable validation rules

**Rationale**:
- pandas provides built-in column checking (`df.columns.tolist()`)
- Type checking via `df.dtypes` is straightforward
- Integrates with existing comparison workflow
- Supports custom validation rules per column type

**Implementation Notes**:
```python
from typing import List, Dict, Tuple

class ColumnValidator:
    def __init__(self, required_columns: List[str]):
        self.required_columns = required_columns

    def validate_columns(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Validate DataFrame against required columns.

        Returns:
            Dict with 'missing' and 'extra' column lists
        """
        df_columns = set(df.columns.tolist())
        required_set = set(self.required_columns)

        missing = list(required_set - df_columns)
        extra = list(df_columns - required_set)

        return {
            'missing': sorted(missing),
            'extra': sorted(extra),  # For informational purposes
            'status': 'PASS' if not missing else 'FAIL'
        }

    def validate_types(self, df: pd.DataFrame, type_rules: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Validate data types for required columns.

        Args:
            df: DataFrame to validate
            type_rules: Dict mapping column names to expected types (e.g., 'int', 'float', 'str')

        Returns:
            Dict with 'mismatch' list of columns with wrong types
        """
        mismatches = []

        for col, expected_type in type_rules.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if expected_type == 'int' and 'int' not in actual_type:
                    mismatches.append(f"{col}: expected int, got {actual_type}")
                elif expected_type == 'float' and 'float' not in actual_type:
                    mismatches.append(f"{col}: expected float, got {actual_type}")
                elif expected_type == 'str' and 'object' not in actual_type:
                    mismatches.append(f"{col}: expected str, got {actual_type}")

        return {
            'mismatch': mismatches,
            'status': 'PASS' if not mismatches else 'FAIL'
        }
```

**Alternatives Considered**:
- **Schema validation library (pandera)**: Rejected - additional dependency, overkill for this use case
- **SQL-side validation**: Rejected - requires different queries per group, less flexible

---

### 4. NULL Value Handling in Comparison

**Task**: Implement NULL-aware comparison per clarification (both sides NULL = pass)

**Decision**: Use pandas NA-aware comparison with explicit NULL check

**Rationale**:
- pandas supports NULL/NA values natively
- `df.isna()` provides efficient NULL detection
- Aligns with financial data quality standards
- Matches research.md pattern from 001-etl-validation

**Implementation Notes**:
```python
def compare_with_null_awareness(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    columns: List[str]
) -> Dict[str, int]:
    """
    Compare DataFrames with NULL-aware logic:
    - If both sides are NULL/NA, consider as match
    - If one side is NULL and other has value, consider as difference

    Returns:
        Dict mapping column names to difference counts
    """
    differences = {}

    for col in columns:
        if col in left_df.columns and col in right_df.columns:
            # Both NULL = match
            left_null = left_df[col].isna()
            right_null = right_df[col].isna()
            both_null = left_null & right_null

            # Compare values where not both NULL
            left_vals = left_df[col].where(~both_null)
            right_vals = right_df[col].where(~both_null)

            # Count differences (excluding where both were NULL)
            diff_mask = left_vals.notna() & right_vals.notna() & (left_vals != right_vals)

            # Add cases where one side is NULL and other is not
            one_null_diff = (left_null ^ right_null)

            total_diffs = diff_mask.sum() + one_null_diff.sum()
            differences[col] = total_diffs
        else:
            differences[col] = -1  # Column missing

    return differences
```

**Alternatives Considered**:
- **Simple equality check**: Rejected - doesn't handle NULL correctly
- **Treat NULL as error**: Rejected - conflicts with user clarification

---

### 5. Report Extension for Group-Specific Results

**Task**: Extend Markdown report generation to include group-specific validation results

**Decision**: Add group metadata section and group-specific column validation results

**Rationale**:
- Clear identification of which group was validated
- Separates general results from group-specific column validation
- Maintains consistency with existing report format

**Implementation Notes**:
```python
def generate_group_validation_report(
    group: Tuple[int, str, str],
    column_validation: Dict,
    comparison_results: Dict,
    output_path: str
):
    """
    Generate Markdown report for group-based validation.

    Args:
        group: Tuple (group_id, product_type, message_type)
        column_validation: Result from ColumnValidator.validate_columns()
        comparison_results: Dict with comparison statistics
        output_path: Path to write report file
    """
    group_id, product_type, message_type = group

    report_lines = [
        f"# Group Validation Report: {product_type}/{message_type}\n",
        f"**Group ID**: {group_id}\n",
        f"**Validation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## Column Validation Summary\n",
        f"**Status**: {column_validation['status']}\n",
    ]

    if column_validation['missing']:
        report_lines.append("### Missing Columns\n")
        for col in column_validation['missing']:
            report_lines.append(f"- {col}\n")

    if column_validation['extra']:
        report_lines.append("### Extra Columns (Ignored)\n")
        for col in column_validation['extra']:
            report_lines.append(f"- {col}\n")

    report_lines.append("\n## Comparison Results\n")
    # ... add comparison results section

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(report_lines)
```

**Alternatives Considered**:
- **Separate report files per group**: Rejected - user may want single consolidated view
- **JSON output only**: Rejected - constitution requires Markdown for human readability

---

### 6. Chunked Processing for Large Datasets

**Task**: Reuse and adapt chunked processing pattern for 2M records per group

**Decision**: Use existing chunking logic from 001-etl-validation (100k rows/chunk)

**Rationale**:
- Proven pattern with 3-5 minute performance for 2M records
- Memory efficient (stays under 2GB limit)
- Aligns with research.md findings from 001-etl-validation

**Implementation Notes**:
```python
CHUNK_SIZE = 100000  # 100k rows per chunk

def process_group_in_chunks(
    left_connection,
    right_connection,
    group: Tuple[int, str, str],
    date_str: str
):
    """
    Process validation for a group using chunked processing.

    Args:
        left_connection: DolphinDB session for left instance
        right_connection: DolphinDB session for right instance
        group: Tuple (group_id, product_type, message_type)
        date_str: Business date in YYYYMMDD format
    """
    group_id, product_type, message_type = group

    # Build query filters
    filters = f"product_type == '{product_type}' AND message_type == '{message_type}'"

    # Query total row count
    total_query = f"SELECT count(*) FROM market_data WHERE business_date == date('{date_str}') AND {filters}"
    total_rows = left_connection.run(total_query).iloc[0, 0]

    # Process in chunks
    all_differences = {}
    processed = 0

    for offset in range(0, total_rows, CHUNK_SIZE):
        # Fetch chunk
        left_chunk = fetch_chunk(left_connection, date_str, filters, offset, CHUNK_SIZE)
        right_chunk = fetch_chunk(right_connection, date_str, filters, offset, CHUNK_SIZE)

        # Match and compare
        matched = pd.merge(left_chunk, right_chunk, on=['receive_time', 'exch_product_id', 'settle_speed'], how='inner')

        # Validate columns
        validator = ColumnValidator(VALIDATION_GROUPS[group])
        col_validation = validator.validate_columns(left_chunk)

        # Compare with NULL awareness
        diff_results = compare_with_null_awareness(left_chunk, right_chunk, validator.required_columns)

        # Aggregate results
        for col, count in diff_results.items():
            if col not in all_differences:
                all_differences[col] = 0
            all_differences[col] += count

        processed += len(left_chunk)
        print(f"Processed {processed}/{total_rows} rows...")

    return col_validation, all_differences
```

**Alternatives Considered**:
- **Full in-memory processing**: Rejected - exceeds 2GB memory limit for 2M records
- **Database-side aggregation**: Rejected - requires cross-instance queries, violates architecture

---

## Summary of Resolved Decisions

All technical decisions are resolved, building on proven patterns from 001-etl-validation:

| Technical Area | Decision | Key Dependencies |
|----------------|------------|------------------|
| Group Definition | Python dict with tuple keys and column lists | None (stdlib) |
| CLI Parameter | Extend argparse with --step (1-3) | argparse (stdlib) |
| Column Validation | pandas DataFrame column checks | pandas |
| NULL Handling | pandas NA-aware comparison | pandas |
| Report Generation | Extend Markdown with group metadata | None (stdlib) |
| Chunked Processing | Reuse 100k row/chunk pattern | pandas |

**No new external dependencies required** - leverages existing stack from 001-etl-validation.

---

## Performance Estimates

Based on 001-etl-validation research and chunked processing (100k rows/chunk):

| Operation | Dataset Size | Chunk Size | Estimated Time |
|------------|---------------|------------|---------------|
| Column validation | 2M rows | N/A | <1 second |
| Data retrieval (2 instances) | 2M rows | 100k | 60-120 seconds |
| Record matching | 2M rows | 100k | 60-120 seconds |
| Column comparison (NULL-aware) | 2M rows | 100k | 60-120 seconds |
| Report generation | N/A | N/A | <5 seconds |
| **Total per group** | 2M rows | 100k | **3-5 minutes** |
| **All 3 groups** | 2M × 3 | 100k | **9-15 minutes** |

**Note**: Times align with SC-002 (3-5 minutes per group).

---

## Next Steps

With all research complete and decisions made, proceed to **Phase 1: Design & Contracts**:

1. Generate `data-model.md` with entity definitions and relationships
2. Generate `contracts/` directory with CLI interface specifications
3. Generate `quickstart.md` with setup and usage instructions
4. Update agent context with technology stack
5. Re-evaluate Constitution Check post-design
