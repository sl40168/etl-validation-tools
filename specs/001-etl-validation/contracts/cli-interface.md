# CLI Interface Contract

**Feature**: [001-etl-validation](../spec.md) | **Date**: 2026-01-15

## Overview

Defines the command-line interface for the DolphinDB ETL Data Validation Tool, including arguments, parameters, exit codes, and input/output specifications.

---

## Command Syntax

```bash
python -m etl_validator --config <path> --date <YYYYMMDD> [--step <1|2|3>]
```

---

## Arguments

| Argument | Type | Required | Description | Example |
|----------|------|----------|-------------|----------|
| `--config` | String | Yes | Path to INI configuration file containing DolphinDB connection details | `--config config/db_connections.ini` |
| `--date` | String | Yes | Business date to validate in YYYYMMDD format | `--date 20260115` |
| `--step` | Integer | No | Validation step number (1, 2, or 3) to execute. If not provided, executes all three steps. | `--step 1` |

---

## Argument Details

### `--config`

**Description**: Path to INI configuration file with DolphinDB connection details for two instances.

**Format**: Must be a valid file path pointing to an INI file with `[instance_left]` and `[instance_right]` sections.

**Required Fields** (per section):
- `host`: DolphinDB server hostname or IP
- `port`: DolphinDB server port (1-65535)
- `username`: Authentication username
- `password`: Authentication password
- `database`: Target database name

**Validation**:
- File must exist and be readable
- INI format must be valid
- Both `[instance_left]` and `[instance_right]` sections must exist
- All required fields must be present in each section
- Connection test will be performed before validation starts

**Errors**:
- `Error: Configuration file not found: <path>` - File does not exist
- `Error: Invalid INI format in configuration file` - INI parsing failed
- `Error: Missing required section: [instance_left] or [instance_right]` - Section missing
- `Error: Missing required field: <field> in section [instance_<side>]` - Field missing
- `Error: Connection test failed for instance_<side>: <reason>` - Cannot connect to DolphinDB

---

### `--date`

**Description**: Business date to validate in YYYYMMDD format. This date is formatted as YYYY.MM.DD when building the SQL query.

**Format**: 8-digit string in format YYYYMMDD (e.g., 20260115).

**Validation**:
- Must be 8 characters long
- Must be numeric only
- Must represent a valid date (e.g., 20261301 is invalid, 20260230 is invalid)
- Year range: 2000-2099

**Errors**:
- `Error: Invalid date format: <value>. Expected YYYYMMDD (e.g., 20260115)` - Format incorrect
- `Error: Invalid date: <value>. Date does not exist.` - Date is invalid (e.g., February 30)

---

### `--step`

**Description**: Optional parameter to execute only a specific validation step instead of all three.

**Format**: Integer value 1, 2, or 3.

**Step Mapping**:

| Step | Product Type | Tick Type | Description |
|------|--------------|------------|-------------|
| 1 | BOND | TRADE | Bond trade data validation |
| 2 | BOND | QUOTE | Bond quote data validation |
| 3 | BOND_FUT | SNAPSHOT | Bond futures snapshot data validation |

**Validation**:
- If provided, must be exactly 1, 2, or 3
- Only one `--step` parameter is allowed (multiple values result in error)

**Errors**:
- `Error: Invalid step number: <value>. Must be 1, 2, or 3` - Value out of range
- `Error: Multiple --step parameters provided. Only one step number is allowed.` - Multiple values

---

## Execution Modes

### Mode 1: Full Validation (All Steps)

Executes all three validation groups in sequence.

```bash
python -m etl_validator --config config/db_connections.ini --date 20260115
```

**Behavior**:
1. Validate configuration and test connections
2. Execute Step 1 (BOND/TRADE)
   - Retrieve data from both instances
   - Match records
   - Compare columns
   - Generate report: `reports/validation_BOND_TRADE_20260115.md`
3. Execute Step 2 (BOND/QUOTE)
   - Same process as Step 1
   - Generate report: `reports/validation_BOND_QUOTE_20260115.md`
4. Execute Step 3 (BOND_FUT/SNAPSHOT)
   - Same process as Step 1
   - Generate report: `reports/validation_BOND_FUT_SNAPSHOT_20260115.md`
5. Summary output to stdout

**Output**:
```
Starting validation for date: 20260115
Configuration loaded from: config/db_connections.ini
Connection tests passed

[Step 1/3] Validating BOND/TRADE...
  Retrieved: 45,234 records from left, 45,198 records from right
  Matched: 45,123 pairs
  Unmatched: 186 records
  Report generated: reports/validation_BOND_TRADE_20260115.md ✓

[Step 2/3] Validating BOND/QUOTE...
  Retrieved: 67,891 records from left, 67,845 records from right
  Matched: 67,789 pairs
  Unmatched: 158 records
  Report generated: reports/validation_BOND_QUOTE_20260115.md ✓

[Step 3/3] Validating BOND_FUT/SNAPSHOT...
  Retrieved: 23,456 records from left, 23,412 records from right
  Matched: 23,345 pairs
  Unmatched: 178 records
  Report generated: reports/validation_BOND_FUT_SNAPSHOT_20260115.md ✓

Validation complete. See reports/ directory for details.
```

---

### Mode 2: Single Step Validation

Executes only one specific validation group.

```bash
python -m etl_validator --config config/db_connections.ini --date 20260115 --step 2
```

**Behavior**:
1. Validate configuration and test connections
2. Execute Step 2 only (BOND/QUOTE)
3. Generate report: `reports/validation_BOND_QUOTE_20260115.md`
4. Summary output to stdout

