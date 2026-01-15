# Implementation Plan: Group-Based Column Validation

**Branch**: `001-group-based-validation` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-group-based-validation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement group-based column validation system that validates data from two DolphinDB instances based on predefined validation groups (BOND/TRADE, BOND/QUOTE, BOND_FUT/SNAPSHOT). Each group has specific required columns that must be validated, and users can validate a single group via --step parameter or all groups sequentially. The system will handle up to 2M records per group using chunked processing and generate detailed Markdown reports with column-level validation results.

## Technical Context

**Language/Version**: Python 3.8+
**Primary Dependencies**: dolphindb>=1.30.0, pandas>=1.3.0, retrying>=1.3.3
**Storage**: DolphinDB (external), INI config files, CSV/JSON reports
**Testing**: pytest>=7.0.0, pytest-mock>=3.6.0
**Target Platform**: Cross-platform (Windows, Linux, macOS)
**Project Type**: Single (CLI application)
**Performance Goals**: 3-5 minutes per group for 2M records using chunked processing
**Constraints**: <100MB memory during validation, CLI-only interface (no web UI), standalone executable
**Scale/Scope**: 3 validation groups, 18-60 columns per group, up to 2M records per group

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Pre-Phase 1)

### Principle I: CLI-First Architecture ✅ PASS
- All functionality is CLI-accessible via argparse
- Text-based I/O: stdin/arguments for input, stdout for output, errors to stderr
- Supports both JSON and human-readable formats in reports
- Ensures scriptability and integration with automation pipelines

### Principle II: Python 3.8+ with Conda ✅ PASS
- Targets Python 3.8+ compatibility
- Dependencies listed in requirements.txt for reproducibility
- Uses virtual environment (venv/conda) for environment management

### Principle III: Standalone Application ✅ PASS
- Built as standalone executable with minimal runtime dependencies
- No external services or databases required for core functionality
- Only external dependency is DolphinDB (data source, not core logic)

### Principle IV: Simplicity & Maintainability ✅ PASS
- Follows YAGNI principles
- Explicit, readable code over clever optimizations
- Favoring functional decomposition with clear module boundaries

### Principle V: Testability ✅ PASS
- Core validation logic independently testable
- Unit tests for individual validators
- Integration tests for end-to-end ETL workflows

### Technology Constraints ✅ PASS
- Language: Python 3.8+ ✅
- Package Manager: Conda/venv ✅
- Dependency Tracking: requirements.txt ✅
- External Services: None for core logic ✅
- Database: File-based storage only (reports as MD/CSV) ✅
- Platform Support: Cross-platform ✅

---

### Re-Check (Post-Phase 1 Design)

All constitution principles continue to PASS after Phase 1 design completion.

**Design Verification**:
- CLI interface contract validates all command-line parameters follow text-based protocol ✅
- Data model confirms standalone file-based storage (Markdown reports) ✅
- Validation logic design maintains testability with clear module boundaries ✅
- No additional external services or dependencies introduced ✅
- Performance goals (3-5 min per 2M records) align with standalone constraint ✅

**Agent Context Updated**: CODEBUDDY.md updated with current technology stack (Python 3.8+, dolphindb, pandas, retrying).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
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
├── __main__.py
├── cli/
│   ├── __init__.py
│   └── main.py                    # CLI entry point with argparse
├── config/
│   ├── __init__.py
│   └── loader.py                  # INI config loading and validation
├── db/
│   ├── __init__.py
│   ├── connection.py              # DolphinDB connection wrapper
│   └── query.py                   # Data retrieval with chunking
├── reporting/
│   ├── __init__.py
│   ├── formatter.py               # Report formatting
│   └── generator.py               # Markdown report generation
├── utils/
│   ├── __init__.py
│   ├── date_helpers.py            # Date parsing and formatting
│   └── retry.py                   # Retry logic with exponential backoff
└── validation/
    ├── __init__.py
    ├── groups.py                  # Validation group definitions
    ├── matcher.py                 # Record matching logic
    └── comparator.py              # Column comparison logic

tests/
├── __init__.py
├── unit/
│   ├── test_groups.py             # Validation group tests
│   ├── test_matcher.py            # Matcher tests
│   ├── test_comparator.py         # Comparator tests
│   └── test_date_helpers.py       # Date utility tests
└── integration/
    ├── test_cli.py                # CLI end-to-end tests
    └── test_validation_flow.py    # Full validation workflow tests

config/
├── db_connections.ini             # DolphinDB connection configuration
└── db_connections_example.ini     # Template for connection config

reports/                           # Generated validation reports (auto-created)
```

**Structure Decision**: Single project structure (Option 1) with clear module separation: cli (interface), config (configuration), db (data access), reporting (output), utils (helpers), validation (core logic). Tests organized by unit (isolated component tests) and integration (end-to-end workflow tests).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations found. Complexity tracking not required.
