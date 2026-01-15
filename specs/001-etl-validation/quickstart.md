# Quick Start Guide: DolphinDB ETL Data Validation Tool

**Feature**: [001-etl-validation](./spec.md) | **Date**: 2026-01-15

## Overview

This guide provides step-by-step instructions to set up and run the DolphinDB ETL Data Validation Tool. The tool validates market price data consistency between two DolphinDB instances and generates detailed Markdown reports.

---

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, Linux, or macOS
- **Conda**: Recommended for environment management (per Constitution Principle II)
- **DolphinDB Access**: Two DolphinDB instances with connection credentials

### DolphinDB Requirements

- Two DolphinDB instances (can be on same or different hosts)
- Access to `marekt_price` table (note: table name is spelled with "marekt", not "market")
- User account with read permissions on the database
- Network connectivity from validation tool to both instances

---

## Installation

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd etl-validation-tools
```

### Step 2: Create Conda Environment

```bash
conda create -n etl-validation python=3.8
conda activate etl-validation
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies**:
- `dolphindb` - Official DolphinDB Python client
- `pandas` - Data manipulation and comparison
- `retrying` - Retry logic with exponential backoff
- `configparser` - INI configuration parsing (Python standard library)
- `argparse` - Command-line argument parsing (Python standard library)

**Verify Installation**:

```bash
python -c "import dolphindb; import pandas; import retrying; print('All dependencies installed')"
```

---

## Configuration

### Step 4: Create Configuration File

Create a file named `db_connections.ini` in the `config/` directory:

```bash
mkdir -p config
```

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

**Configuration Parameters**:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `host` | DolphinDB server hostname or IP address | `localhost`, `192.168.1.100` |
| `port` | DolphinDB server port number | `8848` (default DolphinDB port) |
| `username` | Authentication username | `admin` |
| `password` | Authentication password | `123456` |
| `database` | Target database name | `market_data` |

**Notes**:
- `[instance_left]` and `[instance_right]` section names are fixed
- Replace placeholder values with your actual DolphinDB credentials
- Do not commit credentials to version control

---

## Usage

### Step 5: Run Full Validation

Validate all three product type groups (BOND/TRADE, BOND/QUOTE, BOND_FUT/SNAPSHOT) for a specific business date:

```bash
python -m etl_validator \
  --config config/db_connections.ini \
  --date 20260115
```

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

### Step 6: Run Single Step Validation

Validate only a specific product type group:

```bash
# Step 1: BOND/TRADE
python -m etl_validator \
  --config config/db_connections.ini \
  --date 20260115 \
  --step 1

# Step 2: BOND/QUOTE
python -m etl_validator \
  --config config/db_connections.ini \
  --date 20260115 \
  --step 2

# Step 3: BOND_FUT/SNAPSHOT
python -m etl_validator \
  --config config/db_connections.ini \
  --date 20260115 \
  --step 3
```

---

## Understanding Reports

### Report Location

Reports are generated in the `reports/` directory (created automatically in current working directory):

```bash
ls reports/
```

**Output**:
```
validation_BOND_TRADE_20260115.md
validation_BOND_QUOTE_20260115.md
validation_BOND_FUT_SNAPSHOT_20260115.md
```

---

### Report Structure

Each report contains:

1. **Header**: Validation group, date, and generation timestamp
2. **Summary Table**: Records retrieved from each instance
3. **Match Results**: Total matched and unmatched record counts
4. **Unmatched by Column**: Which columns had differences and how many
5. **Unmatched by Side**: Records only in left vs. only in right instance

**Example Report**:

```markdown
# Validation Report: BOND/TRADE

**Validation Date**: 20260115
**Generated At**: 2026-01-15 14:32:15

## Summary

| Metric | Left Instance | Right Instance |
|--------|---------------|----------------|
| Records Retrieved | 45,234 | 45,198 |

## Match Results

- **Matched Records**: 45,123
- **Unmatched Records**: 186

### Unmatched by Column

| Column Name | Differences |
|-------------|-------------|
| last_trade_price | 12 |
| bid_0_price | 8 |
| offer_0_price | 5 |

### Unmatched by Side

| Side | Records |
|------|---------|
| Left Only | 98 |
| Right Only | 88 |
```

---

## Common Use Cases

### Use Case 1: Daily Data Quality Check

Run full validation every morning to verify data consistency across instances:

```bash
# Get yesterday's date in YYYYMMDD format
YESTERDAY=$(date -d "yesterday" +%Y%m%d)

# Run validation
python -m etl_validator \
  --config config/db_connections.ini \
  --date $YESTERDAY
```

---

