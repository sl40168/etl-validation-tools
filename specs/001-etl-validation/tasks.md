---

description: "Task list for ETL data validation tool implementation"
---

# Tasks: DolphinDB ETL Data Validation Tool

**Input**: Design documents from `/specs/001-etl-validation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-interface.md, quickstart.md

**Tests**: Tests are included as part of the testability requirement (Constitution Principle V). Unit tests and integration tests will be implemented.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Single project structure: `src/`, `tests/`, `config/`, `reports/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure as per implementation plan (src/, tests/, config/, reports/, docs/)
- [ ] T002 Create __init__.py files in src/, src/cli/, src/config/, src/db/, src/validation/, src/reporting/, src/utils/, tests/, tests/unit/, tests/integration/
- [ ] T003 Create requirements.txt with dependencies: dolphindb>=1.30.0, pandas>=1.3.0, retrying>=1.3.3, pytest>=7.0.0, pytest-mock>=3.6.0
- [ ] T004 [P] Create setup.py with package metadata and entry point for etl_validator CLI
- [ ] T005 [P] Create .gitignore to exclude __pycache__/, *.pyc, .pytest_cache/, reports/, config/db_connections.ini, *.log
- [ ] T006 [P] Create config/db_connections_example.ini with example DolphinDB connection configuration
- [ ] T007 Create README.md with project overview, installation instructions, and usage examples

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 [P] Implement config loader in src/config/loader.py to parse INI configuration file and validate required fields (host, port, username, password, database) for [instance_left] and [instance_right] sections
- [ ] T009 [P] Implement retry utility in src/utils/retry.py with @retry decorator, 3 max attempts, exponential backoff (1s, 2s, 4s), retry on dolphindb.session.OperationalError and dolphindb.session.InterfaceError
- [ ] T010 [P] Implement DolphinDB connection wrapper in src/db/connection.py with Session connection, connection test method, and retry integration
- [ ] T011 [P] Implement date parsing utility in src/utils/date_helpers.py to convert YYYYMMDD string to datetime object and format as YYYY.MM.DD for SQL queries
- [ ] T012 [P] Implement validation group definitions in src/validation/groups.py as constant list VALIDATION_GROUPS with tuples (step, product_type, tick_type, description) for the 3 predefined groups
- [ ] T013 Implement query executor in src/db/query.py with methods to execute SQL query for market price table with product_type and tick_type filters, using chunked retrieval (100k records per chunk) for memory management
- [ ] T014 Create CLI argument parser in src/cli/main.py with argparse for --config (required), --date (required, YYYYMMDD format), --step (optional, 1|2|3, single value only), --help, --version arguments
- [ ] T015 [P] Create test fixtures in tests/fixtures/config_example.ini with valid DolphinDB connection configuration for unit testing
- [ ] T016 [P] Create test fixtures in tests/fixtures/sample_data.csv with sample market price records for integration testing

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Validate Market Price Data Between Two DolphinDB Instances (Priority: P1) 🎯 MVP

**Goal**: Retrieve data from two DolphinDB instances, match records, and compare 84 columns for matched pairs

**Independent Test**: Run validation tool against two DolphinDB test instances with known identical and differing data, verify generated report correctly identifies matched/unmatched records with specific column differences

### Tests for User Story 1

- [ ] T017 [P] [US1] Create unit test for config loader validation in tests/unit/test_config_loader.py (test valid config, test missing section, test missing field, test invalid port)
- [ ] T018 [P] [US1] Create unit test for date parsing in tests/unit/test_date_helpers.py (test valid date, test invalid format, test invalid date)
- [ ] T019 [P] [US1] Create unit test for retry utility in tests/unit/test_retry.py (test success on first attempt, test retry 3 times then fail, test exponential backoff)
- [ ] T020 [P] [US1] Create unit test for connection wrapper in tests/unit/test_connection.py (test successful connection, test connection retry, test connection failure after retries)
- [ ] T021 [P] [US1] Create unit test for query executor in tests/unit/test_query.py using pytest-mock to mock DolphinDB session (test query execution, test chunked retrieval, test empty result)
- [ ] T022 [P] [US1] Create comprehensive unit tests for matcher logic in tests/unit/test_matcher.py (test record matching with various scenarios, test chunked processing aggregation, test duplicate matching handling)
- [ ] T023 [P] [US1] Create comprehensive unit tests for column comparison in tests/unit/test_comparator.py (test precision-aware comparison for volumes, prices, yields, test NULL value handling, test exact matches)
- [ ] T024 [P] [US1] Create integration test for validation workflow in tests/integration/test_validation_workflow.py with mocked DolphinDB connections (test end-to-end validation for single group)

### Implementation for User Story 1

