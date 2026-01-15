# Implementation Plan: DolphinDB ETL Data Validation Tool

**Branch**: `001-etl-validation` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-etl-validation/spec.md`

**Note**: This template is filled in by `/speckit.plan` command. See `.specify/templates/commands/plan.md` for execution workflow.

## Summary

Build a CLI-based data validation tool that retrieves market price data from two DolphinDB instances (up to 2,000,000 records per instance), matches records across instances using receive_time, exch_product_id, and settle_speed, compares 84 specified columns for matched pairs using chunked processing, and generates separate Markdown reports for each of three validation groups (BOND/TRADE, BOND/QUOTE, BOND_FUT/SNAPSHOT). The tool supports executing all validation steps or a single step, uses INI configuration for connection details, includes 3-retry logic for failures, and outputs reports to a `reports/` subdirectory with meaningful filenames. Chunked processing (100k records per chunk) ensures memory usage stays under 2GB while handling large datasets.

## Technical Context

**Language/Version**: Python 3.8+
**Primary Dependencies**: dolphindb, configparser, pandas (for data comparison), retrying (for retry logic)
**Storage**: INI configuration files, Markdown reports
**Testing**: pytest (unit tests), pytest-mock (for mocking DolphinDB connections)
**Target Platform**: Cross-platform (Windows, Linux, macOS) via Python CLI
**Project Type**: single (standalone CLI application)
**Performance Goals**: Complete full validation (all 3 groups, 2M records each) in under 5 minutes; generate reports within 30 seconds
**Constraints**: <5 minutes for full validation; <2GB memory for 2M records per instance; CLI-first (stdin/args → stdout/stderr); NO external services except DolphinDB; standalone executable with minimal dependencies
**Scale/Scope**: Up to 2,000,000 records per DolphinDB instance; 3 validation groups per execution; 84 columns compared per matched pair

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. CLI-First Architecture ✅ PASS
- Tool accessed via command-line interface with `--config` and `--date` parameters
- Text-based I/O: arguments for input → stdout for output, errors → stderr
- Support both human-readable (Markdown reports) and structured data (internal processing)
- **Rationale Met**: Ensures scriptability, integration with automation pipelines, and debugging transparency
- **Post-Design Validation**: CLI interface defined in [contracts/cli-interface.md](./contracts/cli-interface.md) confirms adherence to Constitution Principle I

### II. Python 3.8+ with Conda ✅ PASS
- Language: Python 3.8+ specified
- All dependencies will be recorded in `requirements.txt`
- **Rationale Met**: Standardizes development environment, ensures cross-platform compatibility
- **Post-Design Validation**: Technology stack (dolphindb, pandas, retrying) compatible with Python 3.8+

### III. Standalone Application ✅ PASS
- Tool is a standalone CLI with minimal runtime dependencies
- Only external dependency is DolphinDB (data source, not application dependency)
- No external services or databases required for core functionality
- **Rationale Met**: Ensures portability, reduces deployment complexity, enables offline usage
- **Post-Design Validation**: Total external dependencies: 3 (dolphindb, pandas, retrying) - minimal and justified

### IV. Simplicity & Maintainability ✅ PASS
- Direct approach: read config → query DB → match records → compare → report
- No unnecessary abstractions (e.g., no ORM layer, no complex frameworks)
- Explicit code structure: config loader, query executor, matcher, comparator, reporter
- **Rationale Met**: Reduces cognitive load, lowers bug count, speeds development
- **Post-Design Validation**: Data model and CLI contract show simple, direct approach with clear separation of concerns

### V. Testability ✅ PASS
- Core validation logic independently testable (matcher, comparator functions)
- Unit tests cover individual components (config parsing, connection retry, column comparison)
- Integration tests verify end-to-end workflows with mocked DolphinDB
- **Rationale Met**: Ensures reliability of data validation logic, provides confidence in refactoring
- **Post-Design Validation**: Test structure defined in [Project Structure](#project-structure) includes unit, integration, and contract tests

**GATE STATUS**: ✅ ALL GATES PASSED (Initial + Post-Design Re-evaluation) - Ready for Phase 2

## Project Structure

### Documentation (this feature)

```text
specs/001-etl-validation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── cli/
│   ├── __init__.py
│   └── main.py              # CLI entry point, argument parsing, orchestration
├── config/
│   ├── __init__.py
│   └── loader.py            # INI config parsing, connection validation
├── db/
│   ├── __init__.py
│   ├── connection.py         # DolphinDB connection with retry logic
│   └── query.py             # Query execution, result retrieval
├── validation/
│   ├── __init__.py
│   ├── matcher.py           # Record matching by receive_time, exch_product_id, settle_speed
│   ├── comparator.py        # 84-column comparison for matched pairs
│   └── groups.py           # Validation group definitions (BOND/TRADE, BOND/QUOTE, BOND_FUT/SNAPSHOT)
├── reporting/
│   ├── __init__.py
│   ├── generator.py         # Markdown report generation
│   └── formatter.py        # Report statistics formatting
└── utils/
    ├── __init__.py
    └── retry.py            # Retry utility (3 attempts, exponential backoff)

tests/
├── unit/
│   ├── test_config_loader.py
│   ├── test_connection.py
│   ├── test_query.py
│   ├── test_matcher.py
│   ├── test_comparator.py
│   └── test_retry.py
├── integration/
│   ├── test_validation_workflow.py
│   └── test_report_generation.py
└── fixtures/
    ├── config_example.ini
    └── sample_data.csv

config/
└── db_connections_example.ini

reports/                     # Generated at runtime
├── validation_BOND_TRADE_20260115.md
├── validation_BOND_QUOTE_20260115.md
└── validation_BOND_FUT_SNAPSHOT_20260115.md

requirements.txt
setup.py
README.md
```

**Structure Decision**: Single project structure chosen as the tool is a standalone CLI application with no frontend, web services, or platform-specific components. The structure separates concerns (CLI, config, database access, validation logic, reporting) while maintaining simplicity per Constitution Principle IV.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations. Complexity tracking not required.

