# Implementation Plan: Record Matching Logic Enhancement

**Branch**: `006-record-matching` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-record-matching/spec.md`

## Summary

Enhance record matching logic to use position-based comparison after sorting records by `receive_time, exch_product_id, settle_speed` in both DolphinDB instances. Add time-based filtering for BOND_FUT data (09:30:00-15:00:00) and replace composite key matching with sequential position matching. This simplifies validation logic while maintaining accuracy for time-series financial data.

## Technical Context

**Language/Version**: Python 3.8+
**Primary Dependencies**: dolphindb>=1.30.0, pandas>=1.3.0, retrying>=1.3.3
**Storage**: DolphinDB (external database for data retrieval)
**Testing**: pytest
**Target Platform**: Cross-platform (Windows, Linux, macOS)
**Project Type**: Single project (CLI application)
**Performance Goals**: <10 seconds for matching 10,000 records
**Constraints**: Standalone CLI tool, no external services for core functionality
**Scale/Scope**: Modifications to existing ETL validation tools, affecting query builder and matcher modules

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| CLI-First Architecture | ✅ Pass | No changes to CLI interface needed |
| Python 3.8+ with Conda | ✅ Pass | Existing codebase uses Python 3.8+ |
| Standalone Application | ✅ Pass | No new external dependencies required |
| Simplicity & Maintainability | ✅ Pass | Simplifies matching logic, reduces complexity |
| Testability | ✅ Pass | Matching logic remains independently testable |

**Technology Constraints Compliance**:
- ✅ Python 3.8+ compatible
- ✅ No external services added (only existing DolphinDB)
- ✅ Cross-platform maintained
- ✅ File-based configuration preserved

## Project Structure

### Documentation (this feature)

```text
specs/006-record-matching/
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
├── config/
│   └── loader.py                    # Configuration loader (unchanged)
├── db/
│   ├── connection.py                 # Connection wrapper (unchanged)
│   └── query.py                    # Query executor (MODIFY: add ORDER BY and time filter)
├── validation/
│   └── matcher.py                  # Record matcher (MODIFY: change to position-based matching)
├── cli/
│   └── main.py                     # CLI entry point (unchanged)
└── utils/
    └── date_helpers.py              # Date utilities (MODIFY: add time range construction)

tests/
├── unit/
│   ├── db/
│   │   └── test_query.py           # Query executor tests (UPDATE: add new tests)
│   └── validation/
│       └── test_matcher.py         # Matcher tests (UPDATE: add position-based tests)
└── integration/
    └── test_record_matching_flow.py # Integration tests for new matching flow (NEW)
```

**Structure Decision**: Single project structure (Option 1). The feature modifies existing modules in `src/db/` and `src/validation/` without requiring new project structure. All changes are contained within the existing ETL validation tools codebase.

## Complexity Tracking

> No constitution violations - complexity tracking not required

## Phase 0: Research ✅ Complete

**Status**: ✅ Complete - All technical decisions resolved

**Research Tasks Completed**:
1. ✅ SQL-level sorting implementation in DolphinDB
2. ✅ Time-based filtering for BOND_FUT data
3. ✅ Position-based matching logic design
4. ✅ Backward compatibility strategy
5. ✅ Performance optimization approach

**Output**: [research.md](./research.md)

---

## Phase 1: Design & Contracts ✅ Complete

**Status**: ✅ Complete - All design artifacts generated

**Deliverables**:
1. ✅ **Data Model**: [data-model.md](./data-model.md) - Data structures, flow, and constraints
2. ✅ **API Contracts**: [contracts/api.md](./contracts/api.md) - Function interfaces and signatures
3. ✅ **Quick Start**: [quickstart.md](./quickstart.md) - Usage guide and testing
4. ✅ **Agent Context**: Updated CODEBUDDY.md with Python 3.8+ and DolphinDB dependencies

**Design Decisions**:
- Position-based matching replaces composite key matching
- SQL-level sorting ensures consistency across instances
- BOND_FUT time filter applied at database level
- Backward compatibility maintained via deprecated functions

---

## Constitution Check (Post-Design)

| Principle | Status | Notes |
|-----------|--------|-------|
| CLI-First Architecture | ✅ Pass | No changes to CLI interface (only added optional parameter) |
| Python 3.8+ with Conda | ✅ Pass | All new code uses Python 3.8+ compatible syntax |
| Standalone Application | ✅ Pass | No new external dependencies added |
| Simplicity & Maintainability | ✅ Pass | Simplified matching logic, removed complexity |
| Testability | ✅ Pass | All functions independently testable |

**All gates passed - ready for implementation planning**

---

## Next Steps

**Phase 2: Task Breakdown** (NOT created by `/speckit.plan`)

Run `/speckit.tasks` command to generate detailed task breakdown for implementation.

**Command**: `/speckit.tasks`

This will create:
- `specs/006-record-matching/tasks.md` - Detailed task breakdown with implementation steps

---

**Ready for implementation planning!**
