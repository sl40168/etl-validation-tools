# Quick Start: Record Matching Logic Enhancement

**Feature**: [006-record-matching](./spec.md) | **Date**: 2026-01-15

## Overview

This guide helps you quickly understand and test the enhanced record matching logic. The feature changes how records from left and right DolphinDB instances are compared: instead of using composite keys, records are now matched by their sequential position after SQL-level sorting.

---

## What Changed?

### Before (Composite Key Matching)

```python
# Old approach: Match by composite key
merged_df = pd.merge(
    left_df,
    right_df,
    on=['receive_time', 'exch_product_id', 'settle_speed'],
    how='outer',
    indicator=True
)

# Records matched if all three keys match
# Sorting happened post-retrieval
```

### After (Position-Based Matching)

```python
# New approach: Match by position
min_len = min(len(left_df), len(right_df))
for i in range(min_len):
    # Match position i in left with position i in right
    compare(left_df.iloc[i], right_df.iloc[i])

# Records sorted at database level
# Simpler, faster, more predictable
```

---

## Key Features

### 1. SQL-Level Sorting

Records are now sorted in DolphinDB before retrieval:

```sql
-- Both left and right instances use same query
select * from loadTable("dfs://market_data", "market_price_stream_temp")
where business_date = 2026.01.06
  and product_type = `BOND_FUT
order by receive_time, exch_product_id, settle_speed
```

**Benefits**:
- Consistent ordering across both instances
- No post-retrieval sorting needed
- Reduced data transfer overhead

---

### 2. Time-Based Filtering (BOND_FUT Only)

Bond futures data is filtered to trading hours:

```sql
-- Added time filter for BOND_FUT
and receive_time > datetime('2026.01.06 09:30:00')
and receive_time < datetime('2026.01.06 15:00:00')
```

**Benefits**:
- Only active trading data validated
- Improved validation accuracy
- Reduced data processing volume

---

### 3. Position-Based Matching

Records matched by sequence number (1st with 1st, 2nd with 2nd, etc.):

```python
# Simplified matching logic
def match_records_by_position(left_df, right_df):
    min_len = min(len(left_df), len(right_df))

    # Match by position
    matched_pairs = [
        (left_df.iloc[i], right_df.iloc[i])
        for i in range(min_len)
    ]

    # Unpaired records
    left_unpaired = left_df.iloc[min_len:]
    right_unpaired = right_df.iloc[min_len:]

    return matched_pairs, left_unpaired, right_unpaired
```

**Benefits**:
- Eliminates complex merge operations
- Easier to understand and maintain
- Faster execution (~5-8s for 10k records)

---

## Usage

### Running Validation

The CLI interface remains unchanged. Run validation as before:

```bash
# Basic validation (uses new position-based matching by default)
python -m src.cli.main \
  --config config/validation_config.ini \
  --date 2026.01.06 \
  --step 3

# Explicitly specify matching strategy (for testing)
python -m src.cli.main \
  --config config/validation_config.ini \
  --date 2026.01.06 \
  --step 3 \
  --matching-strategy position
```

### New CLI Parameter

```bash
--matching-strategy
    Strategy for matching records from left/right sources
    Choices: position (default), composite (deprecated)
```

---

## Testing

### Unit Tests

Test the new matching logic:

```bash
# Run matcher tests
cd src
pytest tests/unit/validation/test_matcher.py -v

# Run query tests (with ORDER BY and time filter)
pytest tests/unit/db/test_query.py -v
```

### Integration Tests

Test end-to-end validation flow:

```bash
# Full integration test
pytest tests/integration/test_record_matching_flow.py -v

# Test with sample data
python tests/integration/test_record_matching_flow.py \
  --date 2026.01.06 \
  --product-type BOND_FUT
```

### Manual Testing

Test with real DolphinDB instances:

```bash
# Test BOND_FUT with time filter
python -m src.cli.main \
  --config config/validation_config.ini \
  --date 2026.01.06 \
  --step 3

