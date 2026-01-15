# API Contracts: Record Matching Logic Enhancement

**Feature**: [006-record-matching](../spec.md) | **Date**: 2026-01-15

## Overview

This document describes the internal API contracts for the enhanced record matching logic. Since this is a CLI application with no external REST/GraphQL APIs, the contracts focus on Python function interfaces between modules.

---

## Module: `src/db/query.py`

### Function: `execute_query()`

Execute SQL query with sorting and optional time filtering.

```python
def execute_query(
    session: Session,
    database: str,
    table_name: str,
    business_date: str,
    product_type: Optional[str] = None,
    tick_type: Optional[str] = None,
    chunk_size: int = CHUNK_SIZE
) -> pd.DataFrame
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `session` | `Session` | Yes | DolphinDB session object |
| `database` | `str` | Yes | Database name (e.g., "dfs://market_data") |
| `table_name` | `str` | Yes | Table name (e.g., "market_price_stream_temp") |
| `business_date` | `str` | Yes | Business date in YYYY.MM.DD format |
| `product_type` | `Optional[str]` | No | Product type filter (e.g., "BOND_FUT") |
| `tick_type` | `Optional[str]` | No | Tick type filter |
| `chunk_size` | `int` | No | Number of records per chunk (default: 100000) |

**Returns**:
- `pd.DataFrame`: Query results, sorted by `receive_time, exch_product_id, settle_speed`

**Behavior**:
1. Builds WHERE clause with filters
2. Adds time filter if `product_type == "BOND_FUT"` (09:30:00-15:00:00)
3. Adds `ORDER BY receive_time, exch_product_id, settle_speed` clause
4. Executes query via DolphinDB session
5. Returns sorted DataFrame

**Raises**:
- `Exception`: If query execution fails

---

### Function: `execute_query_with_chunks()`

Execute query with chunking for memory management.

```python
def execute_query_with_chunks(
    session: Session,
    database: str,
    table_name: str,
    business_date: str,
    product_type: Optional[str] = None,
    tick_type: Optional[str] = None,
    chunk_size: int = CHUNK_SIZE
)
```

**Parameters**: Same as `execute_query()`

**Yields**:
- `pd.DataFrame`: Single DataFrame with all query results

**Behavior**: Same as `execute_query()` but uses generator pattern

**Raises**:
- `Exception`: If query execution fails

---

### Function: `retrieve_data()`

Retrieve data with automatic connection management.

```python
def retrieve_data(
    config: DolphinDBConfig,
    database: str,
    table_name: str,
    business_date: str,
    product_type: Optional[str] = None,
    tick_type: Optional[str] = None,
    chunk_size: int = CHUNK_SIZE
)
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `config` | `DolphinDBConfig` | Yes | DolphinDB connection configuration |
| `database` | `str` | Yes | Database name |
| `table_name` | `str` | Yes | Table name |
| `business_date` | `str` | Yes | Business date in YYYY.MM.DD format |
| `product_type` | `Optional[str]` | No | Product type filter |
| `tick_type` | `Optional[str]` | No | Tick type filter |
| `chunk_size` | `int` | No | Records per chunk (default: 100000) |

**Yields**:
- `pd.DataFrame`: Query result chunks

**Behavior**:
1. Establishes connection via `ConnectionWrapper`
2. Executes query with sorting and filtering
3. Yields result chunks
4. Automatically closes connection

**Raises**: Exception from query execution

---

## Module: `src/validation/matcher.py`

### Function: `match_records_by_position()` (NEW)

Match records by sequential position (NEW FEATURE).

