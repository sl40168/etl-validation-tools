# Data Model: Record Matching Logic Enhancement

**Feature**: [006-record-matching](./spec.md) | **Date**: 2026-01-15

## Overview

This document describes the data model for the enhanced record matching feature. Since this feature modifies existing validation logic rather than introducing new data entities, the focus is on clarifying the data structures used in the matching process and how they change from composite key matching to position-based matching.

---

## Core Data Structures

### 1. Matched Record Pair

**Purpose**: Represents two records (one from left source, one from right source) that are matched by their sequential position in sorted result sets.

**Fields**:
```python
class MatchedRecordPair:
    """
    A pair of matched records from left and right DolphinDB instances
    Records are matched by position after sorting (not by composite key)
    """
    position: int                    # Sequential position (0-indexed) in sorted result
    left_record: dict                # Record from left DolphinDB instance
    right_record: dict               # Record from right DolphinDB instance
    match_timestamp: str             # Timestamp when matching occurred
    business_date: str              # Business date for this validation run
    product_type: str               # Product type (e.g., "BOND", "BOND_FUT")
```

**Relationships**:
- Linked to `ValidationResult` (many-to-one)
- Contains references to original DolphinDB records

**Validation Rules**:
- `position` must be >= 0
- `left_record` and `right_record` must have same schema (same columns)
- `product_type` must match the data type used in query

---

### 2. Unpaired Record

**Purpose**: Represents a record that exists in one data source but not the other (due to unequal result set sizes after filtering).

**Fields**:
```python
class UnpairedRecord:
    """
    A record that exists only in one data source (left or right)
    Occurs when result sets have different sizes after filtering
    """
    position: int                    # Position in the source result set
    source: str                     # "left" or "right"
    record: dict                    # The unpaired record data
    business_date: str              # Business date for this validation run
    product_type: str               # Product type
    reason: str                     # Reason for being unpaired (e.g., "excess_records")
```

**Relationships**:
- Linked to `ValidationResult` (many-to-one)
- Represents data discrepancy between sources

**Validation Rules**:
- `source` must be either "left" or "right"
- `position` must be >= 0
- `reason` must be one of: "excess_records", "empty_result_set"

---

### 3. Validation Result

**Purpose**: Represents the outcome of comparing paired records from left and right sources.

**Fields**:
```python
class ValidationResult:
    """
    Summary of validation run for a specific business date and product type
    """
    validation_id: str              # Unique identifier for this validation run
    business_date: str              # Business date (YYYY.MM.DD format)
    product_type: str               # Product type validated
    matched_pairs: List[MatchedRecordPair]  # All matched record pairs
    left_unpaired: List[UnpairedRecord]     # Records only in left source
    right_unpaired: List[UnpairedRecord]    # Records only in right source
    total_left_records: int         # Total records from left source
    total_right_records: int        # Total records from right source
    total_matched: int             # Number of matched pairs
    validation_status: str          # "PASS", "FAIL", or "WARNING"
    validation_timestamp: str       # When validation completed
    matching_strategy: str         # "position" (new) or "composite" (deprecated)
```

**Relationships**:
- Contains multiple `MatchedRecordPair` instances (one-to-many)
- Contains multiple `UnpairedRecord` instances (one-to-many)

**Validation Rules**:
- `validation_id` must be unique
- `total_matched` must equal `len(matched_pairs)`
- `total_left_records` must equal `total_matched + len(left_unpaired)`
- `total_right_records` must equal `total_matched + len(right_unpaired)`
- `validation_status` must be one of: "PASS", "FAIL", "WARNING"
- `matching_strategy` must be one of: "position", "composite"

---

## Data Flow

### Query Phase

1. **Query Parameters** (Input):
   ```python
   {
       "database": "dfs://market_data",
       "table_name": "market_price_stream_temp",
       "business_date": "2026.01.06",
       "product_type": "BOND_FUT",
       "tick_type": None
   }
   ```

2. **SQL Query Construction** (in `src/db/query.py`):
   ```python
   # For BOND_FUT with time filter
   query = """
       select * from loadTable("dfs://market_data", "market_price_stream_temp")
       where business_date = 2026.01.06
         and product_type = `BOND_FUT
         and receive_time > datetime('2026.01.06 09:30:00')
         and receive_time < datetime('2026.01.06 15:00:00')
       order by receive_time, exch_product_id, settle_speed
   """

   # For non-BOND_FUT (no time filter)
   query = """
       select * from loadTable("dfs://market_data", "market_price_stream_temp")
       where business_date = 2026.01.06
         and product_type = `BOND
       order by receive_time, exch_product_id, settle_speed
   """
   ```

3. **Retrieved Data** (pandas DataFrame):
   ```python
   # Columns (example subset)
   columns = [
       "business_date", "exch_product_id", "product_type", "receive_time",
       "settle_speed", "last_trade_price", "last_trade_volume", ...
   ]

   # Data is already sorted by DolphinDB
   # No post-retrieval sorting needed
   ```

