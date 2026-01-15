# Tasks: Group-Based Column Validation

**Input**: Design documents from `/specs/001-group-based-validation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are INCLUDED based on feature specification requirements (Unit tests for individual validators, Integration tests for end-to-end ETL workflows)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- This is a CLI application with modular structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create module structure in src/validation/, src/cli/, src/config/, src/db/, src/reporting/, src/utils/ with __init__.py files
- [X] T002 [P] Create test directory structure tests/unit/ and tests/integration/ with __init__.py files
- [X] T003 [P] Create reports/ directory for generated validation reports
- [X] T004 [P] Update requirements.txt with dependencies: dolphindb>=1.30.0, pandas>=1.3.0, retrying>=1.3.3, pytest>=7.0.0, pytest-mock>=3.6.0, pyyaml>=5.4.1
- [X] T005 [P] Create config/db_connections_example.ini template with connection parameters for instance_left and instance_right

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create config/groups.yaml template with 3 group definitions (BOND/TRADE with 18 columns, BOND/QUOTE with 60 columns, BOND_FUT/SNAPSHOT with 39 columns)
- [X] T007 [P] Implement load_groups_from_config() function in src/validation/groups.py to parse YAML config file and return ValidationGroups instance
- [X] T008 [P] Implement validation group definitions in src/validation/groups.py with load_groups_from_config() to populate VALIDATION_GROUPS dict from YAML
- [X] T009 Implement ValidationGroup NamedTuple in src/validation/groups.py with group_id, product_type, message_type, description, required_columns fields
- [X] T010 [P] Implement get_validation_groups() function in src/validation/groups.py to filter groups by step parameter
- [X] T011 [P] Implement get_group_by_step() function in src/validation/groups.py to retrieve specific group by step number
- [X] T012 [P] Create ColumnValidator class in src/validation/column_validator.py with __init__(required_columns, type_rules) method
- [X] T013 Implement validate_columns() method in src/validation/column_validator.py to check DataFrame against required columns and return missing/extra columns
- [X] T014 [P] Implement validate_types() method in src/validation/column_validator.py to validate data types with type_rules parameter
- [X] T015 Implement ColumnValidationResult NamedTuple in src/validation/column_validator.py with status, missing_columns, extra_columns, type_mismatches, validated_at fields
- [X] T016 Implement NULL-aware comparison function in src/validation/comparator.py to compare DataFrames with both sides NULL = pass logic
- [X] T017 [P] Implement record matching function in src/validation/matcher.py using pandas merge on composite key (receive_time, exch_product_id, settle_speed)
- [X] T018 [P] Create ConnectionWrapper class in src/db/connection.py to wrap DolphinDB session with connection management
- [X] T019 [P] Implement verify_connection() function in src/db/connection.py to test connection and raise exceptions on failure
- [X] T020 [P] Implement retrieve_data() generator in src/db/query.py with CHUNK_SIZE=100000 for chunked data retrieval
- [X] T021 [P] Implement load_config() function in src/config/loader.py to parse INI configuration file
- [X] T022 [P] Implement validate_config() function in src/config/loader.py to validate required fields (host, port, username, password, database)
- [X] T023 Implement DolphinDBConfig NamedTuple in src/config/loader.py with host, port, username, password, database fields
- [X] T024 [P] Implement parse_date() function in src/utils/date_helpers.py to parse YYYYMMDD format
- [X] T025 [P] Implement parse_and_format_date() function in src/utils/date_helpers.py to convert YYYYMMDD to YYYY.MM.DD for SQL
- [X] T026 [P] Implement retry decorator with exponential backoff in src/utils/retry.py using retrying library
- [X] T027 [P] Create CLI argument parser in src/cli/main.py with --config, --date, --step parameters and help text
- [X] T028 [P] Implement validate_arguments() function in src/cli/main.py to validate date format and step parameter
- [X] T029 [P] Implement report formatter in src/reporting/formatter.py with Markdown formatting functions
- [X] T030 Implement generate_report() function in src/reporting/generator.py to write Markdown report with column validation and comparison results

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - BOND TRADE Group Validation (Priority: P1) 🎯 MVP

**Goal**: Validate bond trade data against 18 required columns with column presence, type validation, and NULL-aware comparison

**Independent Test**: Run validation with --step 1 on sample BOND TRADE dataset and verify all 18 required columns (business_date, exch_product_id, product_type, exchange, source, settle_speed, last_trade_price, last_trade_yield, last_trade_yield_type, last_trade_volume, last_trade_turnover, last_trade_interest, last_trade_side, level, status) are validated correctly, missing columns are reported, and NULL-aware comparison passes when both sides have NULL values

### Tests for User Story 1

- [X] T031 [P] [US1] Unit test for get_group_by_step(1) in tests/unit/test_groups.py verifying it returns BOND TRADE group
- [ ] T032 [P] [US1] Unit test for validate_columns() in tests/unit/test_column_validator.py with BOND TRADE columns list verifying missing column detection
- [ ] T033 [P] [US1] Unit test for validate_columns() in tests/unit/test_column_validator.py with BOND TRADE columns list verifying extra column detection
- [ ] T034 [P] [US1] Unit test for validate_columns() in tests/unit/test_column_validator.py with BOND TRADE columns list verifying type mismatch detection
- [X] T035 [P] [US1] Unit test for compare_with_null_awareness() in tests/unit/test_comparator.py verifying both sides NULL = pass
- [X] T036 [P] [US1] Unit test for compare_with_null_awareness() in tests/unit/test_comparator.py verifying one side NULL = difference
- [ ] T037 [P] [US1] Integration test for full BOND TRADE validation flow in tests/integration/test_validation_flow.py with mock DolphinDB data

### Implementation for User Story 1

- [ ] T038 [US1] Implement validate_step() function in src/cli/main.py to execute BOND TRADE validation with group_id=1, product_type="BOND", message_type="TRADE"
- [ ] T039 [US1] Add BOND TRADE column validation logic in validate_step() using ColumnValidator with 18 required columns
- [ ] T040 [US1] Integrate NULL-aware column comparison in validate_step() for BOND TRADE group using comparator.compare_with_null_awareness()
- [ ] T041 [US1] Generate BOND TRADE-specific Markdown report in validate_step() with validation status, missing columns, and comparison results
- [ ] T042 [US1] Add error handling for BOND TRADE validation in validate_step() with specific error messages for missing columns and connection failures
- [ ] T043 [US1] Add logging for BOND TRADE validation operations in validate_step() with progress messages for each chunk processed

**Checkpoint**: At this point, User Story 1 (BOND TRADE) should be fully functional and testable independently with command: python -m etl_validator --config config/db_connections.ini --date 20260115 --step 1

---

## Phase 4: User Story 2 - BOND QUOTE Group Validation (Priority: P1)

**Goal**: Validate bond quote data against 60 required columns (6 price levels × 10 fields) with validation for bid/offer structures

**Independent Test**: Run validation with --step 2 on sample BOND QUOTE dataset and verify all 60 required columns across 6 price levels (bid_0_price through bid_5_price, offer_0_price through offer_5_price, with corresponding yield, yield_type, tradable_volume, volume fields) are validated correctly

### Tests for User Story 2

- [ ] T044 [P] [US2] Unit test for get_group_by_step(2) in tests/unit/test_groups.py verifying it returns BOND QUOTE group
- [ ] T045 [P] [US2] Unit test for validate_columns() in tests/unit/test_column_validator.py with BOND QUOTE columns list (60 columns) verifying all price level columns are validated
- [ ] T046 [P] [US2] Unit test for validate_columns() in tests/unit/test_column_validator.py with BOND QUOTE dataset having partial quote levels verifying available levels are validated
- [ ] T047 [P] [US2] Integration test for full BOND QUOTE validation flow in tests/integration/test_validation_flow.py with mock DolphinDB data containing 6 quote levels

### Implementation for User Story 2

- [ ] T048 [US2] Implement validate_step() support for BOND QUOTE with group_id=2, product_type="BOND", message_type="QUOTE"
- [ ] T049 [US2] Add BOND QUOTE column validation logic using ColumnValidator with 60 required columns (bid_0_X, offer_0_X through bid_5_X, offer_5_X)
- [ ] T050 [US2] Integrate NULL-aware column comparison for BOND QUOTE group handling bid/offer price level data
- [ ] T051 [US2] Generate BOND QUOTE-specific Markdown report with validation status for 60 columns and price level structure
- [ ] T052 [US2] Add error handling for BOND QUOTE validation with specific error messages for inconsistent quote level structures

**Checkpoint**: At this point, User Stories 1 (BOND TRADE) AND 2 (BOND QUOTE) should both work independently

---

## Phase 5: User Story 3 - BOND_FUT SNAPSHOT Group Validation (Priority: P2)

**Goal**: Validate bond futures snapshot data against 39 required columns including trade data, quote data (levels 0-1), and market summary data

**Independent Test**: Run validation with --step 3 on sample BOND_FUT SNAPSHOT dataset and verify all 39 required columns are validated: 18 trade columns (same as BOND TRADE), 12 market summary columns (pre_close_price, pre_settle_price, pre_interest, open_price, high_price, low_price, close_price, settle_price, upper_limit, lower_limit, total_volume, total_turnover, open_interest), and 9 quote columns at levels 0-1

### Tests for User Story 3

- [ ] T053 [P] [US3] Unit test for get_group_by_step(3) in tests/unit/test_groups.py verifying it returns BOND_FUT SNAPSHOT group
- [ ] T054 [P] [US3] Unit test for validate_columns() in tests/unit/test_column_validator.py with BOND_FUT SNAPSHOT columns list verifying market summary columns are validated
- [ ] T055 [P] [US3] Unit test for validate_columns() in tests/unit/test_column_validator.py with BOND_FUT SNAPSHOT dataset missing market summary fields verifying specific columns are reported
- [ ] T056 [P] [US3] Unit test for validate_columns() in tests/unit/test_column_validator.py with BOND_FUT SNAPSHOT dataset with quote data beyond level 1 verifying only levels 0-1 are validated
- [ ] T057 [P] [US3] Integration test for full BOND_FUT SNAPSHOT validation flow in tests/integration/test_validation_flow.py with mock DolphinDB data

### Implementation for User Story 3

- [ ] T058 [US3] Implement validate_step() support for BOND_FUT SNAPSHOT with group_id=3, product_type="BOND_FUT", message_type="SNAPSHOT"
- [ ] T059 [US3] Add BOND_FUT SNAPSHOT column validation logic using ColumnValidator with 39 required columns (trade + market summary + quote levels 0-1)
- [ ] T060 [US3] Integrate NULL-aware column comparison for BOND_FUT SNAPSHOT group handling trade, market summary, and quote data
- [ ] T061 [US3] Generate BOND_FUT SNAPSHOT-specific Markdown report with validation status for all 39 columns and market summary statistics
- [ ] T062 [US3] Add error handling for BOND_FUT SNAPSHOT validation with specific error messages for missing market summary columns

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T063 [P] Update README.md with group-based validation examples and --step parameter documentation
- [ ] T064 [P] Add docstrings to all public functions in src/validation/, src/cli/, src/config/, src/db/, src/reporting/, src/utils/
- [ ] T065 [P] Add unit tests for date_helpers.py in tests/unit/test_date_helpers.py covering parse_date() and parse_and_format_date()
- [ ] T066 [P] Add unit tests for retry.py in tests/unit/test_retry.py covering retry decorator functionality
- [ ] T067 [P] Add unit tests for config/loader.py in tests/unit/test_config.py covering load_config() and validate_config()
- [ ] T068 [P] Add unit tests for db/connection.py in tests/unit/test_connection.py covering ConnectionWrapper and verify_connection()
- [ ] T069 [P] Add unit tests for db/query.py in tests/unit/test_query.py covering retrieve_data() chunked retrieval
- [ ] T070 [P] Add unit tests for cli/main.py in tests/unit/test_cli.py covering argument parsing and validation
- [ ] T071 Code cleanup: Remove any unused imports and temporary debugging code
- [ ] T072 Performance optimization: Verify chunked processing stays under 2GB memory limit with 2M records
- [ ] T073 Performance benchmark: Benchmark validation performance with 2M record dataset per group to confirm 3-5 minute completion time (validates SC-002)
- [ ] T074 [P] Run integration test for CLI end-to-end validation in tests/integration/test_cli.py covering all 3 groups
- [ ] T075 Validate quickstart.md examples work correctly with all three validation groups

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (BOND TRADE) - P1**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (BOND QUOTE) - P1**: Can start after Foundational (Phase 2) - Reuses same infrastructure as US1 but different column definitions
- **User Story 3 (BOND_FUT SNAPSHOT) - P2**: Can start after Foundational (Phase 2) - Reuses same infrastructure but includes additional market summary columns

### Within Each User Story

- Tests MUST be written before implementation (TDD approach)
- Tests for foundational components (groups, column_validator, comparator) precede implementation
- Core validation logic before CLI integration
- Error handling and logging after core implementation
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] (T002, T003, T004, T005) can run in parallel
- All Foundational tasks marked [P] (T008, T009, T010, T012, T015, T016, T017, T018, T019, T020, T022, T023, T024, T025, T026, T027) can run in parallel within Phase 2
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel (e.g., T029-T034 for US1)
- Test tasks marked [P] across different test files can run in parallel (e.g., T029-T035 for US1, T042-T045 for US2, T051-T055 for US3)
- Polish phase unit tests marked [P] (T063-T068) can run in parallel
- Documentation tasks in Polish phase marked [P] (T061, T062) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for get_group_by_step(1) in tests/unit/test_groups.py"
Task: "Unit test for validate_columns() in tests/unit/test_column_validator.py with BOND TRADE columns list verifying missing column detection"
Task: "Unit test for validate_columns() in tests/unit/test_column_validator.py with BOND TRADE columns list verifying extra column detection"
Task: "Unit test for validate_columns() in tests/unit/test_column_validator.py with BOND TRADE columns list verifying type mismatch detection"
Task: "Unit test for compare_with_null_awareness() in tests/unit/test_comparator.py verifying both sides NULL = pass"
Task: "Unit test for compare_with_null_awareness() in tests/unit/test_comparator.py verifying one side NULL = difference"
Task: "Integration test for full BOND TRADE validation flow in tests/integration/test_validation_flow.py with mock DolphinDB data"
```

