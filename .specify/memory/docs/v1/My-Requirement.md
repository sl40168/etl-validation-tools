
As a data engineer, I have two data sources, I need to validate the data from the two data sources are consistent.

I. Target of Data Sources

1. Both data sources are in DolphinDB, but in different DolphinDB instances.
2. The connection information regarding two DolphinDB instances **MUST** be provided by an INI configure file, which **MUST** be passed in as a parameter to execute CLI. The parameter is `--config`.

II. The scope of validation

1. The data need to be validated are in the same table in both DolphinDB.
2. Table name is `marekt_price`.
3. We **ONLY** validate **ONE DAY** each time, and the date **MUST** be provided as a parementer to execute CLI. The paremeter is `--date`.
4. Passed in date **MUST** be in the format of `YYYYMMDD`.
5. The data need to be validated **MUST** be extracted by below SQL, in which the `BUSINESS_DATE` **MUST** use passed in `date` and in format of `YYYY.MM.DD`.
```sql
SELECT * FROM marekt_price WHERE business_date = ${BUSINESS_DATE}
```

III. Description of Data

1. Table structure:

| NAME | TYPE |
|------|------|
| business_date | DATE |
| exch_product_id | SYMBOL |
| product_type | SYMBOL |
| exchange | SYMBOL |
| source | SYMBOL |
| settle_speed | INT |
| last_trade_price | DOUBLE |
| last_trade_yield | DOUBLE |
| last_trade_yield_type | SYMBOL |
| last_trade_volume | DOUBLE |
| last_trade_turnover | DOUBLE |
| last_trade_interest | DOUBLE |
| last_trade_side | SYMBOL |
| level | SYMBOL |
| status | SYMBOL |
| pre_close_price | DOUBLE |
| pre_settle_price | DOUBLE |
| pre_interest | DOUBLE |
| open_price | DOUBLE |
| high_price | DOUBLE |
| low_price | DOUBLE |
| close_price | DOUBLE |
| settle_price | DOUBLE |
| upper_limit | DOUBLE |
| lower_limit | DOUBLE |
| total_volume | DOUBLE |
| total_turnover | DOUBLE |
| open_interest | DOUBLE |
| bid_0_price | DOUBLE |
| bid_0_yield | DOUBLE |
| bid_0_yield_type | SYMBOL |
| bid_0_tradable_volume | DOUBLE |
| bid_0_volume | DOUBLE |
| offer_0_price | DOUBLE |
| offer_0_yield | DOUBLE |
| offer_0_yield_type | SYMBOL |
| offer_0_tradable_volume | DOUBLE |
| offer_0_volume | DOUBLE |
| bid_1_price | DOUBLE |
| bid_1_yield | DOUBLE |
| bid_1_yield_type | SYMBOL |
| bid_1_tradable_volume | DOUBLE |
| bid_1_volume | DOUBLE |
| offer_1_price | DOUBLE |
| offer_1_yield | DOUBLE |
| offer_1_yield_type | SYMBOL |
| offer_1_tradable_volume | DOUBLE |
| offer_1_volume | DOUBLE |
| bid_2_price | DOUBLE |
| bid_2_yield | DOUBLE |
| bid_2_yield_type | SYMBOL |
| bid_2_tradable_volume | DOUBLE |
| bid_2_volume | DOUBLE |
| offer_2_price | DOUBLE |
| offer_2_yield | DOUBLE |
| offer_2_yield_type | SYMBOL |
| offer_2_tradable_volume | DOUBLE |
| offer_2_volume | DOUBLE |
| bid_3_price | DOUBLE |
| bid_3_yield | DOUBLE |
| bid_3_yield_type | SYMBOL |
| bid_3_tradable_volume | DOUBLE |
| bid_3_volume | DOUBLE |
| offer_3_price | DOUBLE |
| offer_3_yield | DOUBLE |
| offer_3_yield_type | SYMBOL |
| offer_3_tradable_volume | DOUBLE |
| offer_3_volume | DOUBLE |
| bid_4_price | DOUBLE |
| bid_4_yield | DOUBLE |
| bid_4_yield_type | SYMBOL |
| bid_4_tradable_volume | DOUBLE |
| bid_4_volume | DOUBLE |
| offer_4_price | DOUBLE |
| offer_4_yield | DOUBLE |
| offer_4_yield_type | SYMBOL |
| offer_4_tradable_volume | DOUBLE |
| offer_4_volume | DOUBLE |
| bid_5_price | DOUBLE |
| bid_5_yield | DOUBLE |
| bid_5_yield_type | SYMBOL |
| bid_5_tradable_volume | DOUBLE |
| bid_5_volume | DOUBLE |
| offer_5_price | DOUBLE |
| offer_5_yield | DOUBLE |
| offer_5_yield_type | SYMBOL |
| offer_5_tradable_volume | DOUBLE |
| offer_5_volume | DOUBLE |
| event_time_trade | TIMESTAMP |
| receive_time_trade | TIMESTAMP |
| create_time_trade | TIMESTAMP |
| event_time_quote | TIMESTAMP |
| receive_time_quote | TIMESTAMP |
| create_time_quote | TIMESTAMP |
| tick_type | SYMBOL |
| receive_time | TIMESTAMP |
| create_time | TIMESTAMP |
| store_time | TIMESTAMP |

