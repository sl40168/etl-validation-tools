# Data Model: DolphinDB ETL Data Validation Tool

**Feature**: [001-etl-validation](./spec.md) | **Date**: 2026-01-15

## Overview

This document defines the data entities, their attributes, relationships, and validation rules for the DolphinDB ETL Data Validation Tool. All entities are derived from the feature specification and original requirements.

---

## Entity Definitions

### 1. DolphinDB Connection Configuration

**Description**: Represents connection details for a DolphinDB instance, loaded from INI configuration file.

**Attributes**:

| Attribute | Type | Description | Validation |
|-----------|-------|-------------|-------------|
| `host` | String | DolphinDB server hostname or IP address | Required, non-empty |
| `port` | Integer | DolphinDB server port number | Required, 1-65535 |
| `username` | String | Authentication username | Required, non-empty |
| `password` | String | Authentication password | Required, non-empty |
| `database` | String | Target database name | Required, non-empty |

Relationships:
- Used by: `ValidationGroup` (to query data)

**Validation Rules**:
- All fields must be present in INI section
- Port must be valid integer in range 1-65535
- Connection test must succeed before proceeding with validation

**Example INI Structure**:
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

### 2. Market Price Record

**Description**: Represents a single market price data row retrieved from DolphinDB. Contains 100 fields across identifiers, pricing data, timestamps, and quote levels.

**Attributes**:

| Attribute | Type | Description | Validation |
|-----------|-------|-------------|-------------|
| `business_date` | Date | Business date for the record | Required |
| `exch_product_id` | Symbol | Exchange product identifier | Required (matching key) |
| `product_type` | Symbol | Product type (BOND or BOND_FUT) | Required, enum: BOND, BOND_FUT |
| `exchange` | Symbol | Exchange code | Required |
| `source` | Symbol | Data source identifier | Required |
| `settle_speed` | Integer | Settlement speed (0 or 1 for BOND) | Required (matching key) |
| `last_trade_price` | Double | Last trade price | Optional | Precision: #,###.00000 |
| `last_trade_yield` | Double | Last trade yield | Optional | Precision: #.00000 |
| `last_trade_yield_type` | Symbol | Last trade yield type | Optional |
| `last_trade_volume` | Double | Last trade volume | Optional | Precision: #,#### |
| `last_trade_turnover` | Double | Last trade turnover | Optional | Precision: #,#### |
| `last_trade_interest` | Double | Last trade interest | Optional | Precision: #,#### |
| `last_trade_side` | Symbol | Last trade side | Optional |
| `level` | Symbol | Price level | Optional |
| `status` | Symbol | Status indicator | Optional |
| `pre_close_price` | Double | Previous close price | Optional | Precision: #,###.00000 |
| `pre_settle_price` | Double | Previous settle price | Optional | Precision: #,###.00000 |
| `pre_interest` | Double | Previous interest | Optional | Precision: #,#### |
| `open_price` | Double | Open price | Optional | Precision: #,###.00000 |
| `high_price` | Double | High price | Optional | Precision: #,###.00000 |
| `low_price` | Double | Low price | Optional | Precision: #,###.00000 |
| `close_price` | Double | Close price | Optional | Precision: #,###.00000 |
| `settle_price` | Double | Settlement price | Optional | Precision: #,###.00000 |
| `upper_limit` | Double | Upper limit price | Optional | Precision: #,###.00000 |
| `lower_limit` | Double | Lower limit price | Optional | Precision: #,###.00000 |
| `total_volume` | Double | Total volume | Optional | Precision: #,#### |
| `total_turnover` | Double | Total turnover | Optional | Precision: #,#### |
| `open_interest` | Double | Open interest | Optional | Precision: #,#### |
| `bid_0_price` to `bid_5_price` | Double | Bid prices (6 levels) | Optional | Precision: #,###.00000 |
| `bid_0_yield` to `bid_5_yield` | Double | Bid yields (6 levels) | Optional | Precision: #.00000 |
| `bid_0_yield_type` to `bid_5_yield_type` | Symbol | Bid yield types (6 levels) | Optional |
| `bid_0_tradable_volume` to `bid_5_tradable_volume` | Double | Bid tradable volumes (6 levels) | Optional | Precision: #,#### |
| `bid_0_volume` to `bid_5_volume` | Double | Bid volumes (6 levels) | Optional | Precision: #,#### |
| `offer_0_price` to `offer_5_price` | Double | Offer prices (6 levels) | Optional | Precision: #,###.00000 |
| `offer_0_yield` to `offer_5_yield` | Double | Offer yields (6 levels) | Optional | Precision: #.00000 |
| `offer_0_yield_type` to `offer_5_yield_type` | Symbol | Offer yield types (6 levels) | Optional |
| `offer_0_tradable_volume` to `offer_5_tradable_volume` | Double | Offer tradable volumes (6 levels) | Optional | Precision: #,#### |
| `offer_0_volume` to `offer_5_volume` | Double | Offer volumes (6 levels) | Optional | Precision: #,#### |
| `event_time_trade` | Timestamp | Event time for trade | Optional |
| `receive_time_trade` | Timestamp | Receive time for trade | Optional |
| `create_time_trade` | Timestamp | Create time for trade | Optional |
| `event_time_quote` | Timestamp | Event time for quote | Optional |
| `receive_time_quote` | Timestamp | Receive time for quote | Optional |
| `create_time_quote` | Timestamp | Create time for quote | Optional |
| `tick_type` | Symbol | Tick type (TRADE, QUOTE, or SNAPSHOT) | Required, enum: TRADE, QUOTE, SNAPSHOT |
| `receive_time` | Timestamp | Receive time (matching key) | Required (matching key) |
| `create_time` | Timestamp | Create time | Optional |
| `store_time` | Timestamp | Store time | Optional |

