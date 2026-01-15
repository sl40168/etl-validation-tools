---

description: "Task list for feature implementation"
---

# Tasks: Record Matching Logic Enhancement

**Input**: Design documents from `/specs/006-record-matching/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included in task breakdown as specified in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Verify Python 3.8+ environment and dependencies are installed in requirements.txt
- [X] T002 Review existing codebase structure in src/ and tests/ directories
- [X] T003 [P] Review current implementation in src/db/query.py and src/validation/matcher.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add construct_time_range() function in src/utils/date_helpers.py for building datetime strings
- [X] T005 Add deprecation warnings to existing match_records() function in src/validation/matcher.py
- [X] T006 Add deprecation warnings to existing match_records_chunked() function in src/validation/matcher.py
- [X] T007 Update CLI argument parser in src/cli/main.py to add --matching-strategy parameter with choices=['position', 'composite'] and default='position'

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Validate Data Consistency with Sorted Records (Priority: P1) 🎯 MVP

**Goal**: Implement SQL-level sorting with ORDER BY clause in both DolphinDB instances

**Independent Test**: Run validation task with sample data and verify query contains ORDER BY clause, records are sorted by receive_time, and matching uses position-based approach

### Tests for User Story 1

- [X] T008 [P] [US1] Write unit test test_query_with_order_by() in tests/unit/db/test_query.py to verify ORDER BY clause is added to queries
- [X] T009 [P] [US1] Write unit test test_order_by_in_both_instances() in tests/unit/db/test_query.py to verify both left and right queries have same ORDER BY
- [X] T010 [P] [US1] Write integration test test_sorted_records_matching() in tests/integration/test_record_matching_flow.py to verify end-to-end flow with sorted records

### Implementation for User Story 1

- [X] T011 [US1] Modify execute_query() function in src/db/query.py to add ORDER BY receive_time, exch_product_id, settle_speed clause to SQL query construction
- [X] T012 [US1] Modify execute_query_with_chunks() function in src/db/query.py to add ORDER BY receive_time, exch_product_id, settle_speed clause to SQL query construction
- [X] T013 [US1] Update docstrings in src/db/query.py for execute_query() and execute_query_with_chunks() to document ORDER BY behavior
- [X] T014 [US1] Run unit tests in tests/unit/db/test_query.py to verify ORDER BY clause implementation
- [X] T015 [US1] Run integration tests to verify sorted records are retrieved correctly from both DolphinDB instances

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Filter Bond Futures Data by Trading Hours (Priority: P1)

**Goal**: Implement time-based filtering for BOND_FUT data type (09:30:00-15:00:00)

**Independent Test**: Run validation task on BOND_FUT data and verify only records within 09:30:00-15:00:00 are included, while other data types have no time filter

### Tests for User Story 2

- [X] T016 [P] [US2] Write unit test test_time_filter_for_bond_fut() in tests/unit/db/test_query.py to verify time filter is added for BOND_FUT
- [X] T017 [P] [US2] Write unit test test_no_time_filter_for_other_types() in tests/unit/db/test_query.py to verify time filter is NOT applied to non-BOND_FUT types
- [X] T018 [P] [US2] Write integration test test_bond_fut_time_filtering() in tests/integration/test_record_matching_flow.py to verify BOND_FUT records outside trading hours are excluded

### Implementation for User Story 2

- [X] T019 [US2] Modify execute_query() function in src/db/query.py to add conditional time filter when product_type == "BOND_FUT" using construct_time_range()
- [X] T020 [US2] Modify execute_query_with_chunks() function in src/db/query.py to add conditional time filter when product_type == "BOND_FUT" using construct_time_range()
- [X] T021 [US2] Update docstrings in src/db/query.py to document BOND_FUT time filtering behavior
- [X] T022 [US2] Update construct_time_range() docstring in src/utils/date_helpers.py to document format and return values
- [X] T023 [US2] Run unit tests in tests/unit/db/test_query.py to verify time filter implementation
- [X] T024 [US2] Run integration tests to verify BOND_FUT records are correctly filtered by time range

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Simplify Record Matching to Position-Based Comparison (Priority: P1)

**Goal**: Implement position-based matching logic replacing composite key matching

**Independent Test**: Run validation task and verify records are matched by sequential position (Nth in left with Nth in right), excess records flagged as unpaired, and matching completes in <10 seconds for 10k records

### Tests for User Story 3

- [X] T025 [P] [US3] Write unit test test_position_based_matching_equal_size() in tests/unit/validation/test_matcher.py to verify matching when both DataFrames have same size
- [X] T026 [P] [US3] Write unit test test_position_based_matching_unequal_size() in tests/unit/validation/test_matcher.py to verify unpaired records when DataFrames have different sizes
- [X] T027 [P] [US3] Write unit test test_position_based_matching_empty_dataframes() in tests/unit/validation/test_matcher.py to verify handling of empty DataFrames
- [X] T028 [P] [US3] Write unit test test_position_based_matching_performance() in tests/unit/validation/test_matcher.py to verify <10 second performance for 10,000 records
- [X] T029 [P] [US3] Write integration test test_full_position_matching_flow() in tests/integration/test_record_matching_flow.py to verify end-to-end position-based matching

### Implementation for User Story 3

- [X] T030 [US3] Implement match_records_by_position() function in src/validation/matcher.py to match records by sequential position
- [X] T031 [US3] Implement match_records_by_position_chunked() function in src/validation/matcher.py for chunked processing of large datasets
- [X] T032 [US3] Add error handling in match_records_by_position() to check DataFrame schema compatibility
- [X] T033 [US3] Add comprehensive docstrings to match_records_by_position() and match_records_by_position_chunked() documenting parameters, returns, and behavior
- [X] T034 [US3] Run unit tests in tests/unit/validation/test_matcher.py to verify position-based matching implementation
- [X] T035 [US3] Run integration tests to verify end-to-end position-based matching flow
- [X] T036 [US3] Run performance benchmark tests to verify <10 second target for 10,000 records

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T037 [P] Update README.md to document new --matching-strategy CLI parameter and behavior change
- [X] T038 [P] Update CODEBUDDY.md to document matching strategy change from composite to position-based
- [X] T039 [P] Run all unit tests with pytest to verify no regressions
- [X] T040 [P] Run all integration tests to verify end-to-end functionality
- [X] T041 [P] Update quickstart.md with any lessons learned during implementation
- [X] T042 Run manual smoke tests following quickstart.md verification checklist
- [X] T043 [P] Update inline code comments in src/db/query.py and src/validation/matcher.py for clarity
- [X] T044 Remove deprecated functions if backward compatibility period has passed (document in commit message)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1, but both modify src/db/query.py
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 (uses sorted data) and US2 (uses filtered data)

### Within Each User Story

- Tests MUST be written before implementation (TDD approach)
- Test tasks marked [P] can be written in parallel
- Implementation tasks depend on test tasks being complete
- Tests should FAIL before implementation, PASS after

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T001-T003)
- All Foundational tasks marked [P] can run in parallel (T004-T007)
- Tests within each user story marked [P] can run in parallel
- User Stories 1 and 2 can run in parallel after Foundational (modify different parts of query.py, but tests are separate)
- User Story 3 depends on US1 and US2 completion (uses sorted and filtered data)
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: T008 - Write unit test test_query_with_order_by() in tests/unit/db/test_query.py
Task: T009 - Write unit test test_order_by_in_both_instances() in tests/unit/db/test_query.py
Task: T010 - Write integration test test_sorted_records_matching() in tests/integration/test_record_matching_flow.py

# Then run implementation sequentially (depends on query.py file):
Task: T011 - Modify execute_query() function in src/db/query.py
Task: T012 - Modify execute_query_with_chunks() function in src/db/query.py
Task: T013 - Update docstrings in src/db/query.py
```

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: T016 - Write unit test test_time_filter_for_bond_fut() in tests/unit/db/test_query.py
Task: T017 - Write unit test test_no_time_filter_for_other_types() in tests/unit/db/test_query.py
Task: T018 - Write integration test test_bond_fut_time_filtering() in tests/integration/test_record_matching_flow.py

