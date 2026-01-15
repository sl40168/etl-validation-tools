# Quick Start Guide: Group-Based Column Validation

**Feature**: Group-Based Column Validation
**Version**: 1.0.0
**Last Updated**: 2026-01-15

## Overview

The Group-Based Column Validation feature extends the existing ETL validation tool to support three predefined data groups:
- **BOND TRADE** (18 columns): Validates bond trade data
- **BOND QUOTE** (60 columns): Validates bond quote data across 6 price levels
- **BOND_FUT SNAPSHOT** (39 columns): Validates bond futures snapshot data

The tool validates data from two DolphinDB instances, matching records on composite keys and comparing column values with precision-aware rounding.

---

## Prerequisites

### System Requirements

- Python 3.8 or higher
- Conda (for environment management)
- 2GB available memory
- Access to two DolphinDB instances

### Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `dolphindb` - DolphinDB Python SDK
- `pandas` - Data manipulation
- `retrying` - Retry logic
- `pytest` - Testing

---

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd etl-validation-tools
```

### 2. Create Conda Environment

```bash
conda create -n etl-validation python=3.8
conda activate etl-validation
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -m etl_validator --help
```

Expected output:
```
ETL Data Validation Tool with Group-Based Column Validation

positional arguments:
  None

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG        Path to INI configuration file with DolphinDB connection details
  --date DATE            Business date in YYYYMMDD format
  --step {1,2,3}       Validation step: 1=BOND TRADE, 2=BOND QUOTE, 3=BOND_FUT SNAPSHOT.
                        If not specified, runs all steps sequentially.
```

---

## Configuration

### 1. Create Configuration File

Create `config/dolphindb.ini` with connection details for both instances:

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

### 2. Verify DolphinDB Connections

Test connections to both instances:

```python
from dolphindb import session

# Test left instance
s1 = session.Session()
s1.connect("localhost", 8848, "admin", "123456")
print(f"Left instance connected: {s1.run('version()')}")

# Test right instance
s2 = session.Session()
s2.connect("192.168.1.100", 8848, "admin", "123456")
print(f"Right instance connected: {s2.run('version()')}")
```

---

## Basic Usage

### Validate All Groups

Run validation for all three groups sequentially:

```bash
python -m etl_validator --config config/dolphindb.ini --date 20260115
```

Output:
```
[INFO] Loading configuration from config/dolphindb.ini
[INFO] Connecting to DolphinDB instances...
[INFO] Validating group: BOND TRADE (step 1)
[INFO] Fetching data from left instance...
[INFO] Fetching data from right instance...
[INFO] Validating columns...
[INFO] Column validation: PASS (18/18 columns found)
[INFO] Matching records...
[INFO] Matched 150,000 records
[INFO] Comparing columns...
[INFO] Comparison complete: 23 differences found
[INFO] Generating report...
[INFO] Report saved to: reports/001-group-based-validation/bond_trade_20260115.md
[INFO] Validation complete: SUCCESS

[INFO] Validating group: BOND QUOTE (step 2)
...
[INFO] Validating group: BOND_FUT SNAPSHOT (step 3)
...
[INFO] All validations complete
```

### Validate Single Group

Validate only BOND TRADE (step 1):

```bash
python -m etl_validator --config config/dolphindb.ini --date 20260115 --step 1
```

Validate only BOND QUOTE (step 2):

```bash
python -m etl_validator --config config/dolphindb.ini --date 20260115 --step 2
```

Validate only BOND_FUT SNAPSHOT (step 3):

```bash
python -m etl_validator --config config/dolphindb.ini --date 20260115 --step 3
```

---

## Understanding Reports

Report files are saved to `reports/001-group-based-validation/` with format: `{product_type}_{message_type}_{date}.md`

### Example Report Structure

```markdown
# Group Validation Report: BOND/TRADE

**Group ID**: 1
**Validation Date**: 2026-01-15 14:30:22

## Column Validation Summary

**Status**: PASS

All 18 required columns found:
- business_date ✓
- exch_product_id ✓
- product_type ✓
- exchange ✓
- source ✓
- settle_speed ✓
- last_trade_price ✓
- last_trade_yield ✓
- last_trade_yield_type ✓
- last_trade_volume ✓
- last_trade_turnover ✓
- last_trade_interest ✓
- last_trade_side ✓
- level ✓
- status ✓

## Comparison Results

**Total Records**: 150,000
**Matched Records**: 148,500
**Unmatched Records**: 1,500 (left only: 800, right only: 700)

### Column Differences

| Column Name | Differences | Percentage |
|-------------|-------------|------------|
| last_trade_price | 12 | 0.008% |
| last_trade_volume | 8 | 0.005% |
| settle_speed | 3 | 0.002% |

**Total Differences**: 23 columns affected

### NULL-Aware Passes

