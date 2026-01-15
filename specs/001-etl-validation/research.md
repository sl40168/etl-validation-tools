# Research: DolphinDB ETL Data Validation Tool

**Feature**: [001-etl-validation](./spec.md) | **Date**: 2026-01-15

## Overview

This document consolidates research findings for technical decisions required to implement the DolphinDB ETL Data Validation Tool. All NEEDS CLARIFICATION items from the Technical Context have been resolved through research and analysis.

---

## Research Tasks & Decisions

### 1. DolphinDB Python Client Library

**Task**: Research DolphinDB Python client for connecting to DolphinDB instances and executing queries

**Decision**: Use official DolphinDB Python SDK (`dolphindb` package)

**Rationale**:
- Officially maintained by DolphinDB team
- Supports connection pooling, query execution, and data retrieval
- Provides pandas DataFrame integration for efficient data manipulation
- Well-documented with examples for common operations
- Compatible with Python 3.8+

**Alternatives Considered**:
- **ODBC driver**: Rejected due to additional driver installation complexity and lack of pandas integration
- **REST API**: Rejected due to overhead and lower performance for bulk data retrieval
- **Third-party wrappers**: Rejected due to maintenance and reliability concerns

**Implementation Notes**:
- Connection string format: `host=xxx, port=xxx, username=xxx, password=xxx`
- Query execution: `session.run("SELECT * FROM table")` returns DataFrame
- Connection pooling: Use `dolphindb.session.Session` with context manager
- Error handling: Catch `dolphindb.session.OperationalError` for connection failures

---

### 2. Data Comparison Strategy

**Task**: Determine optimal approach for comparing 84 columns across matched record pairs for datasets up to 2,000,000 records

**Decision**: Use pandas DataFrame operations with vectorized comparison, with chunked processing for large datasets

**Rationale**:
- Pandas provides efficient vectorized operations for large datasets
- Built-in support for column-wise comparison and difference identification
- Memory-efficient for 2M records when using appropriate dtypes and chunking
- Fast performance (<2 minutes for full comparison of 2M records with chunking)
- Easy to integrate with DolphinDB query results (already returns DataFrame)

**Alternatives Considered**:
- **Row-by-row Python loops**: Rejected due to poor performance for 2M records
- **SQL-based comparison**: Rejected because queries run on separate instances
- **Custom numpy arrays**: Rejected due to complexity and maintenance burden
- **Database comparison tools**: Rejected due to external dependency and platform specificity
- **Full DataFrame in-memory**: Rejected due to memory constraints for 2M records

