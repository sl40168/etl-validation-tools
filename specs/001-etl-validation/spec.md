# Feature Specification: DolphinDB ETL Data Validation Tool

**Feature Branch**: `001-etl-validation`  
**Created**: 2026-01-15  
**Status**: Draft  
**Input**: User description: "Create ETL data validation tool for comparing data between two DolphinDB instances for market price data"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validate Market Price Data Between Two DolphinDB Instances (Priority: P1)

As a data engineer, I need to validate that market price data from two different DolphinDB instances are consistent by retrieving data for a specific date, matching records across instances, and comparing all relevant fields to identify discrepancies.

**Why this priority**: This is the core functionality that enables data quality assurance for market price data, which is critical for financial operations and compliance. Without this capability, data engineers cannot detect or resolve data inconsistencies between environments.

**Independent Test**: Can be fully tested by running the validation tool against two DolphinDB test instances with known identical and differing data, then verifying the generated report correctly identifies matched and unmatched records with specific column differences.

**Acceptance Scenarios**:

1. **Given** two DolphinDB instances with connection details in a config file, **When** user executes the tool with a valid date parameter, **Then** the tool retrieves all market price records for that date from both instances
2. **Given** retrieved data from both instances, **When** records are matched by receive_time, exch_product_id, and settle_speed, **Then** the tool correctly identifies all matching record pairs and unmatched records
3. **Given** matched record pairs, **When** comparing all specified columns, **Then** the report identifies which columns differ between the two data sources
4. **Given** records that exist in only one instance, **When** no match is found in the other instance, **Then** these records are marked as NO_MATCH and categorized by left-side or right-side absence

---

### User Story 2 - Generate Comprehensive Validation Reports (Priority: P1)

As a data engineer, I need a detailed Markdown report for each validation group showing statistics on retrieved records, matched records, unmatched records by column, and unmatched records by side, so I can quickly assess data quality and identify areas requiring investigation.

**Why this priority**: Without clear, actionable reports, data engineers cannot efficiently identify and resolve data discrepancies. The report format is essential for documentation and communication with stakeholders.

**Independent Test**: Can be fully tested by running the validation and verifying the generated Markdown file contains all required sections with accurate counts and is properly formatted for display.

**Acceptance Scenarios**:

1. **Given** a completed validation step, **When** the report is generated, **Then** it includes total records retrieved from each DolphinDB instance
2. **Given** matched and unmatched records, **When** the report is generated, **Then** it displays the count of matched records and unmatched records with column names where differences occurred
3. **Given** unmatched records, **When** the report is generated, **Then** it separately counts records unmatched on the left side versus right side
4. **Given** a validation step, **When** the report is generated, **Then** it is formatted as valid Markdown with clear section headers

---

### User Story 3 - Execute Validation for Specific Product Type Groups (Priority: P2)

As a data engineer, I need to run validation for three specific product type groups (BOND/TRADE, BOND/QUOTE, BOND_FUT/SNAPSHOT) either all together or individually, so I can focus validation efforts on specific market data types as needed.

**Why this priority**: This provides flexibility to validate all data types in one run or focus on specific groups when investigating issues or doing targeted testing.

**Independent Test**: Can be fully tested by running the tool with and without the step parameter and verifying that only the specified validation groups are executed.

**Acceptance Scenarios**:

1. **Given** no step parameter is provided, **When** the tool executes, **Then** it runs validation for all three product type groups in sequence
2. **Given** a specific step number (1, 2, or 3) is provided, **When** the tool executes, **Then** it only runs validation for that specific product type group
3. **Given** a step is selected, **When** data is retrieved from DolphinDB, **Then** only records matching that group's product_type and tick_type criteria are included

---

### User Story 4 - Configure Multiple DolphinDB Connections (Priority: P2)

As a data engineer, I need to provide connection information for two DolphinDB instances through an INI configuration file passed as a command-line parameter, so I can easily switch between different instance pairs without modifying code.

**Why this priority**: Configuration management is essential for operational flexibility and security, keeping credentials out of code and enabling environment-specific configurations.

**Independent Test**: Can be fully tested by creating INI files with different connection parameters and verifying the tool correctly reads and uses the specified connections.

**Acceptance Scenarios**:

