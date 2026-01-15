# Implementation Plan: Group-Based Column Validation

**Branch**: `001-group-based-validation` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-group-based-validation/spec.md`

## Summary

This feature extends the existing ETL validation tool to support group-based column validation for three predefined data groups: BOND TRADE (18 columns), BOND QUOTE (60 columns), and BOND_FUT SNAPSHOT (39 columns). The system validates data from two DolphinDB instances by matching records on composite keys (receive_time, exch_product_id, settle_speed), comparing column values with precision-aware rounding, and generating Markdown reports. Groups are selected via CLI `--step` parameter (1-3), with chunked processing to handle up to 2M records per group within 3-5 minutes.

## Technical Context

**Language/Version**: Python 3.8+
**Primary Dependencies**: dolphindb (DolphinDB SDK), pandas (data manipulation), retrying (retry logic)
**Storage**: DolphinDB instances (external, not in scope), Markdown reports (file-based)
**Testing**: pytest
**Target Platform**: Cross-platform (Windows, Linux, macOS)
**Project Type**: CLI application (standalone)
**Performance Goals**: 2,000,000 records per group validated in 3-5 minutes
**Constraints**: Memory limit < 2GB, chunked processing (100k rows/chunk), precision-aware comparison (volumes: integer, prices/yields: 5 decimals)
**Scale/Scope**: 3 validation groups, 117 total columns across all groups, 2M records max per group

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. CLI-First Architecture
✅ **PASS**: All functionality accessible via CLI with `--config`, `--date`, `--step` arguments. Output to stdout (human-readable) and Markdown reports (file-based). Errors to stderr.

### II. Python 3.8+ with Conda
✅ **PASS**: Targeting Python 3.8+ compatibility. Dependencies in `requirements.txt`. Conda for environment management.

### III. Standalone Application
✅ **PASS**: CLI tool with minimal runtime dependencies. No external services required (DolphinDB is data source, not core functionality). Core validation logic works independently.

### IV. Simplicity & Maintainability
✅ **PASS**: Following YAGNI - building on existing validated patterns from 001-etl-validation. No unnecessary abstractions. Vectorized pandas operations for performance.

### V. Testability
✅ **PASS**: Core validation logic independently testable via pytest. Unit tests for individual validators. Integration tests for end-to-end ETL workflows.

## Project Structure

### Documentation (this feature)

```text
specs/001-group-based-validation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── validation/          # Validation logic
│   ├── group_definitions.py  # Group column definitions
│   ├── column_validator.py   # Column-level validation
│   └── result_reporter.py    # Report generation
├── db/                  # DolphinDB integration
│   ├── connector.py          # Connection and query logic
│   └── data_fetcher.py      # Chunked data retrieval
├── reporting/           # Report generation
│   └── markdown_generator.py # Markdown report creation
├── cli/                 # CLI interface
│   └── group_validator.py    # --step parameter handling
├── config/              # Configuration management
│   └── group_config.py       # Group configuration loader
└── utils/               # Utilities
    ├── precision.py          # Precision-aware rounding
    └── memory.py             # Memory management helpers

tests/
├── contract/            # Contract tests (CLI interface)
├── integration/         # End-to-end ETL workflows
└── unit/               # Unit tests for validators
```

**Structure Decision**: Extending existing 001-etl-validation structure with new `validation/group_definitions.py` for group-specific column lists, `cli/group_validator.py` for --step parameter handling, and reusing existing `db/connector.py`, `reporting/markdown_generator.py`, and utilities.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All constitution principles are satisfied.

---