**Implementation Notes**:
- Process data in chunks of 100,000 records to stay under memory limits
- Use `df1.compare(df2)` or `df1.ne(df2)` for column-wise comparison per chunk
- Track specific column names where differences occur across all chunks
- Handle NULL values using pandas' NA-aware comparison
- Memory optimization: Use appropriate dtypes (int32 instead of int64, category for SYMBOL columns)
- **Precision-aware comparison**: Apply rounding before comparison based on field type:
  - Volume fields (e.g., bid_0_volume, offer_5_tradable_volume): Round to integer (#,####)
  - Price fields (e.g., high, last_trade_price, offer_0_price): Round to 5 decimals (#,###.00000)
  - Yield fields (e.g., bid_0_yield, offer_3_yield): Round to 5 decimals (#.00000)

---

### 3. Record Matching Algorithm

**Task**: Design efficient algorithm to match records from two data sources using composite key (receive_time, exch_product_id, settle_speed)

**Decision**: Multi-index merge with pandas (inner join on composite key), with chunked processing for large datasets

**Rationale**:
- Pandas `merge()` with `on=['receive_time', 'exch_product_id', 'settle_speed']` is optimized
- O(n log n) complexity for matching 2M records
- Automatically identifies unmatched records (left_only, right_only)
- Handles NULL matching keys correctly
- Integrated seamlessly with comparison workflow
- Chunked processing reduces memory pressure

**Alternatives Considered**:
- **Hash table lookup in Python**: Rejected due to manual implementation overhead
- **Sort-based merge**: Rejected because pandas already implements this efficiently
- **Database-side join**: Rejected due to cross-instance constraint

**Implementation Notes**:
- Process data in chunks of 100,000 records per instance
- Use `pd.merge(left_df, right_df, on=['receive_time', 'exch_product_id', 'settle_speed'], how='outer', indicator=True)` per chunk
- `_merge` column identifies: 'left_only', 'right_only', 'both'
- Separate matched pairs (`_merge == 'both'`) from unmatched records
- For BOND data: settle_speed can be 0 or 1, both must be considered
- Aggregate results across chunks for final reporting

---

### 4. Retry Logic Implementation

**Task**: Implement retry mechanism with 3 attempts for connection failures and query errors

**Decision**: Use `retrying` library with exponential backoff

**Rationale**:
- Simple decorator-based API (`@retry` on functions)
- Built-in exponential backoff (delays: 1s, 2s, 4s)
- Configurable retry count and exception types
- Well-maintained and widely used in Python projects
- Reduces boilerplate code compared to manual retry loops

**Alternatives Considered**:
- **Manual while loops**: Rejected due to code duplication and error-prone
- **Tenacity library**: Rejected due to slightly more complex API
- **Custom retry decorator**: Rejected due to maintenance burden

**Implementation Notes**:
- Retry on: `dolphindb.session.OperationalError`, `dolphindb.session.InterfaceError`
- Max attempts: 3
- Wait strategy: exponential backoff with jitter
- Stop retrying on specific errors (e.g., authentication failures)

---

### 5. INI Configuration Management

**Task**: Design INI file structure for storing DolphinDB connection details for two instances

**Decision**: Use Python's built-in `configparser` module with standard INI format

**Rationale**:
- No external dependencies (part of Python standard library)
- Simple, human-readable format
- Supports sections (useful for left/right instances)
- Widely understood and easy to edit
- Type conversion support (strings, integers, booleans)

**Alternatives Considered**:
- **YAML**: Rejected due to additional `pyyaml` dependency
- **JSON**: Rejected due to lack of comments support
- **Environment variables**: Rejected due to difficulty managing complex nested config

**Implementation Notes**:
```ini
[instance_left]
host = localhost
port = 8848
username = admin
password = 123456
database = market_data

[instance_right]
host = 192.168.1.100
port = 8848
username = admin
password = 123456
database = market_data
```

---

### 6. Report Generation Approach

**Task**: Design Markdown report format and generation strategy for validation results

**Decision**: Use Python string templating with f-strings for Markdown generation

**Rationale**:
- No external dependencies required
- Full control over report structure and formatting
- Easy to maintain and extend
- Performance is not critical (reports generated in <30 seconds)
- Markdown is text-based, ideal for string operations

**Alternatives Considered**:
- **Jinja2 templates**: Rejected due to additional dependency
- **ReportLab/WeasyPrint**: Rejected (PDF not required)
- **Markdown generation libraries**: Rejected due to overkill for simple reports

**Implementation Notes**:
Report structure per file:
```markdown
# Validation Report: {product_type}/{tick_type}

**Validation Date**: YYYYMMDD  
**Generated At**: YYYY-MM-DD HH:MM:SS

## Summary

| Metric | Left Instance | Right Instance |
|--------|---------------|----------------|
| Records Retrieved | {count} | {count} |

## Match Results

- **Matched Records**: {count}
- **Unmatched Records**: {count}

### Unmatched by Column

| Column Name | Differences |
|-------------|-------------|
| {column_name} | {count} |

### Unmatched by Side

| Side | Records |
|------|---------|
| Left Only | {count} |
| Right Only | {count} |
```

---

### 7. Date Format Handling

**Task**: Implement date parsing from YYYYMMDD (CLI) to YYYY.MM.DD (SQL query)

**Decision**: Use Python's `datetime` module with string formatting

**Rationale**:
- Standard library (no dependencies)
- Simple and reliable
- Built-in validation for date correctness

**Implementation Notes**:
```python
from datetime import datetime

# Parse CLI argument: YYYYMMDD
date_str = "20260115"
date_obj = datetime.strptime(date_str, "%Y%m%d")

# Format for SQL query: YYYY.MM.DD
formatted_date = date_obj.strftime("%Y.%m.%d")  # "2026.01.15"
```

---

### 8. Command-Line Interface Design

**Task**: Design CLI arguments and structure for the validation tool

**Decision**: Use Python's `argparse` module with named parameters

**Rationale**:
- Standard library (no dependencies)
- Automatic help generation (`--help`)
- Type validation (e.g., integer for step number)
- Supports required and optional parameters

**Implementation Notes**:
```python
# CLI structure:
python -m etl_validator --config <path> --date <YYYYMMDD> [--step <1|2|3>]

# --config: Required, path to INI file
# --date: Required, business date in YYYYMMDD format
# --step: Optional, validation step number (1, 2, or 3)
```

---

### 9. Memory Management for Large Datasets

**Task**: Ensure tool handles 2,000,000 records per instance without exceeding 2GB memory limit

**Decision**: Use pandas with memory-efficient dtypes and mandatory chunked processing

**Rationale**:
- Pandas automatically optimizes memory usage with appropriate dtypes
- 2M records × 84 columns × 8 bytes (double) ≈ 1.34GB per DataFrame (too large)
- Chunked processing in 100,000-record chunks reduces peak memory to ~134MB per chunk
- Two DataFrames (left + right) per chunk ≈ 268MB, plus overhead
- Use `category` dtype for SYMBOL columns (significant memory reduction)
- Use `int32` instead of `int64` where range permits

**Alternatives Considered**:
- **Full in-memory processing**: Rejected due to memory constraints for 2M records
- **Dask/out-of-core processing**: Considered but pandas chunking is simpler and sufficient
- **Database cursors**: Rejected due to pandas integration overhead

**Implementation Notes**:
- Process data in chunks of 100,000 records (20 chunks for 2M records)
- Load chunks sequentially, process each chunk, then release memory
- Use `category` dtype for all SYMBOL columns (product_type, exchange, source, etc.)
- Use `int32` for settle_speed, level
- Use `int64` only for timestamps and large numeric fields
- Monitor memory usage with `psutil` if needed for debugging
- Clear DataFrames after each chunk using `del` and `gc.collect()`

---

### 10. Validation Group Execution Flow

**Task**: Design execution flow for three validation groups (all steps or single step)

**Decision**: Sequential execution with independent report generation

**Rationale**:
- Simple and predictable
- Each group is independent (no dependencies)
- Allows partial results if one step fails after retries
- Easy to implement and test

**Implementation Notes**:
```python
VALIDATION_GROUPS = [
    (1, "BOND", "TRADE"),
    (2, "BOND", "QUOTE"),
    (3, "BOND_FUT", "SNAPSHOT"),
]

# Execution flow:
1. Parse --step parameter (default: None = all steps)
2. For each step in VALIDATION_GROUPS:
   a. If --step specified and != current step, skip
   b. Retrieve data from both instances with filters
   c. Match records
   d. Compare columns
   e. Generate report
   f. If failure, retry up to 3 times, then stop
```

---

## Summary of Resolved Decisions

All technical unknowns have been resolved through research:

| Technical Area | Decision | Key Dependencies |
|----------------|------------|------------------|
| DolphinDB Client | Official `dolphindb` SDK | dolphindb |
| Data Comparison | Pandas vectorized operations with precision-aware rounding | pandas |
| Record Matching | Pandas merge on composite key | pandas |
| Retry Logic | `retrying` library with exponential backoff | retrying |
| Config Management | Python `configparser` with INI format | configparser (stdlib) |
| Report Generation | Python f-string templating | None (stdlib) |
| Date Handling | Python `datetime` module | datetime (stdlib) |
| CLI Interface | Python `argparse` module | argparse (stdlib) |
| Memory Management | Pandas with efficient dtypes and chunked processing | pandas |
| Numeric Precision | Pandas `round()` with field-specific precision rules | pandas |

**Total External Dependencies**: 3 (dolphindb, pandas, retrying)

**Total Standard Library Dependencies**: 4 (configparser, argparse, datetime, logging)

---

## Performance Estimates

Based on research findings and constraints (with chunked processing for 2M records):

| Operation | Dataset Size | Chunk Size | Estimated Time |
|------------|---------------|------------|---------------|
| Connect to DolphinDB (2 instances) | N/A | N/A | <5 seconds |
| Query retrieval (2M records per instance) | 2M rows | 60-120 seconds |
| Record matching (2M × 2M) | 2M rows | 100k rows/chunk × 20 chunks: 60-120 seconds |
| Column comparison (84 columns) | Matched pairs | 100k rows/chunk × 20 chunks: 60-120 seconds |
| Report generation | N/A | N/A | <5 seconds |
| **Total for single group** | 2M rows | 100k | **3-5 minutes** |
| **Total for all 3 groups** | 2M rows × 3 | 100k | **9-15 minutes** |

**Critical Note**: The current design with chunked processing may exceed the 5-minute success criterion (SC-001) for 2M records. Two options:

1. **Optimize chunk size**: Increase chunk size to 500,000 rows (4 chunks) - estimated 2-3.5 minutes per group
2. **Adjust success criterion**: Accept 9-15 minutes for 2M records, or clarify if 5-minute criterion applies to smaller datasets

**Recommendation**: Clarify the expected dataset size and performance requirements. If 2M records is the maximum expected, the 5-minute criterion needs adjustment.

---

### 11. Numeric Precision Handling

**Task**: Implement precision-aware comparison for numeric fields to handle floating-point differences that are within acceptable tolerance.

**Decision**: Use pandas `round()` method before comparison, with different rounding rules based on field type (volumes, prices, yields)

**Rationale**:
- Pandas `round()` provides vectorized rounding for entire columns
- Precision requirements are domain-specific (financial data):
  - Volumes: Integer precision (#,####) - 4 decimal places, treat as integer
  - Prices: 5 decimal places (#,###.00000) - typical for currency/price data
  - Yields: 5 decimal places (#.00000) - small values, high precision needed
- Rounding before comparison ensures consistent treatment of floating-point errors
- Pandas NA-aware comparison handles NULL values correctly

**Alternatives Considered**:
- **Absolute tolerance comparison** (`abs(a-b) < tolerance`): Rejected due to different tolerances per field type
- **Relative tolerance comparison** (`abs(a-b) < tolerance * max(a,b)`): Rejected due to complexity and domain mismatch
- **String conversion with formatting**: Rejected due to performance overhead and type safety issues
- **Custom rounding function**: Rejected because pandas `round()` is sufficient and optimized

**Implementation Notes**:
```python
# Define field groups by precision
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
    'offer_4_volume', 'offer_5_volume',
]

PRICE_FIELDS = [
    'last_trade_price', 'pre_close_price', 'pre_settle_price', 'open_price',
    'high_price', 'low_price', 'close_price', 'settle_price', 'upper_limit',
    'lower_limit',
    'bid_0_price', 'bid_1_price', 'bid_2_price', 'bid_3_price',
    'bid_4_price', 'bid_5_price',
    'offer_0_price', 'offer_1_price', 'offer_2_price', 'offer_3_price',
    'offer_4_price', 'offer_5_price',
]

YIELD_FIELDS = [
    'last_trade_yield',
    'bid_0_yield', 'bid_1_yield', 'bid_2_yield', 'bid_3_yield',
    'bid_4_yield', 'bid_5_yield',
    'offer_0_yield', 'offer_1_yield', 'offer_2_yield', 'offer_3_yield',
    'offer_4_yield', 'offer_5_yield',
]

# Apply rounding before comparison
left_rounded = left_df.copy()
right_rounded = right_df.copy()

left_rounded[VOLUME_FIELDS] = left_df[VOLUME_FIELDS].round(0)
right_rounded[VOLUME_FIELDS] = right_df[VOLUME_FIELDS].round(0)

left_rounded[PRICE_FIELDS] = left_df[PRICE_FIELDS].round(5)
right_rounded[PRICE_FIELDS] = right_df[PRICE_FIELDS].round(5)

left_rounded[YIELD_FIELDS] = left_df[YIELD_FIELDS].round(5)
right_rounded[YIELD_FIELDS] = right_df[YIELD_FIELDS].round(5)

# Compare rounded values
differences = left_rounded.ne(right_rounded)
```

**Performance Impact**: Negligible - rounding is O(n) and vectorized, adds <1 second to comparison time for 2M records.

---

## Next Steps

With all research complete and decisions made, proceed to **Phase 1: Design & Contracts**:

1. Generate `data-model.md` with entity definitions and relationships
2. Generate `contracts/` directory with CLI interface specifications
3. Generate `quickstart.md` with setup and usage instructions
4. Update agent context with technology stack
5. Re-evaluate Constitution Check post-design
