# Data Model: Group-Based Column Validation

**Feature**: [001-group-based-validation](./spec.md) | **Date**: 2026-01-15

## Overview

This document defines the data model for group-based column validation, including entities, attributes, relationships, and validation rules. The model extends the existing ETL validation tool with group-specific column definitions and validation logic.

---

## Entities

### ValidationGroup

Represents a data group definition with its required columns for validation.

**Attributes**:
- `group_id` (int): Unique identifier for the group (1, 2, or 3)
- `product_type` (str): Product type code (e.g., "BOND", "BOND_FUT")
- `message_type` (str): Message type code (e.g., "TRADE", "QUOTE", "SNAPSHOT")
- `required_columns` (List[str]): List of column names that must be validated for this group
- `description` (str, optional): Human-readable description of the group

**Key**:
- Composite key: (group_id, product_type, message_type)

**Validation Rules**:
- group_id must be 1, 2, or 3
- product_type must be non-empty string
- message_type must be non-empty string
- required_columns must be non-empty list
- No duplicate column names within a group

**Relationships**:
- One-to-many with ValidationRule (each group has multiple column validation rules)

---

### ValidationRule

Represents column-specific validation requirements for a group.

**Attributes**:
- `column_name` (str): Name of the column to validate
- `data_type` (str): Expected data type ("int", "float", "str", "datetime")
- `required` (bool): Whether the column must be present
- `precision` (int, optional): Decimal precision for numeric fields (0 for integers, 5 for prices/yields)
- `nullable` (bool): Whether NULL values are allowed

**Key**:
- Composite key: (group_key, column_name) where group_key references ValidationGroup

**Validation Rules**:
- column_name must be non-empty string
- data_type must be one of: "int", "float", "str", "datetime"
- If data_type is "int", precision should be 0
- If data_type is "float", precision should be >= 0

**Relationships**:
- Many-to-one with ValidationGroup (belongs to exactly one group)

---

### ColumnValidationResult

Represents the outcome of validating columns for a specific group.

**Attributes**:
- `group_key` (tuple): Reference to ValidationGroup (group_id, product_type, message_type)
- `status` (str): Overall validation status ("PASS" or "FAIL")
- `missing_columns` (List[str]): List of required columns not found in the dataset
- `extra_columns` (List[str]): List of additional columns found (ignored, not required)
- `type_mismatches` (List[str]): List of columns with incorrect data types
- `validated_at` (datetime): Timestamp when validation was performed

**Validation Rules**:
- status must be "PASS" or "FAIL"
- If status is "FAIL", at least one of missing_columns or type_mismatches must be non-empty
- validated_at must be valid datetime

**Relationships**:
- Many-to-one with ValidationGroup

---

### ComparisonResult

Represents the outcome of comparing two datasets (left vs right instances).

**Attributes**:
- `group_key` (tuple): Reference to ValidationGroup
- `total_records` (int): Total number of records processed
- `matched_records` (int): Number of records matched on composite key
- `unmatched_left` (int): Number of records only in left instance
- `unmatched_right` (int): Number of records only in right instance
- `column_differences` (Dict[str, int]): Mapping of column names to difference counts
- `null_aware_passes` (int): Number of columns where both sides were NULL (passed validation)
- `comparison_time_seconds` (float): Time taken for comparison

**Validation Rules**:
- total_records >= matched_records + unmatched_left + unmatched_right
- matched_records >= 0
- column_differences values must be >= 0
- comparison_time_seconds > 0

**Relationships**:
- Many-to-one with ValidationGroup
- One-to-many with ColumnValidationResult (uses column_validation for metadata)

---

### ValidationReport

Represents a complete validation report for a group, combining column validation and comparison results.

**Attributes**:
- `report_id` (str): Unique identifier for the report (UUID)
- `group_key` (tuple): Reference to ValidationGroup
- `column_validation` (ColumnValidationResult): Column validation outcome
- `comparison_result` (ComparisonResult): Comparison outcome
- `business_date` (str): Business date in YYYYMMDD format
- `generated_at` (datetime): Timestamp when report was generated
- `output_path` (str): File path where Markdown report was written