**Output**:
```
Starting validation for date: 20260115
Configuration loaded from: config/db_connections.ini
Connection tests passed

[Step 2/3] Validating BOND/QUOTE...
  Retrieved: 67,891 records from left, 67,845 records from right
  Matched: 67,789 pairs
  Unmatched: 158 records
  Report generated: reports/validation_BOND_QUOTE_20260115.md ✓

Validation complete. See reports/ directory for details.
```

---

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | All validation steps completed successfully |
| 1 | Configuration Error | Invalid or missing configuration file |
| 2 | Argument Error | Invalid command-line arguments |
| 3 | Connection Error | Failed to connect to DolphinDB instance |
| 4 | Query Error | Failed to execute query or retrieve data |
| 5 | Validation Error | Unexpected error during validation process |

**Error Examples**:

```bash
# Configuration error
$ python -m etl_validator --config missing.ini --date 20260115
Error: Configuration file not found: missing.ini

# Argument error
$ python -m etl_validator --config config.ini --date 20260115 --step 4
Error: Invalid step number: 4. Must be 1, 2, or 3
Exit code: 2

# Connection error
$ python -m etl_validator --config config.ini --date 20260115
Error: Connection test failed for instance_left: Connection refused
Exit code: 3
```

---

## Output Specification

### Standard Output (stdout)

**Format**: Human-readable progress and summary messages.

**Content**:
- Configuration loading confirmation
- Connection test results
- Progress per validation step (retrieved, matched, unmatched counts)
- Report file generation confirmation
- Completion message

**No structured data (JSON) on stdout** (per Constitution Principle I).

---

### Standard Error (stderr)

**Format**: Human-readable error messages.

**Content**:
- All error messages (configuration, argument, connection, query, validation)
- Retry notifications (if connection/query fails)
- Stack traces for unexpected errors (debug mode only)

---

### Report Files

**Format**: Markdown (.md files)

**Location**: `reports/` subdirectory in current working directory

**Filenames**:
- `validation_BOND_TRADE_{YYYYMMDD}.md`
- `validation_BOND_QUOTE_{YYYYMMDD}.md`
- `validation_BOND_FUT_SNAPSHOT_{YYYYMMDD}.md`

**Content** (per file):
- Validation group (product_type/tick_type)
- Validation date
- Generation timestamp
- Summary table (records retrieved from each instance)
- Match results (matched count, unmatched count)
- Unmatched by column (column name → difference count)
- Unmatched by side (left only, right only)

**Example**: See `data-model.md` for detailed report structure.

---

## Help Command

```bash
python -m etl_validator --help
```

**Output**:
```
DolphinDB ETL Data Validation Tool

Usage: python -m etl_validator --config <path> --date <YYYYMMDD> [--step <1|2|3>]

Arguments:
  --config PATH    Path to INI configuration file with DolphinDB connection details
  --date YYYYMMDD   Business date to validate (format: YYYYMMDD)
  --step N          Optional: Execute only validation step N (1, 2, or 3)

Validation Steps:
  1  BOND/TRADE data
  2  BOND/QUOTE data
  3  BOND_FUT/SNAPSHOT data

Examples:
  python -m etl_validator --config config/db_connections.ini --date 20260115
  python -m etl_validator --config config/db_connections.ini --date 20260115 --step 1

For more information, see README.md
```

---

## Version Command

```bash
python -m etl_validator --version
```

**Output**:
```
etl-validator version 1.0.0
```

---

## Environment Variables

No environment variables are used. All configuration is provided via the `--config` INI file.

---

## Retry Behavior

**Retry Scope**: Connection failures and query errors only.

**Retry Configuration**:
- Maximum attempts: 3
- Wait strategy: Exponential backoff (1s, 2s, 4s)
- Retry on errors:
  - Connection timeouts
  - Network errors
  - Query execution failures

**No retry on**:
- Configuration errors
- Argument errors
- Authentication failures (wrong username/password)

**Retry Output**:
```
[Step 1/3] Validating BOND/TRADE...
  Retrying connection to instance_left... (attempt 2/3)
  Retrying connection to instance_left... (attempt 3/3)
Error: Connection test failed for instance_left after 3 attempts: Connection timeout
Exit code: 3
```

---

## Performance Requirements

Based on success criteria:

| Metric | Requirement |
|--------|-------------|
| Full validation (all 3 steps) | <5 minutes (for typical datasets) |
| Single step validation | <2 minutes (for typical datasets) |
| Report generation | <30 seconds |
| Max records per instance | 2,000,000 |

**Note**: For very large datasets (2M records), execution time may exceed 5 minutes due to chunked processing required for memory constraints. Expected time for 2M records: 9-15 minutes for all 3 groups.

---

## Platform Compatibility

- **Python Version**: 3.8+
- **Operating Systems**: Windows, Linux, macOS
- **Dependencies**: See `requirements.txt` in repository root

---

## Example Configuration File

**File**: `config/db_connections.ini`

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

## Testing the CLI

### Smoke Test

```bash
# Test with invalid arguments (should fail gracefully)
python -m etl_validator --config invalid.ini --date 20260115

# Test help (should display help text)
python -m etl_validator --help

# Test with valid config (should execute)
python -m etl_validator --config config/db_connections.ini --date 20260115
```

### Integration Test

```bash
# Test single step
python -m etl_validator --config config/db_connections.ini --date 20260115 --step 1

# Verify report file exists
ls reports/validation_BOND_TRADE_20260115.md

# Verify report content
cat reports/validation_BOND_TRADE_20260115.md
```