# Then run implementation (modifies query.py, sequential):
Task: T019 - Modify execute_query() function in src/db/query.py
Task: T020 - Modify execute_query_with_chunks() function in src/db/query.py
Task: T021 - Update docstrings in src/db/query.py
Task: T022 - Update construct_time_range() docstring in src/utils/date_helpers.py
```

---

## Parallel Example: User Story 3

```bash
# Launch all tests for User Story 3 together:
Task: T025 - Write unit test test_position_based_matching_equal_size() in tests/unit/validation/test_matcher.py
Task: T026 - Write unit test test_position_based_matching_unequal_size() in tests/unit/validation/test_matcher.py
Task: T027 - Write unit test test_position_based_matching_empty_dataframes() in tests/unit/validation/test_matcher.py
Task: T028 - Write unit test test_position_based_matching_performance() in tests/unit/validation/test_matcher.py
Task: T029 - Write integration test test_full_position_matching_flow() in tests/integration/test_record_matching_flow.py

# Then run implementation (modifies matcher.py):
Task: T030 - Implement match_records_by_position() function in src/validation/matcher.py
Task: T031 - Implement match_records_by_position_chunked() function in src/validation/matcher.py
Task: T032 - Add error handling in match_records_by_position()
Task: T033 - Add comprehensive docstrings
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T007) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T008-T015)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Verify ORDER BY clause in queries
   - Verify records are sorted correctly
   - Run integration tests