**Key**:
- report_id (UUID)

**Validation Rules**:
- report_id must be valid UUID string
- business_date must match YYYYMMDD format
- generated_at must be valid datetime
- output_path must be absolute path

**Relationships**:
- Many-to-one with ValidationGroup
- One-to-one with ColumnValidationResult
- One-to-one with ComparisonResult

---

## Predefined Validation Groups

### Group 1: BOND TRADE

**Key**: (1, "BOND", "TRADE")
**Required Columns**: 18

```python
BOND_TRADE_COLUMNS = [
    # Base identifiers
    "business_date",
    "exch_product_id",
    "product_type",
    "exchange",
    "source",
    "settle_speed",

    # Trade data
    "last_trade_price",
    "last_trade_yield",
    "last_trade_yield_type",
    "last_trade_volume",
    "last_trade_turnover",
    "last_trade_interest",
    "last_trade_side",
    "level",
    "status",
]
```

**Column Validation Rules**:
- `business_date`: datetime, required, nullable=False
- `exch_product_id`: str, required, nullable=False
- `product_type`: str, required, nullable=False
- `exchange`: str, required, nullable=False
- `source`: str, required, nullable=False
- `settle_speed`: int, required, nullable=False, precision=0
- `last_trade_price`: float, required, nullable=True, precision=5
- `last_trade_yield`: float, required, nullable=True, precision=5
- `last_trade_yield_type`: str, required, nullable=True
- `last_trade_volume`: int, required, nullable=True, precision=0
- `last_trade_turnover`: int, required, nullable=True, precision=0
- `last_trade_interest`: int, required, nullable=True, precision=0
- `last_trade_side`: str, required, nullable=True
- `level`: int, required, nullable=True, precision=0
- `status`: str, required, nullable=False

---

### Group 2: BOND QUOTE

**Key**: (2, "BOND", "QUOTE")
**Required Columns**: 60 (6 price levels × 10 fields)

```python
BOND_QUOTE_COLUMNS = [
    # Base identifiers
    "business_date",
    "exch_product_id",
    "product_type",
    "exchange",
    "source",
    "settle_speed",

    # Bid/offer levels 0-5 (each level has 10 fields)
    "bid_0_price", "bid_0_yield", "bid_0_yield_type",
    "bid_0_tradable_volume", "bid_0_volume",
    "offer_0_price", "offer_0_yield", "offer_0_yield_type",
    "offer_0_tradable_volume", "offer_0_volume",

    "bid_1_price", "bid_1_yield", "bid_1_yield_type",
    "bid_1_tradable_volume", "bid_1_volume",
    "offer_1_price", "offer_1_yield", "offer_1_yield_type",
    "offer_1_tradable_volume", "offer_1_volume",

    "bid_2_price", "bid_2_yield", "bid_2_yield_type",
    "bid_2_tradable_volume", "bid_2_volume",
    "offer_2_price", "offer_2_yield", "offer_2_yield_type",
    "offer_2_tradable_volume", "offer_2_volume",

    "bid_3_price", "bid_3_yield", "bid_3_yield_type",
    "bid_3_tradable_volume", "bid_3_volume",
    "offer_3_price", "offer_3_yield", "offer_3_yield_type",
    "offer_3_tradable_volume", "offer_3_volume",

    "bid_4_price", "bid_4_yield", "bid_4_yield_type",
    "bid_4_tradable_volume", "bid_4_volume",
    "offer_4_price", "offer_4_yield", "offer_4_yield_type",
    "offer_4_tradable_volume", "offer_4_volume",

    "bid_5_price", "bid_5_yield", "bid_5_yield_type",
    "bid_5_tradable_volume", "bid_5_volume",
    "offer_5_price", "offer_5_yield", "offer_5_yield_type",
    "offer_5_tradable_volume", "offer_5_volume",
]
```