**Total Columns**: 100

**Matching Keys**: `receive_time`, `exch_product_id`, `settle_speed`

**Comparison Columns**: 84 columns (all except: `create_time`, `store_time`, and matching keys when used for matching)

**Relationships**:
- Belongs to: `ValidationGroup` (filtered by product_type and tick_type)
- Pairs with: Another `MarketPriceRecord` from opposite instance (if matched)

**Validation Rules**:
- `business_date` must match the validation date
- `product_type` must be one of: BOND, BOND_FUT
- For BOND: `tick_type` must be TRADE or QUOTE; `settle_speed` must be 0 or 1
- For BOND_FUT: `tick_type` must be SNAPSHOT
- Matching keys (receive_time, exch_product_id, settle_speed) must not be NULL for matching
- NULL values allowed in non-matching, non-required fields

---

### 3. Validation Group

**Description**: Represents a logical grouping of records for validation, defined by specific `product_type` and `tick_type` combinations.

**Attributes**:

| Attribute | Type | Description | Validation |
|-----------|-------|-------------|-------------|
| `step_number` | Integer | Sequential step number (1, 2, or 3) | Required, 1-3 |
| `product_type` | Symbol | Product type filter | Required, enum: BOND, BOND_FUT |
| `tick_type` | Symbol | Tick type filter | Required, enum: TRADE, QUOTE, SNAPSHOT |
| `description` | String | Human-readable description | Required |

**Predefined Groups**:

| Step | Product Type | Tick Type | Description |
|------|--------------|------------|-------------|
| 1 | BOND | TRADE | Bond trade data |
| 2 | BOND | QUOTE | Bond quote data |
| 3 | BOND_FUT | SNAPSHOT | Bond futures snapshot data |

**Relationships**:
- Filters: `MarketPriceRecord` from both instances
- Produces: `ValidationReport`

**Validation Rules**:
- Only 3 predefined groups exist (no dynamic groups)
- Each group is independent (no dependencies between groups)

---

### 4. Matched Record Pair

**Description**: Represents two `MarketPriceRecord` instances (one from left DolphinDB, one from right DolphinDB) that match on the composite key.

**Attributes**:

| Attribute | Type | Description |
|-----------|-------|-------------|
| `left_record` | MarketPriceRecord | Record from left DolphinDB instance |
| `right_record` | MarketPriceRecord | Record from right DolphinDB instance |
| `matching_key` | Tuple | (receive_time, exch_product_id, settle_speed) |
| `differences` | List | Column names where values differ |

**Relationships**:
- Composed of: Two `MarketPriceRecord` instances
- Generates: Comparison results in `ValidationReport`

**Validation Rules**:
- Both records must exist (matched)
- Matching keys must be identical
- Differences list may be empty (perfect match)
- Comparison covers 84 columns

---

### 5. Unmatched Record

**Description**: Represents a `MarketPriceRecord` from one instance that has no corresponding record in the other instance.

