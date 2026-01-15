# DolphinDB ETL Data Validation Tool

A CLI-based data validation tool that retrieves market price data from two DolphinDB instances, matches records, compares 84 columns for matched pairs, and generates detailed Markdown reports.

## Features

- **Data Matching**: Match records from two DolphinDB instances using composite key (receive_time, exch_product_id, settle_speed)
- **Column Comparison**: Compare columns with precision-aware comparison (volumes, prices, yields)
- **Chunked Processing**: Handle up to 2M records per instance with memory-efficient processing
- **Validation Groups**: Support for 3 predefined groups (BOND TRADE, BOND QUOTE, BOND_FUT SNAPSHOT)
  - Step 1: BOND TRADE (18 columns)
  - Step 2: BOND QUOTE (60 columns)
  - Step 3: BOND_FUT SNAPSHOT (39 columns)
- **Retry Logic**: Automatic retry for connection failures and query errors (3 attempts with exponential backoff)
- **Report Generation**: Generate detailed Markdown reports with statistics on matched/unmatched records

## Installation

### Prerequisites

- Python 3.8 or higher
- DolphinDB access credentials

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## Configuration

Create a configuration file (e.g., `config/db_connections.ini`):

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

## Usage

### Run Full Validation (All 3 Groups)

```bash
etl_validator --config config/db_connections.ini --date 20260115
```

### Run Single Step Validation

```bash
# Step 1: BOND TRADE (18 columns)
etl_validator --config config/db_connections.ini --date 20260115 --step 1

# Step 2: BOND QUOTE (60 columns)
etl_validator --config config/db_connections.ini --date 20260115 --step 2

# Step 3: BOND_FUT SNAPSHOT (39 columns)
etl_validator --config config/db_connections.ini --date 20260115 --step 3
```

### Command Options

- `--config`: Path to database configuration file (required)
- `--date`: Business date in YYYYMMDD format (required)
- `--step`: Validation step to run (1=BOND TRADE, 2=BOND QUOTE, 3=BOND_FUT SNAPSHOT). If not specified, runs all steps sequentially
- `--help`: Display help message with all options

## Output

Reports are generated in the `reports/` directory:

- `validation_BOND_TRADE_YYYYMMDD.md`
- `validation_BOND_QUOTE_YYYYMMDD.md`
- `validation_BOND_FUT_SNAPSHOT_YYYYMMDD.md`

## Testing

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit

# Run integration tests only
pytest tests/integration

# Run with coverage
pytest --cov=src tests/
```

## Troubleshooting

### Connection Errors

- Verify DolphinDB instances are running
- Check network connectivity and firewall rules
- Confirm credentials are correct

### Performance Issues

- For large datasets (2M records), expected time is 9-15 minutes for all 3 groups
- The tool uses chunked processing (100k records per chunk) to stay under memory limits
- Consider running validation for smaller date ranges if performance is critical

## License

MIT License