# Verify only records within 09:30-15:00 are included

# Test BOND (no time filter)
python -m src.cli.main \
  --config config/validation_config.ini \
  --date 2026.01.06 \
  --step 2

# Verify all records for the day are included
```

---

## Verification Checklist

After running validation, verify:

- [ ] Records are sorted by `receive_time, exch_product_id, settle_speed`
- [ ] BOND_FUT data only includes records within 09:30:00-15:00:00
- [ ] Other data types (BOND, XBOND) include all records for the day
- [ ] Record N in left matches record N in right (by position)
- [ ] Excess records are flagged as unpaired
- [ ] Validation completes in <10 seconds for 10,000 records
- [ ] Report shows correct paired and unpaired counts

---

## Troubleshooting

### Issue: Records not matching as expected

**Symptom**: Paired records have different data

**Check**:
```python
# Verify both sides use same ORDER BY
print(left_query)  # Should have: order by receive_time, exch_product_id, settle_speed
print(right_query) # Should have: order by receive_time, exch_product_id, settle_speed

# Verify data is sorted
print(left_df[['receive_time', 'exch_product_id', 'settle_speed']].head())
print(right_df[['receive_time', 'exch_product_id', 'settle_speed']].head())
```

---

### Issue: BOND_FUT returns empty results

**Symptom**: Zero records after filtering

**Check**:
```bash
# Verify business date has data
# Check if any records exist for the date (ignoring time filter)

# Check if any records exist within trading hours
# Verify time zone handling
```

---

### Issue: Performance slower than expected

**Symptom**: Validation takes >10 seconds for 10,000 records

**Check**:
```python
# Verify sorting is done at database level
# Look for "order by" in SQL query

# Verify no post-retrieval sorting
# Check for sort() calls in Python code

# Verify position-based matching is used
# Check that match_records_by_position() is called
```

---

## Migration from Old Matching

If you have existing validation workflows using composite key matching:

1. **Test new matching strategy**:
   ```bash
   python -m src.cli.main \
     --config config/validation_config.ini \
     --date 2026.01.06 \
     --step 3 \
     --matching-strategy position
   ```

2. **Compare results**:
   - Review validation reports
   - Check paired/unpaired counts
   - Verify data differences

3. **Switch to new strategy**:
   - Remove `--matching-strategy` parameter (uses default `position`)
   - Update any automation scripts

4. **Monitor for issues**:
   - Watch for unexpected unpaired records
   - Check validation status changes
   - Report any discrepancies

---

## Performance Benchmarks

Expected performance for 10,000 records:

| Metric | Old (Composite) | New (Position) | Improvement |
|--------|------------------|-----------------|-------------|
| Execution Time | 12-15 seconds | 5-8 seconds | ~40-50% faster |
| Memory Usage | ~120 MB | ~85 MB | ~30% reduction |
| Code Complexity | High (merge logic) | Low (direct indexing) | Easier to maintain |

---

## Next Steps

1. **Review the implementation**:
   - [data-model.md](./data-model.md) - Data structures and flow
   - [research.md](./research.md) - Technical decisions

2. **Run tests**:
   - Unit tests for matcher and query modules
   - Integration tests for end-to-end flow

3. **Validate with real data**:
   - Test with production-like data
   - Verify time filter for BOND_FUT
   - Compare with old matching results

4. **Deploy to production**:
   - Update validation schedules
   - Monitor validation reports
   - Report any issues

---

## Getting Help

If you encounter issues:

1. Check [data-model.md](./data-model.md) for data structure details
2. Review [research.md](./research.md) for implementation decisions
3. Run unit tests to identify specific issues
4. Check logs for SQL queries and matching details
5. Report bugs with reproduction steps

---

**Feature Branch**: `006-record-matching`
**Status**: Ready for implementation
**Next Command**: `/speckit.tasks` to generate task breakdown
