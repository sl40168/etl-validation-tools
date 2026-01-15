# Research: Record Matching Logic Enhancement

**Feature**: [006-record-matching](./spec.md) | **Date**: 2026-01-15

## Overview

This document consolidates research findings for implementing position-based record matching with SQL-level sorting and time-based filtering for BOND_FUT data. The feature modifies existing ETL validation tools to simplify matching logic while improving accuracy for time-series financial data. All technical decisions are based on existing codebase analysis and aligned with project constitution.

---

## Research Tasks & Decisions

### 1. SQL-Level Sorting in DolphinDB

**Task**: Determine how to implement `ORDER BY receive_time, exch_product_id, settle_speed` in DolphinDB queries

**Decision**: Modify query builder in `src/db/query.py` to include `ORDER BY` clause in SQL statements

**Rationale**:
- Sorting at database level reduces data transfer overhead
- DolphinDB natively supports `ORDER BY` for efficient sorting
- Ensures consistent ordering across both instances before data retrieval
- Eliminates need for post-retrieval sorting in Python

**Implementation Notes**:
```python
# In execute_query() and execute_query_with_chunks()
# Add ORDER BY to query construction
where_clause = " and ".join(where_clauses)
order_by_clause = "order by receive_time, exch_product_id, settle_speed"
query = f"select * from loadTable(\"{database}\", \"{table_name}\") where {where_clause} {order_by_clause}"
```

**Alternatives Considered**:
- **Post-retrieval sorting in pandas**: Rejected - inefficient for large datasets, doubles processing time
- **External sorting service**: Rejected - violates standalone principle, adds complexity
- **No sorting (rely on insertion order)**: Rejected - unreliable, violates spec requirement

---

### 2. Time-Based Filtering for BOND_FUT

**Task**: Implement time range filter for BOND_FUT data (09:30:00 to 15:00:00)

**Decision**: Add conditional time filter in query builder when `product_type == 'BOND_FUT'`

**Rationale**:
- Filter at database level reduces data retrieval volume
- Consistent with SQL-level sorting approach
- Easy to implement with DolphinDB datetime functions
- Applies only to BOND_FUT as per spec (FR-005)

**Implementation Notes**:
```python
# In execute_query() and execute_query_with_chunks()
where_clauses = [f"business_date = {business_date}"]

if product_type is not None:
    where_clauses.append(f"product_type = `{product_type}")

# Add time filter for BOND_FUT
if product_type == "BOND_FUT":
    time_filter = f"receive_time > datetime('{business_date} 09:30:00') and receive_time < datetime('{business_date} 15:00:00')"
    where_clauses.append(time_filter)
```

**Date Helper Function**:
```python
# In src/utils/date_helpers.py
def construct_time_range(business_date: str, start_time: str = "09:30:00", end_time: str = "15:00:00") -> Tuple[str, str]:
    """
    Construct datetime strings for time range filtering

    Args:
        business_date: Date in YYYY.MM.DD format
        start_time: Start time in HH:MM:SS format
        end_time: End time in HH:MM:SS format

    Returns:
        Tuple of (start_datetime, end_datetime) strings
    """
    start_dt = f"datetime('{business_date} {start_time}')"
    end_dt = f"datetime('{business_date} {end_time}')"
    return start_dt, end_dt
