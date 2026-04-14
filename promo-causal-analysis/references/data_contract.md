# Data Contract

## Purpose

Use this reference to determine whether the data can support the full workflow or only a downgraded subset. Do not start causal interpretation until the minimum contract is satisfied.

## Accepted Input Shapes

Accept either:

1. Raw source tables:
   - `orders`
   - `exposure`
   - `activity_calendar`
2. A pre-built `category-day panel`

## Minimum Viable Contract

The minimum contract for any runnable version of this skill is:

- a daily date field
- a category identifier that supports `category x day` aggregation
- a reliable activity indicator, either directly present or derivable
- a sales measure that represents category-day GMV

If any minimum item is missing, stop causal workflow and explicitly report the blocking gap.

## Raw Table Requirements

### `orders`

Required fields:

- `date`
- category field such as `category_name_cn` or `category_id`
- sales field such as `gmv` or `sku_sale_amt`

Optional fields:

- `sale_num`
- `order_cnt`
- `buy_uv`
- `discount_rate`
- SKU identifier for exposure roll-up

### `exposure`

Required fields only when exposure-based modules are requested:

- `date`
- category field aligned with `orders`, or SKU field plus a defensible SKU-to-category mapping
- `view_uv` or an equivalent exposure measure

Optional fields:

- impressions
- click UV
- channel split fields

### `activity_calendar`

Required fields unless `is_activity` is already present and trustworthy:

- `date`
- `is_activity`

Optional fields:

- activity name
- activity type
- campaign ID

## Standardized Category-Day Panel Schema

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
- baseline-quality flags for LocalGap

## Grain Rules

- default analysis grain is `category x day`
- if the raw data is finer than day, aggregate upward before modeling
- if the raw data is coarser than `category x day`, disclose the loss of within-category timing resolution

## Missing and Zero Handling

- treat missing structural fields as blockers
- treat observed zero-sales or zero-exposure days as valid rows unless they are explicit data errors
- report missingness and zero shares separately
- do not silently replace missing exposure or discount fields with zero

## Exposure at `SKU x day` Only

Default handling:

1. use a documented SKU-to-category mapping from the product dimension or order table
2. aggregate `view_uv` from `SKU x day` to `category x day`
3. disclose any SKU rows that could not be mapped

If no mapping exists, downgrade all exposure-based modules and state that the exposure signal is unavailable at the required grain.

## Validation Rules

Validate these checks before downstream modeling:

- dates parse cleanly and aggregate to day
- category-day keys are unique after aggregation
- activity and non-activity dates both exist
- panel coverage is long enough to include historical non-activity observations
- missing rate is reported for `gmv`, `discount_rate`, `view_uv`, and `buy_uv`
- zero shares are reported for `gmv`, `view_uv`, and `buy_uv`

## Module Entry Contracts

### EDA

Requires:

- valid `category-day panel`
- at least one activity row and one non-activity row

### PSM + DID / Event Study

Requires:

- event window or activity period definition
- treatment intensity variable from exposure, discount, or a documented activity-intensity proxy
- sufficient pre-period coverage
- enough covariates to support matching or, if not available, an explicit downgrade to unmatched DID

### LocalGap

Requires:

- `gmv` at `category x day`
- `is_activity`
- historical non-activity rows
- at least 2 matched observations for the hard minimum baseline

Treat 4 matched observations as the recommended minimum. Mark baselines built on 2 or 3 matches as `weak`.

### GPS

Requires:

- continuous treatment variable
- outcome variable such as `local_gap` or `gmv`
- enough overlap to estimate treatment support

### Uplift

Requires:

- a defensible treatment definition
- outcome variable
- time-safe validation split
- enough repeated observations to assess fold stability

## Downgrade Rules

Apply downgrade rules explicitly and keep them attached to final reporting.

| Condition | Action |
| --- | --- |
| Missing `view_uv` | Skip exposure DID, GPS on exposure dose, and exposure decomposition terms |
| Missing `discount_rate` | Skip discount DID, GPS on discount dose, and discount decomposition terms |
| Missing both `view_uv` and `discount_rate` | Skip channel decomposition and continuous-dose modules; keep LocalGap total only |
| Missing `buy_uv` | Do not compute conversion metrics |
| Missing `activity_calendar` and no reliable `is_activity` source | Stop causal workflow; allow descriptive only if user accepts the downgrade |
| Insufficient non-activity history | Mark `LocalBaseline` unavailable and downgrade LocalGap to limited or unavailable |
| Sparse category-day panel | Aggregate to a coarser category level or mark the slice as non-estimable |
| Weak overlap for GPS | Restrict interpretation to supported treatment region or skip GPS entirely |
| Unstable uplift folds | Keep uplift exploratory and do not operationalize priority buckets aggressively |

## Output Artifacts

Expect these outputs from a successful run:

- validated category-day panel
- data quality report
- downgrade log with reasons and consequences
- module-specific tables and summaries