Columns where both instances had NULL values (passed validation):
- last_trade_yield: 450 records
- last_trade_interest: 320 records
```

---

## Column Definitions

### BOND TRADE (Step 1) - 18 Columns

| Column | Type | Description |
|--------|------|-------------|
| business_date | datetime | Business date |
| exch_product_id | string | Exchange product identifier |
| product_type | string | Product type code |
| exchange | string | Exchange code |
| source | string | Data source |
| settle_speed | integer | Settlement speed (0 or 1) |
| last_trade_price | float | Last trade price |
| last_trade_yield | float | Last trade yield |
| last_trade_yield_type | string | Last trade yield type |
| last_trade_volume | integer | Last trade volume |
| last_trade_turnover | integer | Last trade turnover |
| last_trade_interest | integer | Last trade interest |
| last_trade_side | string | Last trade side (buy/sell) |
| level | integer | Price level |
| status | string | Record status |

### BOND QUOTE (Step 2) - 60 Columns

Includes 6 bid/offer price levels (0-5), each with:
- `bid_X_price`, `offer_X_price` - Price (5 decimals)
- `bid_X_yield`, `offer_X_yield` - Yield (5 decimals)
- `bid_X_yield_type`, `offer_X_yield_type` - Yield type
- `bid_X_tradable_volume`, `offer_X_tradable_volume` - Tradable volume (integer)
- `bid_X_volume`, `offer_X_volume` - Volume (integer)

Plus base columns (same as BOND TRADE): business_date, exch_product_id, product_type, exchange, source, settle_speed

### BOND_FUT SNAPSHOT (Step 3) - 39 Columns

**Trade Data** (same as BOND TRADE):
- All 18 BOND TRADE columns

**Market Summary** (12 columns):
- `pre_close_price` - Previous close price
- `pre_settle_price` - Previous settlement price
- `pre_interest` - Previous open interest
- `open_price` - Opening price
- `high_price` - High price
- `low_price` - Low price
- `close_price` - Closing price
- `settle_price` - Settlement price
- `upper_limit` - Upper limit price
- `lower_limit` - Lower limit price
- `total_volume` - Total volume
- `total_turnover` - Total turnover
- `open_interest` - Open interest

**Quote Data** (levels 0-1 only, 20 columns):
- Bid/offer levels 0 and 1 with all 10 fields per level

---

## Common Use Cases

### Use Case 1: Daily Data Quality Check

Run all groups validation for today's business date:

```bash
# Get today's date in YYYYMMDD format
DATE=$(date +%Y%m%d)

# Run validation
python -m etl_validator --config config/dolphindb.ini --date $DATE
```

### Use Case 2: Validate Specific Group After ETL

Validate BOND QUOTE data after ETL pipeline completes:

```bash
python -m etl_validator --config config/dolphindb.ini --date 20260115 --step 2
```

### Use Case 3: Historical Validation

Validate historical data for a specific date:

```bash
python -m etl_validator --config config/dolphindb.ini --date 20260110 --step 1
```

### Use Case 4: Automated Scheduled Validation

Create a cron job to run daily validation at 10:00 PM:

```cron
0 22 * * * cd /path/to/etl-validation-tools && /path/to/conda/envs/etl-validation/bin/python -m etl_validator --config config/dolphindb.ini --date $(date +\%Y\%m\%d) >> logs/validation_$(date +\%Y\%m\%d).log 2>&1
```

---

## Troubleshooting

### Connection Errors

**Problem**: `Connection failed to left instance: timeout`

**Solutions**:
1. Verify DolphinDB instances are running: `netstat -an | grep 8848`
2. Check firewall settings
3. Verify host and port in configuration file
4. Check username and password

### Column Validation Errors

**Problem**: `Column validation: FAIL - Missing columns: last_trade_price`

**Solutions**:
1. Verify data exists in DolphinDB for the specified date
2. Check column names in the database match expected names
3. Ensure business_date filter is correct

### Memory Errors

**Problem**: `MemoryError: Unable to allocate array`

**Solutions**:
1. Reduce dataset size (validate fewer days at a time)
2. Close other applications to free memory
3. Check system has at least 2GB available memory

### Date Format Errors

**Problem**: `Invalid date format: 2026-01-15`

**Solution**:
Use YYYYMMDD format: `20260115`

---

## Performance Tips

### Optimize for Large Datasets

The tool processes data in 100,000-row chunks. For 2M records:

- **Expected time**: 3-5 minutes per group
- **Memory usage**: < 2GB peak
- **Recommended**: Run groups sequentially, not in parallel

### Monitor Progress

The tool outputs progress messages for each chunk:

```
[INFO] Processing chunk 1/20 (0-100,000 rows)...
[INFO] Processing chunk 2/20 (100,000-200,000 rows)...
```

### Reduce Validation Time

If validating multiple dates, run validation for each date in a loop:

```bash
for date in 20260110 20260111 20260112; do
    python -m etl_validator --config config/dolphindb.ini --date $date
done
```

---

## Testing

### Run Unit Tests

```bash
pytest tests/unit/
```

### Run Integration Tests

```bash
pytest tests/integration/
```

### Run Contract Tests

```bash
pytest tests/contract/
```

---

## Next Steps

1. Review the full [CLI Interface Contract](contracts/cli-interface.md) for detailed API documentation
2. Read the [Data Model](data-model.md) for entity definitions
3. Check [Research Findings](research.md) for technical decisions
4. Explore the source code in `src/validation/`, `src/cli/`, and `src/db/`

---

## Support

For issues or questions:
1. Check this guide and [CLI Interface Contract](contracts/cli-interface.md)
2. Review logs in `logs/` directory
3. Check report files in `reports/001-group-based-validation/`
4. Contact the development team