2. Data contains the market price of 2 types of `product_type`, which are `BOND` and `BOND_FUT`.
3. For `BOND` product_type, we have 2 types of `tick_type`, which are `TRADE` and `QUOTE`, for `BOND_FUT` product_type, we have 1 type of `tick_type`, which is `SNAPSHOT`.
4. For `BOND` product_type, we have 2 types of `settle_speed`, which are `0` and `1`.
5. For ALL product_type, we have at most 6 levels * 2 sides of quotes, from `bid_0` to `offer_5`.

IV. Description of Validation

1. I would like to validate data in 3 groups: 
   - `product_type = 'BOND' and tick_type = 'TRADE'`
   - `product_type = 'BOND' and tick_type = 'QUOTE'`
   - `product_type = 'BOND_FUT' and tick_type = 'SNAPSHOT'`

2. In each group, I would like to match the data from two data sources by the combination of below columns:
   - `receive_time`
   - `exch_product_id`
   - `settle_speed`

3. For each matched record pair, I would like to compare the following columns:
   - `business_date`
   - `exch_product_id`
   - `product_type`
   - `exchange`
   - `source`
   - `settle_speed`
   - `last_trade_price`
   - `last_trade_yield`
   - `last_trade_yield_type`
   - `last_trade_volume`
   - `last_trade_turnover`
   - `last_trade_interest`
   - `last_trade_side`
   - `level`
   - `status`
   - `pre_close_price`
   - `pre_settle_price`
   - `pre_interest`
   - `open_price`
   - `high_price`
   - `low_price`
   - `close_price`
   - `settle_price`
   - `upper_limit`
   - `lower_limit`
   - `total_volume`
   - `total_turnover`
   - `open_interest`
   - `bid_0_price`
   - `bid_0_yield`
   - `bid_0_yield_type`
   - `bid_0_tradable_volume`
   - `bid_0_volume`
   - `offer_0_price`
   - `offer_0_yield`
   - `offer_0_yield_type`
   - `offer_0_tradable_volume`
   - `offer_0_volume`
   - `bid_1_price`
   - `bid_1_yield`
   - `bid_1_yield_type`
   - `bid_1_tradable_volume`
   - `bid_1_volume`
   - `offer_1_price`
   - `offer_1_yield`
   - `offer_1_yield_type`
   - `offer_1_tradable_volume`
   - `offer_1_volume`
   - `bid_2_price`
   - `bid_2_yield`
   - `bid_2_yield_type`
   - `bid_2_tradable_volume`
   - `bid_2_volume`
   - `offer_2_price`
   - `offer_2_yield`
   - `offer_2_yield_type`
   - `offer_2_tradable_volume`
   - `offer_2_volume`
   - `bid_3_price`
   - `bid_3_yield`
   - `bid_3_yield_type`
   - `bid_3_tradable_volume`
   - `bid_3_volume`
   - `offer_3_price`
   - `offer_3_yield`
   - `offer_3_yield_type`
   - `offer_3_tradable_volume`
   - `offer_3_volume`
   - `bid_4_price`
   - `bid_4_yield`
   - `bid_4_yield_type`
   - `bid_4_tradable_volume`
   - `bid_4_volume`
   - `offer_4_price`
   - `offer_4_yield`
   - `offer_4_yield_type`
   - `offer_4_tradable_volume`
   - `offer_4_volume`
   - `bid_5_price`
   - `bid_5_yield`
   - `bid_5_yield_type`
   - `bid_5_tradable_volume`
   - `bid_5_volume`
   - `offer_5_price`
   - `offer_5_yield`
   - `offer_5_yield_type`
   - `offer_5_tradable_volume`
   - `offer_5_volume`
   - `event_time_trade`
   - `receive_time_trade`
   - `event_time_quote`
   - `receive_time_quote`
   - `tick_type`
   - `receive_time`

4. If there is no record matched on another side, no matter lack of left or right side, I would like to mark it as `NO_MATCH`.

V. The process

1. I would like to break the whole process down to 3 separated steps, base on 3 groups mentioned in IV.1.

2. Each step **ONLY** retrieve data from both DolphinDB instances with additional filter mentioned in IV.1.

3. By default, the process execute 3 separated steps in sequence, but I would like to add a parameter to indicate the certain step to execute.

VI. The output

1. I would like to generate a report for each step, which contains the following information:
   - The number of records retrieved from DolphinDB instances.
   - The number of records matched.
   - The number of records unmatched, **MUST** include the column name of unmatched.
   - The number of records unmatched on left side.
   - The number of records unmatched on right side.

2. I would like this report be in Markdown format.