**Column Validation Rules**:
- Base columns (business_date, exch_product_id, etc.): Same as BOND TRADE
- Price fields (bid_X_price, offer_X_price): float, required, nullable=True, precision=5
- Yield fields (bid_X_yield, offer_X_yield): float, required, nullable=True, precision=5
- Yield type fields (bid_X_yield_type, offer_X_yield_type): str, required, nullable=True
- Tradable volume fields (bid_X_tradable_volume, offer_X_tradable_volume): int, required, nullable=True, precision=0
- Volume fields (bid_X_volume, offer_X_volume): int, required, nullable=True, precision=0

---

### Group 3: BOND_FUT SNAPSHOT

**Key**: (3, "BOND_FUT", "SNAPSHOT")
**Required Columns**: 39

```python
BOND_FUT_SNAPSHOT_COLUMNS = [
    # Base identifiers
    "business_date",
    "exch_product_id",
    "product_type",
    "exchange",
    "source",
    "settle_speed",

    # Trade data
    "last_trade_price",
    "last_trade_yield",
    "last_trade_yield_type",
    "last_trade_volume",
    "last_trade_turnover",
    "last_trade_interest",
    "last_trade_side",
    "level",
    "status",

    # Market summary data
    "pre_close_price",
    "pre_settle_price",
    "pre_interest",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "settle_price",
    "upper_limit",
    "lower_limit",
    "total_volume",
    "total_turnover",
    "open_interest",

    # Quote data (levels 0-1 only)
    "bid_0_price", "bid_0_yield", "bid_0_yield_type",
    "bid_0_tradable_volume", "bid_0_volume",
    "offer_0_price", "offer_0_yield", "offer_0_yield_type",
    "offer_0_tradable_volume", "offer_0_volume",

    "bid_1_price", "bid_1_yield", "bid_1_yield_type",
    "bid_1_tradable_volume", "bid_1_volume",
    "offer_1_price", "offer_1_yield", "offer_1_yield_type",
    "offer_1_tradable_volume", "offer_1_volume",
]
```

**Column Validation Rules**:
- Trade data columns: Same as BOND TRADE
- Market summary fields:
  - Price fields (pre_close_price, open_price, etc.): float, required, nullable=True, precision=5
  - pre_interest, total_volume, total_turnover, open_interest: int, required, nullable=True, precision=0
  - upper_limit, lower_limit: float, required, nullable=True, precision=5
- Quote data (levels 0-1): Same as BOND QUOTE but only levels 0 and 1

---

## Relationships

```
ValidationGroup (1) ----< (1..n) ValidationRule
       |                        |
       |                        |
       |                        v
       |                  ColumnValidationResult
       |
       v
    ComparisonResult
       |
       v
    ValidationReport
```

**Relationship Descriptions**:
- Each ValidationGroup has multiple ValidationRules (one per required column)
- Each ColumnValidationResult belongs to exactly one ValidationGroup
- Each ComparisonResult belongs to exactly one ValidationGroup
- Each ValidationReport references one ColumnValidationResult and one ComparisonResult, both belonging to the same ValidationGroup

---

## Data Flow

1. **Group Selection**: User specifies `--step` parameter (1, 2, or 3)
2. **Group Lookup**: System maps step to ValidationGroup key (group_id, product_type, message_type)
3. **Column Validation**: System validates dataset columns against group's required_columns list
4. **Record Matching**: System matches records between left and right instances on composite key
5. **Comparison**: System compares column values with NULL-aware logic
6. **Report Generation**: System generates Markdown report with ColumnValidationResult and ComparisonResult

---

## State Transitions

### ValidationReport Lifecycle

```
[Created] → [Generating] → [Completed]
              ↓               ↓
           [Failed]        [Failed]
```

**States**:
- **Created**: Report initialized with metadata
- **Generating**: Column validation and comparison in progress
- **Completed**: Report successfully generated and written to file
- **Failed**: Error occurred during validation or report generation

**Transitions**:
- Created → Generating: When validation starts
- Generating → Completed: When validation succeeds and report is written
- Generating → Failed: When error occurs during validation
- Failed → Generating: When retry logic initiates (max 3 attempts)

---

## Constraints

