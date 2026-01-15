## Clarifications

### Session 2026-01-15

- Q: What rule should determine the secondary sort order when multiple records have the same receive_time? → A: order by receive_time, exch_product_id, settle_speed (MUST be executed in both DolphinDB instances by SQL)
- Q: What behavior should occur when the BOND_FUT time filter returns zero records? → A: if both are zero, that's ok
- Q: How should the system handle the trading hours filter when the business date spans midnight? → A: existing market does not trade in midnight

# Feature Specification: Record Matching Logic Enhancement

**Feature Branch**: `006-record-matching`  
**Created**: 2026-01-15  
**Status**: Draft  
**Input**: User description: "Let's have modification on the logic to match record between left and right data source. 1. The returned records from both data sources MUST be sorted by receive_time. 2. For BOND_FUT, an additional filter MUST be added while retrieving, that is receive_time > {BUSINESS_DATA} 09:30:00 amd receive_time < {BUSINESS_DATE} 15:00:00. 3. The record from left and right data source are matched no longer by the combination, but just the sequence number in result set, for example, the 1st record in left compare with the 1st record in right."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validate Data Consistency with Sorted Records (Priority: P1)

As a data validation engineer, I need to validate that records from left and right data sources are correctly matched when they are sorted by receive_time, so that I can ensure data consistency across systems without relying on complex key combinations.

**Why this priority**: This is the core functionality that ensures accurate data validation across different data sources. Without proper record matching, validation results would be meaningless.

**Independent Test**: Can be fully tested by running a validation task with sample data sorted by receive_time and verifying that records are matched in sequence order, delivering accurate validation reports.

**Acceptance Scenarios**:

1. **Given** a validation task configured with left and right data sources, **When** records are retrieved from both sources, **Then** all records MUST be sorted by receive_time in ascending order
2. **Given** sorted records from both data sources, **When** the matching process runs, **Then** the Nth record from the left source MUST be compared with the Nth record from the right source
3. **Given** validation completes, **When** the report is generated, **Then** it MUST reflect comparisons between records in their sorted sequence positions

---

### User Story 2 - Filter Bond Futures Data by Trading Hours (Priority: P1)

As a data validation engineer specializing in bond futures, I need to filter BOND_FUT records to only include those received during trading hours (09:30:00 to 15:00:00 on the business date), so that validation focuses on active market data and ignores after-hours records.

**Why this priority**: This filtering is critical for bond futures validation as it ensures only relevant trading data is compared, improving validation accuracy and performance.

**Independent Test**: Can be fully tested by running a validation task on BOND_FUT data and verifying that only records within the specified time window are included in the validation, delivering focused and accurate validation results.

**Acceptance Scenarios**:

1. **Given** a validation task for BOND_FUT data type, **When** records are retrieved, **Then** only records with receive_time between {BUSINESS_DATE} 09:30:00 and {BUSINESS_DATE} 15:00:00 MUST be included
2. **Given** BOND_FUT records outside trading hours exist, **When** data is retrieved, **Then** these records MUST be excluded from the result set
3. **Given** a validation task for non-BOND_FUT data types, **When** records are retrieved, **Then** no time filter MUST be applied

---

### User Story 3 - Simplify Record Matching to Position-Based Comparison (Priority: P1)

As a data validation engineer, I need records to be matched based on their position in the sorted result set rather than complex key combinations, so that the validation logic is simpler and more predictable.

**Why this priority**: This is the core change in matching logic that simplifies the entire validation process and makes it easier to understand and maintain.

**Independent Test**: Can be fully tested by validating that records are matched purely by their sequence index after sorting, delivering consistent and predictable validation results.

**Acceptance Scenarios**:

1. **Given** sorted result sets from left and right sources, **When** matching occurs, **Then** record at position 1 in left MUST match with record at position 1 in right
2. **Given** sorted result sets of unequal size, **When** matching occurs, **Then** records beyond the smaller set size MUST be flagged as unpaired
3. **Given** matched record pairs, **When** validation rules are applied, **Then** field comparisons MUST be performed between the paired records

---

### Edge Cases

- What happens when left and right result sets have different sizes after filtering and sorting?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST sort all records retrieved from left and right data sources using DolphinDB's `ORDER BY receive_time, exch_product_id, settle_speed` clause. This ordering MUST be executed in both DolphinDB instances via SQL queries before matching.
- **FR-002**: System MUST filter BOND_FUT data type records to include only those with receive_time greater than {BUSINESS_DATE} 09:30:00 and less than {BUSINESS_DATE} 15:00:00
- **FR-003**: System MUST match records from left and right sources based on their sequential position in the sorted result sets (e.g., position N in left matches position N in right)
- **FR-004**: System MUST handle mismatched result set sizes by flagging excess records as unpaired. If both left and right result sets are empty (zero records) after filtering, validation proceeds normally with this condition reported.
- **FR-005**: System MUST NOT apply the trading hours filter to data types other than BOND_FUT
- **FR-006**: System MUST maintain receive_time values in records after sorting for audit and reporting purposes

### Key Entities *(include if feature involves data)*

- **Validation Result**: Represents the outcome of comparing paired records from left and right sources, containing matched fields, differences, and validation status
- **Record Pair**: Represents two records (one from left source, one from right source) that are matched based on their position in sorted sequences
- **Business Date**: Represents the trading date used for filtering and time window calculations in BOND_FUT data

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Records from both data sources are sorted by receive_time before matching in 100% of validation tasks
- **SC-002**: BOND_FUT validation tasks only include records within trading hours (09:30:00 - 15:00:00) with 100% accuracy
- **SC-003**: Record matching by position completes in under 10 seconds for result sets up to 10,000 records
- **SC-004**: Validation reports correctly indicate paired and unpaired records with 100% accuracy
- **SC-005**: Users can verify record matching logic by inspecting sorted sequences and position numbers in validation reports