**Attributes**:

| Attribute | Type | Description | Validation |
|-----------|-------|-------------|-------------|
| `record` | MarketPriceRecord | The unmatched record | Required |
| `side` | Symbol | Which side the record is from | Required, enum: LEFT, RIGHT |
| `reason` | String | Reason for no match (e.g., "No matching record in right instance") | Required |

**Relationships**:
- One `MarketPriceRecord` instance
- Categorized in: `ValidationReport`

**Validation Rules**:
- Side must be LEFT or RIGHT
- Record must not have a matching record in opposite instance

---

### 6. Validation Report

**Description**: A Markdown document containing statistics and results for a validation group execution.

**Attributes**:

| Attribute | Type | Description |
|-----------|-------|-------------|
| `group` | ValidationGroup | The validation group this report covers |
| `validation_date` | Date | Business date being validated (YYYYMMDD) |
| `generated_at` | Timestamp | When the report was generated |
| `left_retrieved_count` | Integer | Number of records retrieved from left instance |
| `right_retrieved_count` | Integer | Number of records retrieved from right instance |
| `matched_count` | Integer | Number of matched record pairs |
| `unmatched_count` | Integer | Total number of unmatched records |
| `column_differences` | Dictionary | Column name → count of differences |
| `left_unmatched_count` | Integer | Records only in left instance |
| `right_unmatched_count` | Integer | Records only in right instance |
| `filename` | String | Output filename (e.g., validation_BOND_TRADE_20260115.md) |

**Relationships**:
- Generated from: `ValidationGroup`
- Contains: Statistics for `MatchedRecordPair` and `UnmatchedRecord`

**Validation Rules**:
- All counts must be non-negative
- `left_retrieved_count + right_retrieved_count >= matched_count * 2`
- `unmatched_count == left_unmatched_count + right_unmatched_count`
- Filename format: `validation_{product_type}_{tick_type}_{YYYYMMDD}.md`
- Output directory: `reports/` (relative to current working directory)

**Report Structure**:
```markdown
# Validation Report: {product_type}/{tick_type}

**Validation Date**: {YYYYMMDD}  
**Generated At**: {YYYY-MM-DD HH:MM:SS}

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
...

### Unmatched by Side

| Side | Records |
|------|---------|
| Left Only | {count} |
| Right Only | {count} |
```

---

## Data Precision Requirements

**Critical**: All numeric comparisons must respect the following precision formats. Differences beyond specified precision should be considered equal.

### Volume Precision: #,####

Fields with this precision (4 decimal places, integer format):
- `last_trade_volume`
- `last_trade_turnover`
- `last_trade_interest`
- `pre_interest`
- `total_volume`
- `total_turnover`
- `open_interest`
- `bid_0_tradable_volume` through `bid_5_tradable_volume` (6 levels)
- `bid_0_volume` through `bid_5_volume` (6 levels)
- `offer_0_tradable_volume` through `offer_5_tradable_volume` (6 levels)
- `offer_0_volume` through `offer_5_volume` (6 levels)

**Comparison Rule**: Round to nearest integer before comparison. Values differing by <0.5 are considered equal.

**Example**:
```
Left:  12345.6789
Right: 12345.1234
Rounded: 12346, 12345 → NOT EQUAL (difference: 1)
```

### Price Precision: #,###.00000

Fields with this precision (5 decimal places):
- `last_trade_price`
- `pre_close_price`
- `pre_settle_price`
- `open_price`
- `high_price`
- `low_price`
- `close_price`
- `settle_price`
- `upper_limit`
- `lower_limit`
- `bid_0_price` through `bid_5_price` (6 levels)
- `offer_0_price` through `offer_5_price` (6 levels)

**Comparison Rule**: Round to 5 decimal places before comparison. Values differing by <0.000005 are considered equal.

**Example**:
```
Left:  123.4567890123
Right: 123.4567889876
Rounded: 123.45679, 123.45679 → EQUAL
```

### Yield Precision: #.00000

Fields with this precision (5 decimal places, typically small values):
- `last_trade_yield`
- `bid_0_yield` through `bid_5_yield` (6 levels)
- `offer_0_yield` through `offer_5_yield` (6 levels)

**Comparison Rule**: Round to 5 decimal places before comparison. Values differing by <0.000005 are considered equal.

**Example**:
```
Left:  0.0123456789
Right: 0.0123451234
Rounded: 0.01235, 0.01235 → EQUAL
```

