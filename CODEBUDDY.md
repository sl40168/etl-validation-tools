# etl-validation-tools Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-15

## Active Technologies
- DolphinDB (external database for data retrieval) (006-record-matching)

- Python 3.8+ + dolphindb>=1.30.0, pandas>=1.3.0, retrying>=1.3.3 (001-group-based-validation)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.8+: Follow standard conventions

## Recent Changes
- 006-record-matching: Implemented position-based record matching with SQL-level sorting and BOND_FUT time filtering (09:30-15:00). Default matching strategy changed from composite key to position-based. Old `match_records()` and `match_records_chunked()` functions are deprecated but retained for backward compatibility. Performance improvement: ~40-50% faster (<10s for 10k records vs 12-15s previously).

- 001-group-based-validation: Added Python 3.8+ + dolphindb>=1.30.0, pandas>=1.3.0, retrying>=1.3.3

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
