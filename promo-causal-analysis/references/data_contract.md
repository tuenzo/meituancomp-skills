# Data Contract

## Purpose

Use this reference to decide whether the input is sufficient for `full`, `did_only`, or `localgap_only` execution.

Do not start modeling until the minimum contract is satisfied.

## Accepted Input Shapes

Accept either:

1. Raw source tables:
   - `orders`
   - `exposure`
   - `activity_calendar`
2. A pre-built category-day panel

## Minimum Viable Contract

The minimum contract for any runnable analysis is:

- a daily date field
- a category identifier that can support category-day aggregation
- a reliable activity indicator, either directly present or derivable from an activity calendar
- a sales measure that can represent category-day GMV

If any of the four items above is missing, stop causal analysis and report the blocking gap.

## Raw Table Requirements

### `orders`

Required fields:

- `date`
- category key such as `category_name_cn`, `category_id`, or a documented equivalent
- sales amount such as `sku_sale_amt`, `gmv`, or an equivalent transaction-level revenue field

Optional fields:

- `sale_num`
- `order_cnt`
- `buy_uv`
- `discount_rate`

### `exposure`

Required fields only if exposure analysis is requested:

- `date`
- category key aligned with `orders`
- `view_uv` or an equivalent exposure measure

Optional fields:

- impressions
- click UV
- channel split fields

### `activity_calendar`

Required fields unless `is_activity` is already present in the panel or raw fact tables:

- `date`
- `is_activity`

Optional fields:

- activity name
- activity type
- campaign ID

## Standardized Category-Day Panel Schema

Normalize to the following field set where available.

Required output fields:

- `date`
- `category_name_cn`
- `is_activity`
- `gmv`

Recommended fields:

- `sale_num`
- `order_cnt`
- `discount_rate`
- `view_uv`
- `buy_uv`

Helper fields:

- `weekday`
- `month`
- `day_of_month`
- `dist2pay`
- `is_month_end`

Derived fields when source columns exist:

- `conversion_rate = buy_uv / view_uv`
- `log_view_uv = log(view_uv + 1)`

## Validation Rules

Validate these checks before downstream modeling:

- dates parse cleanly and aggregate to day
- category-day keys are unique after aggregation
- activity and non-activity dates both exist
- panel coverage is long enough to include historical non-activity observations
- missing rate is reported for `gmv`, `discount_rate`, `view_uv`, and `buy_uv`

## Downgrade Rules

Apply these downgrade rules explicitly and disclose them in outputs.

| Condition | Action |
| --- | --- |
| Missing `view_uv` | Skip exposure DID and omit `ExcessView` terms |
| Missing `discount_rate` | Skip discount DID and omit `ExcessDiscount` terms |
| Missing both `view_uv` and `discount_rate` | Skip decomposition into exposure and discount channels |
| Missing `buy_uv` | Do not compute conversion metrics |
| Missing `activity_calendar` and no `is_activity` source | Stop causal workflow; descriptive analysis only if the user agrees |
| Insufficient non-activity history | Mark `LocalBaseline` unavailable and downgrade to descriptive analysis plus limited regression if feasible |
| Category-day cells too sparse | Aggregate to a coarser category level or disclose that the slice is not estimable |

## LocalGap Entry Contract

Run LocalGap only when all conditions below hold:

- `gmv` is available at category-day level
- `is_activity` is available
- at least one historical non-activity observation exists for each estimable category
- at least 2 matched observations are available for a hard minimum baseline

Treat 4 matched observations as the recommended minimum. Mark any baseline built on 2 or 3 matches as `weak`.

## DID Entry Contract

Run DID or event-study only when all conditions below hold:

- an event date or event window can be defined
- a treatment intensity variable can be constructed from exposure or discount data
- pre-period coverage is sufficient for trend checks

If treatment is defined from realized activity-period intensity, describe the result as intensity-group comparison rather than a clean treatment assignment design.

## Output Artifacts

Expect these outputs from a successful run:

- validated category-day panel or panel summary
- data quality report
- mode-specific tables and model outputs
- downgrade log with reasons and consequences