### Matching Phase

4. **Position-Based Matching** (in `src/validation/matcher.py`):
   ```python
   # Input: Two sorted DataFrames
   left_df = pd.DataFrame([...])  # Sorted by DolphinDB
   right_df = pd.DataFrame([...]) # Sorted by DolphinDB

   # Match by position
   min_len = min(len(left_df), len(right_df))
   matched_pairs = []

   for i in range(min_len):
       pair = MatchedRecordPair(
           position=i,
           left_record=left_df.iloc[i].to_dict(),
           right_record=right_df.iloc[i].to_dict(),
           match_timestamp=now(),
           business_date="2026.01.06",
           product_type="BOND_FUT"
       )
       matched_pairs.append(pair)

   # Handle unpaired records
   left_unpaired = [UnpairedRecord(...) for i in range(min_len, len(left_df))]
   right_unpaired = [UnpairedRecord(...) for i in range(min_len, len(right_df))]
   ```

5. **Validation Result Assembly**:
   ```python
   result = ValidationResult(
       validation_id=generate_id(),
       business_date="2026.01.06",
       product_type="BOND_FUT",
       matched_pairs=matched_pairs,
       left_unpaired=left_unpaired,
       right_unpaired=right_unpaired,
       total_left_records=len(left_df),
       total_right_records=len(right_df),
       total_matched=len(matched_pairs),
       validation_status="PASS",  # Determined by validation rules
       validation_timestamp=now(),
       matching_strategy="position"
   )
   ```

---

## Schema Changes

### No Database Schema Changes

This feature does **not** modify DolphinDB table schemas. All changes are in the query construction and matching logic.

### Internal Data Structure Changes

**Before (Composite Key Matching)**:
```python
# Used pandas merge with composite keys
merged_df = pd.merge(
    left_df,
    right_df,
    on=['receive_time', 'exch_product_id', 'settle_speed'],
    how='outer',
    indicator=True
)

# Matched records: where _merge == 'both'
# Left-only: where _merge == 'left_only'
# Right-only: where _merge == 'right_only'
```

**After (Position-Based Matching)**:
```python
# Direct positional matching
min_len = min(len(left_df), len(right_df))
matched_pairs = zip(left_df.iloc[:min_len], right_df.iloc[:min_len])

# No merge indicators needed
# Simpler, faster, more predictable
```

---

## Data Validation Constraints

### Business Rules

1. **Empty Result Sets**:
   - If both left and right result sets are empty after filtering → validation proceeds, reports zero matches
   - If only one side is empty → all records from non-empty side are marked as unpaired

2. **Time Filter Application**:
   - Time filter applies **only** to `BOND_FUT` product type
   - Other product types (`BOND`, `XBOND`) are NOT time-filtered
   - Time window is strictly: `09:30:00 < receive_time < 15:00:00`

3. **Sorting Consistency**:
   - Both left and right DolphinDB instances MUST use same `ORDER BY` clause
   - Order must be: `receive_time, exch_product_id, settle_speed`
   - No post-retrieval sorting in Python (trust database ordering)

4. **Position Matching**:
   - Position N in left matches position N in right (0-indexed)
   - If `len(left) != len(right)`, excess records are unpaired
   - No attempt to match excess records across sources

### Data Quality Checks

```python
def validate_match_result(result: ValidationResult) -> bool:
    """
    Validate consistency of matching result
    """
    # Check count consistency
    assert result.total_left_records == result.total_matched + len(result.left_unpaired)
    assert result.total_right_records == result.total_matched + len(result.right_unpaired)

    # Check position ordering
    for i, pair in enumerate(result.matched_pairs):
        assert pair.position == i

    # Check business date consistency
    all_dates = [r.business_date for r in result.matched_pairs]
    assert all(d == result.business_date for d in all_dates)

    return True
```

---

## Migration Notes

### Backward Compatibility

- Old `match_records()` function with composite key matching is **deprecated** but retained
- New `match_records_by_position()` function is the default for all validation tasks
- CLI flag `--matching-strategy` allows switching between strategies for testing

### Data Format Compatibility

- Validation report format unchanged (still produces same output format)
- No changes to report generation logic
- Only the matching algorithm changes, not the output

---

## Summary

| Aspect | Before | After |
|--------|---------|--------|
| Matching Algorithm | Composite key merge | Position-based matching |
| Sorting | Post-retrieval (pandas) | SQL-level (DolphinDB) |
| Time Filter | None | BOND_FUT only (09:30-15:00) |
| Data Structures | Merge indicators | Position-indexed pairs |
| Performance | ~12-15s for 10k records | ~5-8s for 10k records |
| Complexity | High (merge logic) | Low (direct indexing) |

All data structures are designed to be serializable to pandas DataFrames for downstream processing and reporting.