```python
def match_records_by_position(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    chunk_size: int = CHUNK_SIZE
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `left_df` | `pd.DataFrame` | Yes | DataFrame from left DolphinDB (sorted) |
| `right_df` | `pd.DataFrame` | Yes | DataFrame from right DolphinDB (sorted) |
| `chunk_size` | `int` | No | Records per chunk (default: 100000) |

**Returns**:
- `Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]`:
  - `matched_pairs`: DataFrame with concatenated left+right records (MultiIndex columns)
  - `left_only`: Records only in left DataFrame (excess after matching)
  - `right_only`: Records only in right DataFrame (excess after matching)

**Behavior**:
1. Handle empty DataFrames (return empty results)
2. Determine min length for matching
3. Match records by position (0 to min_len-1)
4. Identify unpaired records (excess beyond min_len)
5. Return matched pairs and unpaired records

**Raises**:
- `ValueError`: If DataFrames have different schemas

---

### Function: `match_records()` (DEPRECATED)

Match records using composite key (DEPRECATED - kept for backward compatibility).

```python
def match_records(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    chunk_size: int = CHUNK_SIZE
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
```

**Parameters**: Same as `match_records_by_position()`

**Returns**: Same as `match_records_by_position()`

**Behavior**: Uses pandas merge on composite key `[receive_time, exch_product_id, settle_speed]`

**Deprecation Notice**:
```python
"""
DEPRECATED: Use match_records_by_position() for new validation tasks
This function is maintained for backward compatibility only
"""
```

---

### Function: `match_records_chunked()` (DEPRECATED)

Chunked processing for composite key matching (DEPRECATED).

```python
def match_records_chunked(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    chunk_size: int = CHUNK_SIZE
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
```

**Parameters**: Same as `match_records_by_position()`

**Returns**: Same as `match_records_by_position()`

**Behavior**: Processes data in chunks using deprecated `match_records()`

**Deprecation Notice**: Same as `match_records()`

---

### Function: `match_records_by_position_chunked()` (NEW)

Chunked processing for position-based matching.

```python
def match_records_by_position_chunked(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    chunk_size: int = CHUNK_SIZE
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
```

**Parameters**: Same as `match_records_by_position()`

**Returns**: Same as `match_records_by_position()`

**Behavior**:
1. If datasets are small enough (<= chunk_size), process all at once
2. Otherwise, process in chunks using `match_records_by_position()`
3. Concatenate results

**Raises**: Same as `match_records_by_position()`

---

## Module: `src/utils/date_helpers.py`

### Function: `construct_time_range()` (NEW)

Construct datetime strings for time range filtering.

```python
def construct_time_range(
    business_date: str,
    start_time: str = "09:30:00",
    end_time: str = "15:00:00"
) -> Tuple[str, str]
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `business_date` | `str` | Yes | Date in YYYY.MM.DD format |
| `start_time` | `str` | No | Start time in HH:MM:SS format (default: "09:30:00") |
| `end_time` | `str` | No | End time in HH:MM:SS format (default: "15:00:00") |

**Returns**:
- `Tuple[str, str]`: `(start_datetime, end_datetime)` strings ready for SQL

**Behavior**:
```python
# Returns:
start_dt = "datetime('2026.01.06 09:30:00')"
end_dt = "datetime('2026.01.06 15:00:00')"
```

**Raises**:
- `ValueError`: If date/time format is invalid

---

## Module: `src/cli/main.py`

### CLI Parameter: `--matching-strategy` (NEW)

Select record matching strategy.

```python
parser.add_argument(
    '--matching-strategy',
    choices=['position', 'composite'],
    default='position',
    help='Strategy for matching records from left/right sources (default: position)'
)
```

**Values**:
- `position` (default): Match by sequential position (NEW)
- `composite` (deprecated): Match by composite key

**Usage**:
```bash
# Use new position-based matching (default)
python -m src.cli.main --config config.ini --date 2026.01.06

# Use old composite key matching (deprecated)
python -m src.cli.main --config config.ini --date 2026.01.06 --matching-strategy composite
```

---

## Data Structures

### DataFrame Schema (Retrieved Data)

**Columns** (example subset):

| Column | Type | Description |
|--------|------|-------------|
| `business_date` | str | Business date (YYYY.MM.DD) |
| `exch_product_id` | str | Exchange product ID |
| `product_type` | str | Product type (BOND, BOND_FUT, etc.) |
| `receive_time` | datetime | Reception timestamp (sorted column 1) |
| `settle_speed` | str | Settlement speed (sorted column 3) |
| `last_trade_price` | float | Last trade price |
| `last_trade_volume` | int | Last trade volume |
| ... | ... | ... |

**Sorting**: Records are sorted by `receive_time, exch_product_id, settle_speed` (ascending)

---

### Matched DataFrame Schema

**MultiIndex Columns** (after concatenation):

```
('left', 'business_date')      | ('right', 'business_date')
('left', 'exch_product_id')    | ('right', 'exch_product_id')
('left', 'receive_time')        | ('right', 'receive_time')
...
```

**Structure**:
- Each row represents a matched pair
- Left columns have prefix `('left', ...)`
- Right columns have prefix `('right', ...)`

---

## Error Handling

### Query Execution Errors

```python
try:
    result_df = session.run(query)
except Exception as e:
    raise Exception(f"Query execution failed: {e}")
```

**Error Messages**:
- `"Query execution failed: <details>"`

---

### Matching Errors

```python
if left_df.columns != right_df.columns:
    raise ValueError("Left and right DataFrames have different schemas")
```

**Error Messages**:
- `"Left and right DataFrames have different schemas"`
- `"DataFrame missing required matching keys"` (deprecated)

---

### Date/Time Errors

```python
try:
    # Validate date format
    datetime.strptime(business_date, "%Y.%m.%d")
except ValueError:
    raise ValueError(f"Invalid business date format: {business_date}")
```

**Error Messages**:
- `"Invalid business date format: <date>"`

---

## Testing Contracts

### Unit Test: `test_query_with_order_by()`

```python
def test_query_with_order_by():
    """Verify ORDER BY clause is added to queries"""
    # Setup: Create mock session
    # Execute: execute_query(session, db, table, date)
    # Assert: Query contains "order by receive_time, exch_product_id, settle_speed"
```

---

### Unit Test: `test_time_filter_for_bond_fut()`

```python
def test_time_filter_for_bond_fut():
    """Verify time filter is added for BOND_FUT"""
    # Setup: Mock session with BOND_FUT product type
    # Execute: execute_query(session, db, table, date, product_type="BOND_FUT")
    # Assert: Query contains time range filter
```

---

### Unit Test: `test_position_based_matching()`

```python
def test_position_based_matching():
    """Verify records are matched by position"""
    # Setup: Create two sorted DataFrames
    # Execute: match_records_by_position(left_df, right_df)
    # Assert: Record 0 in left matches record 0 in right
```

---

### Integration Test: `test_full_validation_flow()`

```python
def test_full_validation_flow():
    """Verify end-to-end validation with new matching logic"""
    # Setup: Configure validation task
    # Execute: Run validation with matching-strategy=position
    # Assert: Records are sorted, filtered, and matched correctly
```

---

## Versioning

### Version 2.0.0 (006-record-matching)

**Breaking Changes**:
- Default matching strategy changed from `composite` to `position`
- `match_records()` and `match_records_chunked()` deprecated

**New Features**:
- Added `match_records_by_position()` function
- Added `match_records_by_position_chunked()` function
- Added `--matching-strategy` CLI parameter
- Added `construct_time_range()` helper function

**Modifications**:
- `execute_query()` now adds `ORDER BY` clause
- `execute_query()` now filters BOND_FUT by time range

---

## Migration Guide

### For Existing Code

**Before** (v1.0.0):
```python
from src.validation.matcher import match_records

matched, left_only, right_only = match_records(left_df, right_df)
```

**After** (v2.0.0):
```python
from src.validation.matcher import match_records_by_position

matched, left_only, right_only = match_records_by_position(left_df, right_df)
```

### Backward Compatibility

Old functions are still available (deprecated):

```python
# Still works, but generates deprecation warning
from src.validation.matcher import match_records

matched, left_only, right_only = match_records(left_df, right_df)
```

---

## Summary

| Module | New Functions | Modified Functions | Deprecated Functions |
|--------|---------------|-------------------|---------------------|
| `src/db/query.py` | None | `execute_query()`, `execute_query_with_chunks()`, `retrieve_data()` | None |
| `src/validation/matcher.py` | `match_records_by_position()`, `match_records_by_position_chunked()` | None | `match_records()`, `match_records_chunked()` |
| `src/utils/date_helpers.py` | `construct_time_range()` | None | None |
| `src/cli/main.py` | `--matching-strategy` parameter | None | None |

All API contracts are designed to be backward compatible while providing a clear migration path to the new position-based matching logic.