### Performance Constraints
- Maximum records per group: 2,000,000
- Chunk size: 100,000 rows per processing chunk
- Validation time: 3-5 minutes per group for 2M records
- Memory usage: < 2GB peak

### Data Constraints
- Column names must follow naming convention: level_bid/offer fields use `bid_X_` and `offer_X_` prefixes
- NULL handling: Both sides NULL = pass validation
- Precision: Volumes = integer (0 decimals), Prices/Yields = 5 decimals

### Configuration Constraints
- Groups are configured in YAML file (config/groups.yaml) - runtime extensible without code changes
- Step parameter values limited to 1, 2, or 3 (corresponding to group_id)
- All groups use the same composite key for matching: (receive_time, exch_product_id, settle_speed)

---

## Business Rules for Data Type Validation

This section defines the expected data types and business rules for each column category across all validation groups.

### Base Identifier Columns (All Groups)

| Column | Type | Required | Nullable | Precision | Validation Rules |
|--------|------|----------|----------|-----------|-----------------|
| `business_date` | datetime | Yes | False | - | Must match YYYYMMDD format, cannot be NULL |
| `exch_product_id` | str | Yes | False | - | Non-empty string, product identifier, cannot be NULL |
| `product_type` | str | Yes | False | - | One of: "BOND", "BOND_FUT", cannot be NULL |
| `exchange` | str | Yes | False | - | Exchange code (e.g., "SSE", "SZSE"), cannot be NULL |
| `source` | str | Yes | False | - | Data source identifier, cannot be NULL |
| `settle_speed` | int | Yes | False | 0 | Settlement speed code, integer, cannot be NULL |

### Trade Data Columns (BOND TRADE, BOND_FUT SNAPSHOT)

| Column | Type | Required | Nullable | Precision | Validation Rules |
|--------|------|----------|----------|-----------|-----------------|
| `last_trade_price` | float | Yes | True | 5 | Decimal price, max 5 decimal places, can be NULL if no trade |
| `last_trade_yield` | float | Yes | True | 5 | Decimal yield (percent), max 5 decimal places, can be NULL if no trade |
| `last_trade_yield_type` | str | Yes | True | - | Yield type code (e.g., "YTM", "YTC"), can be NULL if no trade |
| `last_trade_volume` | int | Yes | True | 0 | Trade volume in shares, integer, can be NULL if no trade |
| `last_trade_turnover` | float | Yes | True | 2 | Trade turnover in currency, max 2 decimal places, can be NULL if no trade |
| `last_trade_interest` | float | Yes | True | 0 | Interest amount, can be NULL if no trade |
| `last_trade_side` | str | Yes | True | - | Trade side (e.g., "B", "S", "N"), can be NULL if no trade |
| `level` | int | Yes | False | 0 | Price level indicator (typically 0), cannot be NULL |
| `status` | str | Yes | False | - | Trade status (e.g., "A", "C"), cannot be NULL |

### Market Summary Columns (BOND_FUT SNAPSHOT Only)

| Column | Type | Required | Nullable | Precision | Validation Rules |
|--------|------|----------|----------|-----------|-----------------|
| `pre_close_price` | float | Yes | True | 5 | Previous day's close price, can be NULL on new instruments |
| `pre_settle_price` | float | Yes | True | 5 | Previous day's settlement price, can be NULL on new instruments |
| `pre_interest` | int | Yes | True | 0 | Previous day's open interest, can be NULL on new instruments |
| `open_price` | float | Yes | True | 5 | Today's opening price, can be NULL if no trades yet |
| `high_price` | float | Yes | True | 5 | Today's high price, can be NULL if no trades yet |
| `low_price` | float | Yes | True | 5 | Today's low price, can be NULL if no trades yet |
| `close_price` | float | Yes | True | 5 | Today's close price, can be NULL if market not closed |
| `settle_price` | float | Yes | True | 5 | Today's settlement price, can be NULL if not set |
| `upper_limit` | float | Yes | True | 5 | Daily upper price limit, can be NULL if not applicable |
| `lower_limit` | float | Yes | True | 5 | Daily lower price limit, can be NULL if not applicable |
| `total_volume` | int | Yes | True | 0 | Total trading volume today, can be NULL if no trades |
| `total_turnover` | float | Yes | True | 2 | Total trading turnover today, can be NULL if no trades |
| `open_interest` | int | Yes | True | 0 | Today's open interest, can be NULL if not applicable |