1. **Given** an INI configuration file with valid DolphinDB connection details, **When** the tool is executed with --config parameter pointing to the file, **Then** it successfully connects to both DolphinDB instances
2. **Given** the --config parameter is missing or points to an invalid file, **When** the tool executes, **Then** it displays a clear error message indicating the configuration issue
3. **Given** connection parameters in the INI file, **When** the tool attempts to connect, **Then** it uses the correct connection details for each instance (source and target)

---

### Edge Cases

- What happens when the specified date has no records in one or both DolphinDB instances?
- How does the system handle connection failures or timeouts to DolphinDB instances?
- What happens when the configuration file is malformed or missing required parameters?
- How does the system handle records with NULL values in the matching columns (receive_time, exch_product_id, settle_speed)?
- What happens when date parameter is in invalid format (not YYYYMMDD)?
- How does the system handle very large result sets that might exceed memory limits?
- What happens when duplicate matching records exist within a single instance?
- How does the system handle timestamp precision differences between instances?
- If a validation step fails after 3 retry attempts, the system stops execution and reports the error without attempting remaining steps

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST read DolphinDB connection information for two instances from an INI configuration file specified via --config command-line parameter
- **FR-001-1**: System MUST retry failed connection attempts or queries up to 3 times before stopping execution and reporting the error
- **FR-002**: System MUST accept a --date command-line parameter in YYYYMMDD format specifying the business date to validate
- **FR-003**: System MUST retrieve market price data from both DolphinDB instances for the specified date using the query pattern `SELECT * FROM market_price WHERE business_date = {formatted_date}`
- **FR-004**: System MUST format the date parameter as YYYY.MM.DD when building the SQL query
- **FR-005**: System MUST execute validation in three distinct groups based on product_type and tick_type: BOND/TRADE, BOND/QUOTE, and BOND_FUT/SNAPSHOT
- **FR-006**: System MUST match records from two data sources using the combination of receive_time, exch_product_id, and settle_speed columns
- **FR-007**: System MUST compare the following 84 columns for each matched record pair: business_date, exch_product_id, product_type, exchange, source, settle_speed, last_trade_price, last_trade_yield, last_trade_yield_type, last_trade_volume, last_trade_turnover, last_trade_interest, last_trade_side, level, status, pre_close_price, pre_settle_price, pre_interest, open_price, high_price, low_price, close_price, settle_price, upper_limit, lower_limit, total_volume, total_turnover, open_interest, bid_0_price, bid_0_yield, bid_0_yield_type, bid_0_tradable_volume, bid_0_volume, offer_0_price, offer_0_yield, offer_0_yield_type, offer_0_tradable_volume, offer_0_volume, bid_1_price, bid_1_yield, bid_1_yield_type, bid_1_tradable_volume, bid_1_volume, offer_1_price, offer_1_yield, offer_1_yield_type, offer_1_tradable_volume, offer_1_volume, bid_2_price, bid_2_yield, bid_2_yield_type, bid_2_tradable_volume, bid_2_volume, offer_2_price, offer_2_yield, offer_2_yield_type, offer_2_tradable_volume, offer_2_volume, bid_3_price, bid_3_yield, bid_3_yield_type, bid_3_tradable_volume, bid_3_volume, offer_3_price, offer_3_yield, offer_3_yield_type, offer_3_tradable_volume, offer_3_volume, bid_4_price, bid_4_yield, bid_4_yield_type, bid_4_tradable_volume, bid_4_volume, offer_4_price, offer_4_yield, offer_4_yield_type, offer_4_tradable_volume, offer_4_volume, bid_5_price, bid_5_yield, bid_5_yield_type, bid_5_tradable_volume, bid_5_volume, offer_5_price, offer_5_yield, offer_5_yield_type, offer_5_tradable_volume, offer_5_volume, event_time_trade, receive_time_trade, event_time_quote, receive_time_quote, tick_type
- **FR-007-1**: System MUST classify the 84 comparison columns into three precision categories for precision-aware comparison:
  - **Volume Fields (round to integer, precision #,####)**: last_trade_volume, last_trade_turnover, last_trade_interest, pre_interest, total_volume, total_turnover, open_interest, bid_0_tradable_volume through bid_5_tradable_volume (6 fields), bid_0_volume through bid_5_volume (6 fields), offer_0_tradable_volume through offer_5_tradable_volume (6 fields), offer_0_volume through offer_5_volume (6 fields) - total 31 fields
  - **Price Fields (round to 5 decimals, precision #,###.00000)**: last_trade_price, pre_close_price, pre_settle_price, open_price, high_price, low_price, close_price, settle_price, upper_limit, lower_limit, bid_0_price through bid_5_price (6 fields), offer_0_price through offer_5_price (6 fields) - total 20 fields
  - **Yield Fields (round to 5 decimals, precision #.00000)**: last_trade_yield, bid_0_yield through bid_5_yield (6 fields), offer_0_yield through offer_5_yield (6 fields) - total 13 fields
- **FR-008**: System MUST identify records with no match in the other data source and mark them as NO_MATCH
- **FR-009**: System MUST separately track and report unmatched records that exist only in the left instance versus only in the right instance
- **FR-010**: System MUST generate separate Markdown files for each validation group with meaningful filenames indicating the product type and tick type along with the validation date (e.g., validation_BOND_TRADE_YYYYMMDD.md, validation_BOND_QUOTE_YYYYMMDD.md, validation_BOND_FUT_SNAPSHOT_YYYYMMDD.md) in a dedicated `reports` subdirectory in the current working directory, containing: total records retrieved from each instance, number of matched records, number of unmatched records with column names, count of left-side unmatched records, and count of right-side unmatched records
- **FR-011**: System MUST support an optional parameter to execute only a specific validation step (1, 2, or 3) instead of all three
- **FR-012**: System MUST accept only a single step parameter and display an error if multiple step parameters are provided
- **FR-013**: System MUST default to executing all three validation steps when no specific step is provided
- **FR-014**: System MUST retrieve data from both DolphinDB instances for each validation group with the appropriate product_type and tick_type filters applied

### Key Entities

- **DolphinDB Connection**: Represents connection details (host, port, credentials, database) for a DolphinDB instance, configured via INI file
- **Market Price Record**: Represents a single market price data row containing 100 fields including identifiers (exch_product_id, product_type, exchange, source), pricing data (last_trade_price, bid/offer prices), timestamps, and quote levels
- **Validation Group**: Represents a logical grouping of records for validation, defined by specific product_type and tick_type combinations (BOND/TRADE, BOND/QUOTE, BOND_FUT/SNAPSHOT)
- **Matched Record Pair**: Represents two records (one from each DolphinDB instance) that match based on receive_time, exch_product_id, and settle_speed
- **Unmatched Record**: Represents a record from one instance that has no corresponding record in the other instance, categorized as left-side or right-side unmatched
- **Validation Report**: A Markdown document containing statistics and results for a validation group execution

## Clarifications

### Session 2026-01-15

- Q: For the step parameter that executes specific validation groups (1, 2, or 3), how should the tool behave when multiple steps are specified (e.g., `--step 1 --step 2`)? → A: Only accept a single step parameter; error if multiple steps are provided
- Q: For comparing matched record pairs, should the system compare all 100 columns in the table, or exclude certain columns from the comparison (e.g., store_time, create_time, receive_time which may legitimately differ)? → A: Compare only the 84 columns explicitly listed in the original requirements document (IV.3), which includes all fields except: create_time, store_time, and the three matching columns used for record matching (receive_time, exch_product_id, settle_speed when used as part of matching criteria)
- Q: For the validation reports, should the system generate a single combined Markdown file containing all three validation group reports, or create separate Markdown files for each group? → A: Separate Markdown files for each validation group with meaningful names indicating product type and tick type (e.g., validation_BOND_TRADE_YYYYMMDD.md, validation_BOND_QUOTE_YYYYMMDD.md, validation_BOND_FUT_SNAPSHOT_YYYYMMDD.md)
- Q: Where should the validation report files be generated and saved? → A: A dedicated `reports` subdirectory in the current working directory
- Q: If a connection failure or query error occurs during one of the three validation steps, should the tool stop execution completely or continue to the next validation group? → A: Retry the failed validation step up to 3 times, and stop execution completely if it still fails after retries

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Data engineers can complete a full validation of all three product type groups for a single business day in under 15 minutes (2,000,000 records per instance with chunked processing)
- **SC-002**: The validation tool accurately identifies 100% of record matches and unmatched records when tested against datasets with known discrepancies
- **SC-003**: Generated validation reports are produced within 30 seconds of completion and contain all required statistics in valid Markdown format
- **SC-004**: Configuration changes (switching between different DolphinDB instance pairs) can be completed by updating the INI file without any code modifications
- **SC-005**: The tool handles datasets with up to 2,000,000 records per instance without performance degradation
- **SC-006**: Error messages for configuration or connection issues are clear and actionable, enabling users to resolve issues without technical support in under 2 minutes