### Implementation Notes

When comparing numeric fields in the 84-column comparison:

1. **Apply rounding based on field type** before comparison
2. **Use pandas `round()` method** for vectorized rounding:
   ```python
   volume_fields.round(0)  # Round to integer
   price_fields.round(5)    # Round to 5 decimals
   yield_fields.round(5)     # Round to 5 decimals
   ```
3. **Handle NaN/NULL values**: Treat NaN as different from any non-NaN value
4. **Precision-aware comparison**: Only flag differences after rounding

**Example Implementation**:
```python
# Before comparison, apply precision rounding
left_rounded = left_df[price_fields].round(5)
right_rounded = right_df[price_fields].round(5)

# Compare rounded values
differences = left_rounded.ne(right_rounded)
```

---

## Entity Relationships

```
DolphinDB Connection (left) ─┐
                             ├──► MarketPriceRecord ─┬──► MatchedRecordPair
DolphinDB Connection (right)─┘                          │
                                                 │
ValidationGroup ──► MarketPriceRecord ──► UnmatchedRecord
                                                 │
                                                 └──► ValidationReport
```

**Legend**:
- `──►` = "filters" or "queries"
- `┬──►` = "pairs with"
- `─►` = "belongs to" or "produces"

---

## State Transitions

### Validation Execution Flow

```
[Start]
  │
  ├─► Load Config (2x DolphinDB Connection)
  │
  ├─► For each ValidationGroup (1, 2, 3):
  │     │
  │     ├─► Retrieve Data (MarketPriceRecord from both instances)
  │     │
  │     ├─► Match Records (MatchedRecordPair, UnmatchedRecord)
  │     │
  │     ├─► Compare Columns (84 columns)
  │     │
  │     └─► Generate Report (ValidationReport)
  │
  └─► [End]
```

**Notes**:
- Steps execute sequentially
- If a step fails after 3 retries, execution stops
- Each step is independent (no dependencies)

---

## Data Volume Considerations

Based on success criteria:

- **Max records per instance**: 2,000,000
- **Max records per validation group**: 2,000,000 (per instance)
- **Max matched pairs**: 2,000,000
- **Max unmatched records**: Up to 4,000,000 (if no matches)
- **Total columns per record**: 100
- **Comparison columns**: 84

**Memory Estimates** (with chunked processing):
- Chunk size: 100,000 records (20 chunks for 2M records)
- Single chunk DataFrame (100k rows × 84 columns × 8 bytes) ≈ 67 MB
- Two DataFrames per chunk (left + right) ≈ 134 MB (with sparse data optimization)
- With efficient dtypes (category for SYMBOL, int32 for small ints): <100 MB per chunk
- Peak memory: ~150-200 MB (including overhead for processing)

---

## Validation Rules Summary

### Input Validation

| Input | Rule |
|--------|-------|
| `--config` parameter | Must be valid file path, INI format, required fields present |
| `--date` parameter | Must be YYYYMMDD format, valid date |
| `--step` parameter | Must be 1, 2, or 3 (optional, single value only) |
| Connection parameters | Host, port, username, password, database all required |
| INI structure | Must have `[instance_left]` and `[instance_right]` sections |

### Data Validation

| Entity | Rule |
|--------|-------|
| MarketPriceRecord | `product_type` ∈ {BOND, BOND_FUT}; `tick_type` ∈ {TRADE, QUOTE, SNAPSHOT} |
| MarketPriceRecord | For BOND: `settle_speed` ∈ {0, 1} |
| MarketPriceRecord | Matching keys (receive_time, exch_product_id, settle_speed) not NULL |
| MatchedRecordPair | Both records exist, keys identical |
| ValidationReport | All counts non-negative; totals consistent |

### Business Validation

| Rule | Description |
|------|-------------|
| Date format | CLI input: YYYYMMDD; SQL query: YYYY.MM.DD |
| Group selection | Only 3 predefined groups; no dynamic groups |
| Retry logic | Up to 3 attempts; stop if all fail |
| Report location | `reports/` subdirectory in CWD |
| Multiple steps | Error if multiple `--step` parameters provided |

---

## Next Steps

With data model defined, proceed with:

1. Generate CLI interface contracts in `contracts/`
2. Generate `quickstart.md` with setup instructions
3. Update agent context with technology stack
4. Re-evaluate Constitution Check