### Quote Level Columns (BOND QUOTE, BOND_FUT SNAPSHOT)

For each price level (0-5 in BOND QUOTE, 0-1 in BOND_FUT SNAPSHOT):

| Column Pattern | Type | Required | Nullable | Precision | Validation Rules |
|----------------|------|----------|----------|-----------|-----------------|
| `bid_X_price` | float | Yes | True | 5 | Bid price at level X, max 5 decimals, can be NULL |
| `bid_X_yield` | float | Yes | True | 5 | Bid yield at level X (percent), max 5 decimals, can be NULL |
| `bid_X_yield_type` | str | Yes | True | - | Bid yield type code at level X, can be NULL |
| `bid_X_tradable_volume` | int | Yes | True | 0 | Tradable volume at bid level X, can be NULL |
| `bid_X_volume` | int | Yes | True | 0 | Total volume at bid level X, can be NULL |
| `offer_X_price` | float | Yes | True | 5 | Offer price at level X, max 5 decimals, can be NULL |
| `offer_X_yield` | float | Yes | True | 5 | Offer yield at level X (percent), max 5 decimals, can be NULL |
| `offer_X_yield_type` | str | Yes | True | - | Offer yield type code at level X, can be NULL |
| `offer_X_tradable_volume` | int | Yes | True | 0 | Tradable volume at offer level X, can be NULL |
| `offer_X_volume` | int | Yes | True | 0 | Total volume at offer level X, can be NULL |

**Note**: In BOND QUOTE, X ranges from 0 to 5 (6 levels). In BOND_FUT SNAPSHOT, X ranges from 0 to 1 (2 levels).

### Type Validation Implementation Rules

The `validate_types()` method in `ColumnValidator` must enforce these rules:

1. **Integer Fields** (precision=0): Reject values with non-zero decimal places
   - Example: `settle_speed` value of `10.5` should fail validation
   - Accept: `10`, `-5`, `0`
   - Reject: `10.5`, `10.0` (if stored as float with decimals)

2. **Float Fields with Precision Limit** (precision=5 for prices/yields):
   - Accept: `100.12345`, `99.5`, `100.0`
   - Reject: `100.123456` (6 decimal places), `100.1234567`

3. **Float Fields with 2 Decimal Places** (turnover):
   - Accept: `12345.67`, `100.0`, `0.01`
   - Reject: `12345.678` (3 decimal places)

4. **String Fields**: Non-empty string if not NULL
   - Accept: `"BOND"`, `"SSE"`, `"YTM"`
   - Reject: `""` (empty string), `None` (if nullable=False)

5. **Datetime Fields**: Valid datetime in YYYYMMDD format
   - Accept: `"20260115"`, datetime objects
   - Reject: `"2026-01-15"` (wrong format), `"20261301"` (invalid month), `None` (if nullable=False)

6. **NULL Handling**:
   - If `nullable=True`: Accept `None`, `pd.NA`, `numpy.nan`
   - If `nullable=False`: Reject all NULL values

### Example: type_rules Parameter Structure

The `type_rules` parameter passed to `ColumnValidator` should be structured as:

```python
type_rules = {
    "business_date": {"type": "datetime", "nullable": False},
    "exch_product_id": {"type": "str", "nullable": False},
    "settle_speed": {"type": "int", "nullable": False, "precision": 0},
    "last_trade_price": {"type": "float", "nullable": True, "precision": 5},
    "last_trade_yield": {"type": "float", "nullable": True, "precision": 5},
    "last_trade_volume": {"type": "int", "nullable": True, "precision": 0},
    "bid_0_price": {"type": "float", "nullable": True, "precision": 5},
    # ... and so on for all required columns
}
```