5. Demo validation with sorted records

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
   - SQL-level sorting implemented
   - Records sorted by receive_time, exch_product_id, settle_speed
3. Add User Story 2 → Test independently → Deploy/Demo
   - BOND_FUT time filtering added
   - Only trading hours data validated
4. Add User Story 3 → Test independently → Deploy/Demo
   - Position-based matching implemented
   - Simplified matching logic
5. Polish → Final deployment

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T007)
2. Once Foundational is done:
   - Developer A: User Story 1 (T008-T015) - Sorting logic
   - Developer B: User Story 2 (T016-T024) - Time filter logic (can parallelize with US1 tests, but implementation conflicts on query.py)
   - Developer C: Start on US3 tests (T025-T029) while waiting for US1/US2 completion
3. After US1 and US2 complete:
   - Developer A/B: Complete US3 implementation (T030-T036)
4. Team completes Polish phase together (T037-T044)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are written FIRST and should FAIL before implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tasks modify existing files (src/db/query.py, src/validation/matcher.py) - be aware of merge conflicts in parallel development
- Backward compatibility maintained via deprecated functions
- Performance target: <10 seconds for 10,000 records
- All three user stories are P1 priority - all should be completed for full feature

---

## Summary

- **Total Tasks**: 44
- **Setup Tasks**: 3 (T001-T003)
- **Foundational Tasks**: 4 (T004-T007)
- **User Story 1 Tasks**: 8 (3 tests + 5 implementation)
- **User Story 2 Tasks**: 9 (3 tests + 6 implementation)
- **User Story 3 Tasks**: 12 (5 tests + 7 implementation)
- **Polish Tasks**: 8 (T037-T044)

**Test Coverage**: 11 unit tests + 3 integration tests = 14 total tests

**Parallel Opportunities**: 
- 3 parallel opportunities in Setup
- 4 parallel opportunities in Foundational
- 3 parallel opportunities per user story (tests)
- 8 parallel opportunities in Polish

**Independent Test Criteria**:
- US1: Query contains ORDER BY, records sorted, matching works
- US2: BOND_FUT has time filter, other types don't, correct records included
- US3: Position-based matching works, unpaired records flagged, performance <10s

**Suggested MVP Scope**: User Story 1 only (SQL-level sorting) - provides core value and can be tested independently

**Format Validation**: ✅ All tasks follow checklist format (checkbox, ID, labels, file paths)