- [ ] T025 [P] [US1] Implement record matcher in src/validation/matcher.py with match_records(left_df, right_df) function using pandas merge on composite key (receive_time, exch_product_id, settle_speed), supporting chunked processing (100k records per chunk), returning matched pairs and unmatched records (left_only, right_only)
- [ ] T026 [US1] Implement precision-aware column comparator in src/validation/comparator.py with compare_columns(left_record, right_record) function, defining VOLUME_FIELDS (round to 0 decimals), PRICE_FIELDS (round to 5 decimals), YIELD_FIELDS (round to 5 decimals), applying pandas round() before comparison, comparing 84 columns (excluding create_time, store_time, matching keys when used), returning list of column names with differences
- [ ] T027 [US1] Implement main validation orchestration in src/cli/main.py in validate_step() function that loads config, tests connections, retrieves data for specified validation group using query executor with product_type and tick_type filters, calls matcher for each chunk, aggregates results across chunks, calls comparator for matched pairs, and collects statistics (retrieved counts, matched count, unmatched count, column differences, left unmatched, right unmatched)
- [ ] T028 [US1] Integrate retry logic into query executor and connection wrapper in src/db/query.py and src/db/connection.py for connection failures and query errors
- [ ] T029 [US1] Add progress logging in src/cli/main.py for validation steps (retrieved counts, matched counts, unmatched counts, retry notifications)
- [ ] T030 [US1] Add error handling and exit codes in src/cli/main.py (1 for config error, 2 for argument error, 3 for connection error, 4 for query error, 5 for validation error)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Generate Comprehensive Validation Reports (Priority: P1)

**Goal**: Generate detailed Markdown reports for each validation group with statistics on retrieved records, matched records, unmatched records by column, and unmatched records by side

**Independent Test**: Run validation and verify generated Markdown file contains all required sections with accurate counts and is properly formatted for display

### Tests for User Story 2

- [ ] T031 [P] [US2] Create unit test for report generator in tests/unit/test_generator.py (test report structure, test statistics accuracy, test Markdown formatting)

### Implementation for User Story 2

- [ ] T032 [P] [US2] Implement report generator in src/reporting/generator.py with generate_report(validation_stats, group_info, validation_date) function using f-string templating, creating reports/ directory if needed, generating filename as validation_{product_type}_{tick_type}_{YYYYMMDD}.md, including all required sections (header, summary table, match results, unmatched by column, unmatched by side)
- [ ] T033 [P] [US2] Implement statistics formatter in src/reporting/formatter.py with format_number(value) helper for integer formatting (e.g., 45,234), format_column_differences(column_differences) to convert dictionary to Markdown table, format_side_counts(left_unmatched, right_unmatched) for side-specific statistics
- [ ] T034 [US2] Integrate report generation into validation orchestration in src/cli/main.py, calling generate_report() after each validation step with aggregated statistics, outputting report file path to stdout
- [ ] T035 [US2] Add validation statistics aggregation in src/cli/main.py to track left_retrieved_count, right_retrieved_count, matched_count, column_differences dictionary, left_unmatched_count, right_unmatched_count across all chunks for a validation step

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Execute Validation for Specific Product Type Groups (Priority: P2)

**Goal**: Run validation for three specific product type groups (BOND/TRADE, BOND/QUOTE, BOND_FUT/SNAPSHOT) either all together or individually

**Independent Test**: Run tool with and without step parameter and verify only specified validation groups are executed

### Tests for User Story 3

- [ ] T036 [P] [US3] Create unit test for validation group filtering in tests/unit/test_groups.py (test group definitions, test group filtering by step parameter)

### Implementation for User Story 3

- [ ] T037 [US3] Implement step parameter validation in src/cli/main.py to validate --step parameter accepts only 1, 2, or 3, rejects multiple --step values, defaults to None (all steps) when not provided
- [ ] T038 [US3] Implement validation group iteration in src/cli/main.py main() function to loop through VALIDATION_GROUPS (from groups.py), skip groups if --step parameter is specified and doesn't match current group number, call validate_step() for each selected group
- [ ] T039 [US3] Update progress logging in src/cli/main.py to display step number (e.g., [Step 1/3], [Step 2/3], [Step 3/3]) for full validation or [Step X/3] for single step
- [ ] T040 [US3] Add query filtering in src/db/query.py to apply product_type and tick_type filters to SQL query based on validation group (WHERE product_type = '{product_type}' AND tick_type = '{tick_type}')

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Configure Multiple DolphinDB Connections (Priority: P2)

**Goal**: Provide connection information for two DolphinDB instances through INI configuration file passed as command-line parameter

**Independent Test**: Create INI files with different connection parameters and verify tool correctly reads and uses specified connections

### Tests for User Story 4

- [ ] T041 [P] [US4] Create unit test for INI file validation in tests/unit/test_config_loader.py (test valid INI format, test missing instance section, test invalid INI syntax, test empty file)
- [ ] T042 [P] [US4] Create unit test for connection test in tests/unit/test_connection.py (test successful connection test, test connection test failure)

### Implementation for User Story 4