```bash
# Launch all unit tests for Foundational phase together:
Task: "Implement get_validation_groups() function in src/validation/groups.py to filter groups by step parameter"
Task: "Implement get_group_by_step() function in src/validation/groups.py to retrieve specific group by step number"
Task: "Create ColumnValidator class in src/validation/column_validator.py with __init__(required_columns) method"
Task: "Implement validate_types() method in src/validation/column_validator.py to validate data types with type_rules parameter"
Task: "Implement record matching function in src/validation/matcher.py using pandas merge on composite key"
Task: "Create ConnectionWrapper class in src/db/connection.py to wrap DolphinDB session with connection management"
Task: "Implement verify_connection() function in src/db/connection.py to test connection and raise exceptions on failure"
Task: "Implement retrieve_data() generator in src/db/query.py with CHUNK_SIZE=100000 for chunked data retrieval"
Task: "Implement load_config() function in src/config/loader.py to parse INI configuration file"
Task: "Implement validate_config() function in src/config/loader.py to validate required fields"
Task: "Implement parse_date() function in src/utils/date_helpers.py to parse YYYYMMDD format"
Task: "Implement parse_and_format_date() function in src/utils/date_helpers.py to convert YYYYMMDD to YYYY.MM.DD for SQL"
Task: "Implement retry decorator with exponential backoff in src/utils/retry.py using retrying library"
Task: "Create CLI argument parser in src/cli/main.py with --config, --date, --step parameters and help text"
Task: "Implement validate_arguments() function in src/cli/main.py to validate date format and step parameter"
Task: "Implement report formatter in src/reporting/formatter.py with Markdown formatting functions"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T028) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T029-T041)
4. **STOP and VALIDATE**: Test User Story 1 independently with `python -m etl_validator --config config/db_connections.ini --date 20260115 --step 1`
5. Deploy/demo if ready - BOND TRADE validation is now fully functional

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T028)
2. Add User Story 1 → Test independently → Deploy/Demo (T029-T041, MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (T042-T050)
4. Add User Story 3 → Test independently → Deploy/Demo (T051-T060)
5. Complete Polish → Final release (T061-T072)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T028)
2. Once Foundational is done:
   - Developer A: User Story 1 (BOND TRADE) - T029-T041
   - Developer B: User Story 2 (BOND QUOTE) - T042-T050
   - Developer C: User Story 3 (BOND_FUT SNAPSHOT) - T051-T060
3. Stories complete and integrate independently
4. Team completes Polish phase together (T061-T072)

---

## Summary

### Task Statistics

- **Total Tasks**: 72
- **Setup Phase**: 5 tasks (T001-T005)
- **Foundational Phase**: 23 tasks (T006-T028)
- **User Story 1 (BOND TRADE) - P1**: 13 tasks (T029-T041)
  - Tests: 7 tasks
  - Implementation: 6 tasks
- **User Story 2 (BOND QUOTE) - P1**: 9 tasks (T042-T050)
  - Tests: 4 tasks
  - Implementation: 5 tasks
- **User Story 3 (BOND_FUT SNAPSHOT) - P2**: 10 tasks (T051-T060)
  - Tests: 5 tasks
  - Implementation: 5 tasks
- **Polish Phase**: 12 tasks (T061-T072)

### Parallel Opportunities

- **High Parallelism in Foundational Phase**: 17 tasks marked [P] (T008-T009, T010, T012, T015-T027)
- **High Parallelism in User Story Tests**: All test tasks per story are parallelizable (T029-T035 for US1, T042-T045 for US2, T051-T055 for US3)
- **High Parallelism in Polish Phase**: 6 tasks marked [P] (T061-T068)
- **User Stories Can Run in Parallel**: After Foundational phase, US1, US2, US3 can be developed simultaneously

### Independent Test Criteria

- **User Story 1**: Run `python -m etl_validator --config config/db_connections.ini --date 20260115 --step 1` and verify BOND TRADE report generated with 18 columns validated
- **User Story 2**: Run `python -m etl_validator --config config/db_connections.ini --date 20260115 --step 2` and verify BOND QUOTE report generated with 60 columns validated
- **User Story 3**: Run `python -m etl_validator --config config/db_connections.ini --date 20260115 --step 3` and verify BOND_FUT SNAPSHOT report generated with 39 columns validated

### Suggested MVP Scope

**MVP = Phase 1 + Phase 2 + Phase 3 (User Story 1 only)**

- Delivers BOND TRADE validation (most frequently used, highest priority)
- 31 tasks total (T001-T041)
- Estimated effort: Foundational + one user story
- Provides immediate value: Validate 18-column bond trade data with column presence, type validation, and NULL-aware comparison
- Can be deployed and demoed independently
- User Stories 2 and 3 can be added incrementally without breaking MVP

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are included based on feature specification requirements (Unit tests for individual validators, Integration tests for end-to-end ETL workflows)