### Use Case 2: Investigate Specific Product Type

When issues are reported for a specific product type, validate only that group:

```bash
# Investigate BOND_QUOTE issues
python -m etl_validator \
  --config config/db_connections.ini \
  --date 20260115 \
  --step 2

# Review report
cat reports/validation_BOND_QUOTE_20260115.md
```

---

### Use Case 3: Test New DolphinDB Instance

Compare production to staging instance to verify data consistency:

```bash
# Create config for production vs staging
cat > config/prod_staging.ini << EOF
[instance_left]
host = production-db.example.com
port = 8848
username = admin
password = prod_password
database = market_data

[instance_right]
host = staging-db.example.com
port = 8848
username = admin
password = staging_password
database = market_data
EOF

# Run validation
python -m etl_validator \
  --config config/prod_staging.ini \
  --date 20260115
```

---

## Troubleshooting

### Error: Configuration file not found

**Problem**: The INI file path is incorrect or file does not exist.

**Solution**:
```bash
# Verify file exists
ls config/db_connections.ini

# Use absolute path if needed
python -m etl_validator \
  --config /full/path/to/config/db_connections.ini \
  --date 20260115
```

---

### Error: Invalid date format

**Problem**: Date is not in YYYYMMDD format.

**Solution**:
```bash
# Correct format (YYYYMMDD)
python -m etl_validator --config config/db_connections.ini --date 20260115

# Incorrect format (will fail)
python -m etl_validator --config config/db_connections.ini --date 2026-01-15
```

---

### Error: Connection test failed

**Problem**: Cannot connect to DolphinDB instance.

**Solution**:
1. Verify DolphinDB is running: `telnet <host> <port>`
2. Check network connectivity and firewall rules
3. Verify username and password are correct
4. Check if database exists on the instance

```bash
# Test connection manually (if dolphindb installed)
python -c "
from dolphindb.session import Session
session = Session('localhost', 8848, 'admin', '123456')
print('Connected successfully')
"
```

---

### Error: No records retrieved

**Problem**: Query returns zero records for the specified date.

**Solution**:
1. Verify date exists in database: `SELECT business_date FROM market_price LIMIT 10`
2. Check if table has data for the date
3. Verify database name in config is correct
4. Confirm table name is `market_price` (not `marekt_price`)

---

### Performance: Validation takes too long

**Problem**: Full validation exceeds 5 minutes.

**Solution**:
1. Run single step to identify slow group
2. Check if instance has >2,000,000 records (tool uses chunked processing)
3. For large datasets (2M records), expected time is 9-15 minutes for all 3 groups
4. Consider breaking validation into smaller date ranges
5. Check network latency to DolphinDB instances

**Note**: The tool uses chunked processing (100k records per chunk) to handle up to 2M records within memory constraints. This increases execution time for large datasets but ensures memory usage stays under 2GB.

---

### Memory: Out of memory error

**Problem**: Tool exceeds memory limit with large datasets.

**Solution**:
1. Verify dataset size: `SELECT count(*) FROM marekt_price WHERE business_date = 2026.01.15`
2. If >2M records, consider running validation for smaller date ranges
3. Close other applications consuming memory
4. The tool is designed for <2GB memory usage with 2M records (chunked processing)
4. Use a machine with more RAM

---

## Help and Documentation

### View Command Help

```bash
python -m etl_validator --help
```

### Check Version

```bash
python -m etl_validator --version
```

### View README

```bash
cat README.md
```

---

## Next Steps

After running validation:

1. **Review Reports**: Open Markdown files in `reports/` directory
2. **Investigate Differences**: Focus on columns with high difference counts
3. **Fix Root Causes**: Address data inconsistencies in source systems
4. **Re-run Validation**: Verify fixes resolved the issues

---

## Advanced Usage

### Batch Validation with Multiple Dates

```bash
# Validate last 7 days
for i in {0..6}; do
  DATE=$(date -d "$i days ago" +%Y%m%d)
  python -m etl_validator --config config/db_connections.ini --date $DATE
done
```

### Automate with Cron (Linux)

```bash
# Edit crontab
crontab -e

# Add daily validation at 2 AM
0 2 * * * cd /path/to/etl-validation-tools && python -m etl_validator --config config/db_connections.ini --date $(date -d 'yesterday' +\%Y\%m\%d) >> logs/validation.log 2>&1
```

---

## Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [CLI Interface Contract](./contracts/cli-interface.md) for detailed argument documentation
3. Check [Data Model](./data-model.md) for entity definitions
4. Review [Implementation Plan](./plan.md) for technical details

---

**Version**: 1.0.0 | **Last Updated**: 2026-01-15
