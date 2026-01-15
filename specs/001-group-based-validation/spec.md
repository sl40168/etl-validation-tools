# Feature Specification: Group-Based Column Validation

**Feature Branch**: `001-group-based-validation`
**Created**: 2026-01-15
**Status**: Draft
**Input**: User description from My-Requirement.md

## Clarifications

### Session 2026-01-15

- Q: How should the system identify which validation group to use for a given dataset? → A: Require explicit group identifiers in command-line arguments (--step parameter matching group_id 1-3)
- Q: How should the system handle datasets containing columns from multiple validation groups? → A: Not applicable - single group per execution via --step parameter
- Q: What is the maximum expected dataset size that the system needs to handle? → A: 2,000,000 records per group
- Q: How should the system handle datasets with additional columns not specified in any validation group? → A: Ignore extra columns, only validate required columns
- Q: How should the system handle null/empty values in required columns? → A: If both sides are null/empty, it should be fine (pass validation)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - BOND TRADE Group Validation (Priority: P1)

As a data quality analyst, I need to validate trade data for bonds against a specific set of columns so that I can ensure the accuracy and completeness of bond trade records in the system.

**Why this priority**: Bond trade validation is critical for financial data integrity and is the most frequently used validation type.

**Independent Test**: Can be fully tested by running validation on a sample BOND TRADE dataset and verifying all 18 required columns are validated correctly.

**Acceptance Scenarios**:

1. **Given** a BOND TRADE dataset, **When** validation is executed, **Then** system validates all required columns: business_date, exch_product_id, product_type, exchange, source, settle_speed, last_trade_price, last_trade_yield, last_trade_yield_type, last_trade_volume, last_trade_turnover, last_trade_interest, last_trade_side, level, status
2. **Given** a BOND TRADE dataset missing required columns, **When** validation is executed, **Then** system reports validation failures for missing columns
3. **Given** a BOND TRADE dataset with invalid data types, **When** validation is executed, **Then** system identifies data type mismatches for each affected column

---

### User Story 2 - BOND QUOTE Group Validation (Priority: P1)

As a data quality analyst, I need to validate quote data for bonds against bid and offer columns at multiple price levels so that I can ensure market data accuracy across different quote levels.

**Why this priority**: Bond quote validation is equally critical as trade validation and involves complex multi-level price data.

**Independent Test**: Can be fully tested by running validation on a sample BOND QUOTE dataset and verifying all 60 required columns (6 price levels × 10 fields per level) are validated.

**Acceptance Scenarios**:

1. **Given** a BOND QUOTE dataset, **When** validation is executed, **Then** system validates all required bid/offer columns at levels 0-5: price, yield, yield_type, tradable_volume, and volume for each level
2. **Given** a BOND QUOTE dataset with partial quote levels, **When** validation is executed, **Then** system validates all available quote levels without errors
3. **Given** a BOND QUOTE dataset with inconsistent quote level data, **When** validation is executed, **Then** system reports inconsistencies in bid/offer price level structures

---

### User Story 3 - BOND_FUT SNAPSHOT Group Validation (Priority: P2)

As a data quality analyst, I need to validate bond futures snapshot data against both trade and quote columns plus market summary data so that I can ensure completeness of futures market data.

**Why this priority**: Bond futures validation combines multiple data types but has lower volume than plain bond data.

**Independent Test**: Can be fully tested by running validation on a sample BOND_FUT SNAPSHOT dataset and verifying all 39 required columns are validated.

**Acceptance Scenarios**:

1. **Given** a BOND_FUT SNAPSHOT dataset, **When** validation is executed, **Then** system validates all required columns including trade data, quote data (levels 0-1), and market summary data (pre_close_price, pre_settle_price, open_price, high_price, low_price, close_price, settle_price, upper_limit, lower_limit, total_volume, total_turnover, open_interest)
2. **Given** a BOND_FUT SNAPSHOT dataset missing market summary fields, **When** validation is executed, **Then** system reports specific missing market summary columns
3. **Given** a BOND_FUT SNAPSHOT dataset with quote data at levels beyond 1, **When** validation is executed, **Then** system validates only levels 0-1 as specified for this group

---

### Edge Cases

- How does system handle duplicate column names with different prefixes (e.g., bid_0_price vs bid_1_price)? Each is treated as a distinct required column
- Datasets with additional columns not in validation rules are ignored, only required columns are validated
- Null/empty values: If both left and right instances have null/empty for a column, validation passes for that column
- What happens when validation rules for a group are not defined or incomplete?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST validate data columns based on group identifiers specified via --step parameter (1-3)
- **FR-002**: System MUST support three predefined data groups:
  - Group (1, "BOND", "TRADE") with 18 required columns
  - Group (2, "BOND", "QUOTE") with 60 required columns (6 price levels × 10 fields)
  - Group (3, "BOND_FUT", "SNAPSHOT") with 39 required columns
- **FR-003**: System MUST verify presence of all required columns for the specified data group
- **FR-004**: System MUST validate data types for all required columns according to business rules
- **FR-005**: System MUST report validation failures with specific column names and error descriptions
- **FR-006**: System MUST validate only the specified group based on --step parameter, ignoring multi-group datasets
- **FR-007**: System MUST allow configuration of column validation rules for each group
- **FR-008**: System MUST provide clear validation results indicating pass/fail status for each column
- **FR-009**: System MUST ignore additional columns not specified in the validation group's required column list
- **FR-010**: System MUST treat columns where both left and right instances have null/empty values as passing validation
- **FR-011**: System MUST support extensible group definitions to add new groups in the future

### Key Entities

- **Validation Group**: Represents a data group definition containing group_id, product_type, message_type, and the list of columns to validate
- **Validation Rule**: Represents column-specific validation requirements including data type constraints and business rules
- **Validation Result**: Represents the outcome of validating a dataset, including pass/fail status per column and overall group status

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can validate any supported data group (BOND TRADE, BOND QUOTE, BOND_FUT SNAPSHOT) with 100% accuracy in identifying required columns
- **SC-002**: Validation completes for a 2,000,000-record dataset within 3-5 minutes per group (using chunked processing)
- **SC-003**: System correctly identifies all missing columns with 100% accuracy
- **SC-004**: 95% of validation results are immediately understandable without requiring technical interpretation
- **SC-005**: Adding a new data group definition takes less than 15 minutes by updating configuration only
- **SC-006**: False positive validation errors occur in less than 1% of validation runs

## Assumptions

- Group identifiers are specified via command-line arguments (--step parameter 1-3 matching group_id)
- Column names follow consistent naming conventions across datasets
- Validation rules for data types are defined externally (not in scope of this feature)
- Datasets are stored in DolphinDB instances and accessible via the Python SDK
- Users have access to sample datasets for testing each data group
- Validation groups are pre-configured and do not require runtime inference
