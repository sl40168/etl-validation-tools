<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0
- Modified principles: All 5 placeholder principles replaced with project-specific principles
- Added sections: Technology Constraints, Development Workflow
- Removed sections: None
- Templates requiring updates:
  ✅ .specify/templates/plan-template.md - verified alignment
  ✅ .specify/templates/spec-template.md - verified alignment
  ✅ .specify/templates/tasks-template.md - verified alignment
  ⚠ README.md - does not exist, should be created
- Follow-up TODOs: None
-->

# ETL Validation Tools Constitution

## Core Principles

### I. CLI-First Architecture

All functionality MUST be accessible via command-line interface. Text-based I/O protocol: stdin/arguments for input → stdout for output, errors → stderr. Support both JSON and human-readable formats. Rationale: Ensures scriptability, integration with automation pipelines, and debugging transparency.

### II. Python 3.8+ with Conda

Project MUST target Python 3.8+ compatibility. Virtual environment MUST be managed using Conda. All dependencies MUST be recorded in `requirements.txt` for reproducibility and ease of setup. Rationale: Standardizes development environment, ensures cross-platform compatibility, and simplifies dependency management for all users.

### III. Standalone Application

Application MUST be built as a standalone executable with minimal runtime dependencies. MUST NOT require external services or databases for core functionality. Rationale: Ensures portability, reduces deployment complexity, and enables offline usage.

### IV. Simplicity & Maintainability

Code MUST follow YAGNI (You Ain't Gonna Need It) principles. Avoid unnecessary abstractions and complexity. Favor explicit, readable code over clever optimizations. Rationale: Reduces cognitive load for contributors, lowers bug count, and speeds up feature development.

### V. Testability

Core validation logic MUST be independently testable. Unit tests MUST cover individual validators. Integration tests MUST verify end-to-end ETL workflows. Rationale: Ensures reliability of data validation logic and provides confidence in refactoring.

## Technology Constraints

- Language: Python 3.8 or higher (NO Python 3.7 or earlier)
- Package Manager: Conda for environment management
- Dependency Tracking: All Python packages MUST be listed in `requirements.txt`
- External Services: None permitted for core functionality
- Database: File-based storage only (JSON, CSV, YAML, etc.) - NO external databases
- Platform Support: Cross-platform (Windows, Linux, macOS) via Python

## Development Workflow

### Code Review

All code changes MUST pass:
- Linting (flake8 or equivalent)
- Type checking (mypy recommended but optional)
- Unit tests (pytest)
- Manual CLI smoke tests

### Version Management

Follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes to CLI interface or file formats
- MINOR: New features, backward-compatible changes
- PATCH: Bug fixes, documentation updates

### Documentation

Public CLI commands MUST have:
- `--help` documentation for all commands
- Usage examples in README.md
- Inline docstrings for all public functions

## Governance

This constitution supersedes all ad-hoc practices. Amendments require:
1. Written proposal justifying the change
2. Impact assessment on existing code
3. Migration plan if backward-incompatible
4. Version bump according to semantic versioning rules

All feature development MUST verify compliance with these principles before implementation begins. Complexity MUST be explicitly justified if it conflicts with Simplicity principle.

**Version**: 1.0.0 | **Ratified**: 2026-01-15 | **Last Amended**: 2026-01-15
