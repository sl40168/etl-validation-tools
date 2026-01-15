# CLI Interface Contract

**Feature**: Group-Based Column Validation
**Version**: 1.0.0
**Date**: 2026-01-15

## Command Structure

```bash
python -m etl_validator --config <path> --date <YYYYMMDD> [--step <1|2|3>]
```

## Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `--config` | string | Path to INI configuration file with DolphinDB connection details | `config/dolphindb.ini` |
| `--date` | string | Business date in YYYYMMDD format | `20260115` |

### Optional Parameters

| Parameter | Type | Description | Default | Values |
|-----------|------|-------------|----------|--------|
| `--step` | integer | Validation step to execute | `None` (all steps) | `1`, `2`, `3` |

## Step Mapping

| Step Value | Product Type | Message Type | Column Count |
|------------|--------------|---------------|--------------|
| 1 | BOND | TRADE | 18 |
| 2 | BOND | QUOTE | 60 |
| 3 | BOND_FUT | SNAPSHOT | 39 |

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Validation completed successfully |
| 1 | Error | Configuration file not found or invalid |
| 2 | Error | Invalid date format (must be YYYYMMDD) |
| 3 | Error | Invalid step value (must be 1, 2, or 3) |
| 4 | Error | DolphinDB connection failed |
| 5 | Error | Data retrieval failed |
| 6 | Error | Validation failed (data quality issues) |
| 7 | Error | Report generation failed |
| 8 | Error | Unexpected error |

## Output Format

### Standard Output (stdout)

Human-readable progress messages:

```
[INFO] Connecting to DolphinDB instances...
[INFO] Loading configuration from config/dolphindb.ini
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
```

### Standard Error (stderr)

Error messages with details:

```
[ERROR] Configuration file not found: config/dolphindb.ini
[ERROR] Connection failed to left instance: timeout
[ERROR] Invalid date format: 2026-01-15 (expected YYYYMMDD)
[ERROR] Validation failed: Missing column 'last_trade_price' in dataset
```

### Report Files

Markdown reports generated per group:

**Location**: `reports/001-group-based-validation/`

**Filename Pattern**: `{product_type}_{message_type}_{date}.md`

**Examples**:
- `bond_trade_20260115.md`
- `bond_quote_20260115.md`
- `bond_fut_snapshot_20260115.md`

## Configuration File Format

INI format with two sections:

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

## Usage Examples

### Validate All Groups (Sequential)

```bash
python -m etl_validator --config config/dolphindb.ini --date 20260115
```

Output:
- Runs steps 1, 2, 3 sequentially
- Generates 3 reports

### Validate Single Group (BOND TRADE)

```bash
python -m etl_validator --config config/dolphindb.ini --date 20260115 --step 1
```

Output:
- Runs step 1 only
- Generates 1 report: `bond_trade_20260115.md`

### Validate Single Group (BOND QUOTE)

```bash
python -m etl_validator --config config/dolphindb.ini --date 20260115 --step 2
```

Output:
- Runs step 2 only
- Generates 1 report: `bond_quote_20260115.md`

### Validate Single Group (BOND_FUT SNAPSHOT)

```bash
python -m etl_validator --config config/dolphindb.ini --date 20260115 --step 3
```

Output:
- Runs step 3 only
- Generates 1 report: `bond_fut_snapshot_20260115.md`

## Help Command

```bash
python -m etl_validator --help
```

Output:

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

## Error Handling

### Configuration Errors

**Missing or invalid config file**:
```
[ERROR] Configuration file not found or invalid: config/dolphindb.ini
[ERROR] Please ensure the file exists and contains valid INI format
Exit code: 1
```

### Connection Errors

**DolphinDB connection failure**:
```
[INFO] Connecting to DolphinDB instances...
[ERROR] Connection failed to left instance: timeout
[INFO] Retrying... (attempt 2/3)
[ERROR] Connection failed to left instance: timeout
[INFO] Retrying... (attempt 3/3)
[ERROR] Connection failed to left instance: timeout
[ERROR] Max retry attempts reached. Aborting.
Exit code: 4
```

### Validation Errors

**Missing required columns**:
```
[INFO] Validating columns...
[ERROR] Column validation: FAIL
[ERROR] Missing columns: last_trade_price, last_trade_volume
[INFO] Validation complete: FAILED (data quality issues)
Exit code: 6
```

### Date Format Errors

**Invalid date format**:
```
[ERROR] Invalid date format: 2026-01-15
[ERROR] Expected format: YYYYMMDD (e.g., 20260115)
Exit code: 2
```

### Step Value Errors

**Invalid step value**:
```
[ERROR] Invalid step value: 4
[ERROR] Step must be 1 (BOND TRADE), 2 (BOND QUOTE), or 3 (BOND_FUT SNAPSHOT)
Exit code: 3
```

## Performance Indicators

### Progress Messages

```
[INFO] Processing chunk 1/20 (0-100,000 rows)...
[INFO] Processing chunk 2/20 (100,000-200,000 rows)...
...
[INFO] Processing chunk 20/20 (1,900,000-2,000,000 rows)...
```

### Time Estimates

```
[INFO] Estimated completion time: 3-5 minutes for 2,000,000 records
```

### Memory Usage

```
[INFO] Current memory usage: 1.2GB / 2GB limit
```