```

**Alternatives Considered**:
- **Post-retrieval filtering in Python**: Rejected - retrieves unnecessary data, inefficient
- **Configuration-driven time ranges**: Rejected - over-engineering, spec has fixed times
- **Skip time filter entirely**: Rejected - violates spec requirement FR-002

---

### 3. Position-Based Matching Logic

**Task**: Replace composite key matching with position-based (sequential) matching

**Decision**: Simplify `src/validation/matcher.py` to match records by index instead of composite keys

**Rationale**:
- Records are already sorted in DolphinDB, so position matching is natural
- Eliminates need for complex merge operations
- Reduces memory overhead (no merge indicators needed)
- Simplifies code and improves maintainability

**Implementation Notes**:
```python
# New function in src/validation/matcher.py
def match_records_by_position(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    chunk_size: int = CHUNK_SIZE
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Match records from two DataFrames by sequential position

    Args:
        left_df: DataFrame from left DolphinDB instance (sorted)
        right_df: DataFrame from right DolphinDB instance (sorted)
        chunk_size: Number of records to process per chunk

    Returns:
        Tuple of (matched_pairs, left_only, right_only):
        - matched_pairs: DataFrame with matched records (by position)
        - left_only: Records only in left DataFrame (excess after matching)
        - right_only: Records only in right DataFrame (excess after matching)
    """
    # Handle empty DataFrames
    if left_df.empty and right_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Determine min length for matching
    min_len = min(len(left_df), len(right_df))

    if min_len == 0:
        # One side is empty, return as unpaired
        return pd.DataFrame(), left_df.copy(), right_df.copy()

    # Match by position (0 to min_len-1)
    matched_left = left_df.iloc[:min_len].copy()
    matched_right = right_df.iloc[:min_len].copy()

    # Reset index for clean concatenation
    matched_left = matched_left.reset_index(drop=True)
    matched_right = matched_right.reset_index(drop=True)

    # Combine matched pairs
    matched_pairs = pd.concat([matched_left, matched_right], axis=1)

    # Identify unpaired records
    left_only = left_df.iloc[min_len:].copy() if len(left_df) > min_len else pd.DataFrame()
    right_only = right_df.iloc[min_len:].copy() if len(right_df) > min_len else pd.DataFrame()

    return matched_pairs, left_only, right_only
```

**Handling Column Name Conflicts**:
```python
# When concatenating, add suffixes to distinguish left/right columns
matched_pairs = pd.concat(
    [matched_left, matched_right],
    axis=1,
    keys=['left', 'right']
)
# This creates MultiIndex columns: ('left', 'col1'), ('right', 'col1')
```

**Alternatives Considered**:
- **Keep composite key matching**: Rejected - violates spec requirement FR-003
- **Hybrid approach (key + position)**: Rejected - adds complexity without benefit
- **Fuzzy matching algorithms**: Rejected - over-engineering, not needed for sorted data

---

### 4. Backward Compatibility Strategy

**Task**: Ensure changes don't break existing validation workflows

**Decision**: Keep old matching functions as deprecated for gradual migration

**Rationale**:
- Allows testing of new logic without breaking existing flows
- Provides rollback path if issues arise
- Enables A/B testing of old vs new matching

**Implementation Notes**:
```python
# Keep existing match_records() and match_records_chunked()
# Add new match_records_by_position() and match_records_by_position_chunked()

# Deprecation notice
def match_records(...):
    """
    DEPRECATED: Use match_records_by_position() for new validation tasks
    This function is maintained for backward compatibility only
    """
    # ... existing implementation ...
```

**CLI Flag for Matching Strategy**:
```python
# In CLI parser, add optional flag
parser.add_argument(
    '--matching-strategy',
    choices=['position', 'composite'],
    default='position',
    help='Record matching strategy (default: position)'
)
```

**Alternatives Considered**:
- **Immediate replacement (no backward compat)**: Rejected - risky, breaks existing workflows
- **Separate module for new logic**: Rejected - increases codebase complexity
- **Feature flag system**: Rejected - over-engineering for this use case

---

### 5. Performance Optimization

**Task**: Ensure position-based matching meets <10 second target for 10,000 records

**Decision**: Leverage pandas vectorized operations and efficient indexing

**Rationale**:
- `iloc[]` indexing is O(1) for position access
- `pd.concat()` is highly optimized for DataFrame operations
- No merge operations reduce overhead significantly

**Benchmark Results (Expected)**:
- Composite key matching (old): ~12-15 seconds for 10,000 records
- Position-based matching (new): ~5-8 seconds for 10,000 records
- Memory usage: ~30% reduction (no merge indicators)

**Implementation Notes**:
```python
# Use iloc[] for efficient position-based access
matched_left = left_df.iloc[:min_len].copy()  # O(min_len)

# Vectorized concatenation
matched_pairs = pd.concat([matched_left, matched_right], axis=1)  # O(min_len * num_columns)
```

**Alternatives Considered**:
- **Caching matched results**: Rejected - adds complexity, data is already in memory
- **Parallel processing**: Rejected - pandas operations already vectorized, threading adds overhead
- **NumPy arrays instead of DataFrames**: Rejected - breaks existing validation pipeline

---

## Summary of Technical Decisions

| Area | Decision | Impact |
|------|----------|--------|
| Sorting | SQL-level `ORDER BY` in DolphinDB | Reduces data transfer, ensures consistency |
| Time Filter | Conditional WHERE clause for BOND_FUT | Filters at source, improves efficiency |
| Matching | Position-based by index | Simplifies logic, reduces complexity |
| Backward Compat | Keep deprecated functions | Safe migration path |
| Performance | Pandas vectorized operations | Meets <10 second target |

## Unresolved Questions

None - all technical decisions resolved.

---

## Next Steps

Proceed to Phase 1 (Design & Contracts) to create data model documentation and update agent context.