- [ ] T043 [P] [US4] Enhance config loader in src/config/loader.py to add validate_config(config_dict) function that checks for [instance_left] and [instance_right] sections, validates all required fields present, validates port is integer in range 1-65535, returns structured configuration object
- [ ] T044 [P] [US4] Enhance connection wrapper in src/db/connection.py to add test_connection(config) function that attempts to connect to DolphinDB using provided configuration, returns True on success, raises exception on failure with detailed error message
- [ ] T045 [US4] Add configuration error handling in src/cli/main.py to catch file not found, invalid INI format, missing sections/fields, connection test failure, display clear error messages to stderr, exit with code 1
- [ ] T046 [US4] Add configuration loading confirmation in src/cli/main.py to output "Configuration loaded from: {path}" to stdout on successful load
- [ ] T047 [US4] Add connection test confirmation in src/cli/main.py to output "Connection tests passed" to stdout after successfully testing both instances

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T048 [P] Create integration test for full validation workflow in tests/integration/test_validation_workflow.py (test all 3 groups execution, test single step execution, test report generation)
- [ ] T049 [P] Create integration test for report generation in tests/integration/test_report_generation.py (test report file creation, test report content accuracy, test Markdown formatting)
- [ ] T050 Code cleanup and refactoring across src/ modules to ensure consistency with Constitution Principle IV (simplicity and maintainability)
- [ ] T051 Performance optimization for large datasets (2M records) in src/validation/matcher.py and src/validation/comparator.py to verify chunked processing keeps memory under 2GB and completes in acceptable time
- [ ] T052 Add logging configuration in src/cli/main.py to set up appropriate log levels for development vs production
- [ ] T053 Security hardening to ensure credentials are not logged and error messages don't expose sensitive information
- [ ] T054 Update README.md with comprehensive documentation including installation, configuration, usage, troubleshooting, and examples
- [ ] T055 Run quickstart.md validation to verify all documented steps work correctly
- [ ] T056 Add __main__.py in src/ to enable `python -m etl_validator` execution as specified in CLI contract

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) and User Story 1 - Integrates with US1's validation results but generates independently testable reports
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Builds on US1's validation logic but adds step parameter filtering
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Enhances config loader and connection wrapper from Phase 2

### Within Each User Story

- Unit tests MUST be written before or alongside implementation
- Core logic (matcher, comparator, generator) before orchestration (main.py)
- Error handling and logging after core functionality
- Integration tests after implementation is complete

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All unit tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all unit tests for User Story 1 together:
Task: "Create unit test for config loader validation in tests/unit/test_config_loader.py"
Task: "Create unit test for date parsing in tests/unit/test_date_helpers.py"
Task: "Create unit test for retry utility in tests/unit/test_retry.py"
Task: "Create unit test for connection wrapper in tests/unit/test_connection.py"
Task: "Create unit test for query executor in tests/unit/test_query.py"
Task: "Create integration test for validation workflow in tests/integration/test_validation_workflow.py"

# Launch core implementation for User Story 1 together:
Task: "Implement record matcher in src/validation/matcher.py"
Task: "Implement precision-aware column comparator in src/validation/comparator.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 and 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (validate market price data)
4. Complete Phase 4: User Story 2 (generate reports)
5. **STOP and VALIDATE**: Test User Stories 1 and 2 together independently
6. Deploy/demo MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Validate core validation logic
3. Add User Story 2 → Test independently → Generate readable reports (MVP!)
4. Add User Story 3 → Test independently → Enable selective group validation
5. Add User Story 4 → Test independently → Enhance configuration management
6. Complete Polish → Final production-ready system

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (matching and comparison)
   - Developer B: User Story 2 (report generation)
3. After US1 and US2 complete:
   - Developer A: User Story 3 (step parameter)
   - Developer B: User Story 4 (configuration enhancements)
4. Team completes Polish together
5. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Unit tests provide coverage per Constitution Principle V (testability)
- Chunked processing (100k records per chunk) is MANDATORY for handling 2M records
- Precision-aware comparison (volumes: 0 decimals, prices: 5 decimals, yields: 5 decimals) is MANDATORY for accurate comparison
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Summary

**Total Tasks**: 56
**Tasks per User Story**:
- User Story 1: 12 tasks (6 tests + 6 implementation)
- User Story 2: 5 tasks (1 test + 4 implementation)
- User Story 3: 5 tasks (1 test + 4 implementation)
- User Story 4: 7 tasks (2 tests + 5 implementation)

**Parallel Opportunities**: 28 tasks marked [P] can run in parallel
**MVP Scope**: Phases 1-4 (Setup + Foundational + User Stories 1 and 2) = 32 tasks
**Independent Test Criteria**: Each user story has explicit independent test criteria defined

**Suggested MVP**: User Stories 1 and 2 (core validation logic + report generation) provide a fully functional tool that validates market price data and generates detailed reports. User Stories 3 and 4 add convenience features (selective validation) and robustness (configuration management) that enhance usability but are not required for core functionality.
