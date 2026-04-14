# LocalGap Method

## Role

Treat `LocalGap` as the main incremental accounting layer in this skill.

Use it to estimate how much activity-period performance exceeds a local natural benchmark that already respects cyclical demand structure.

## Why It Is the Main Layer

Global baselines are too coarse when payday, month-end, and weekday effects change the natural level of demand. LocalGap uses nearby historical non-activity observations for the same category, making the main increment estimate better aligned with the business question.

## Entry Criteria

Run LocalGap only after the panel passes the contract in [data_contract.md](data_contract.md).

Minimum entry conditions:

- panel exists
- `gmv` and `is_activity` are available
- historical non-activity observations exist
- at least 2 matched observations are available for each estimable category-day cell

## Default Parameters

| Parameter | Default | Notes |
| --- | --- | --- |
| `baseline_match` | `same_weekday` | Match cyclical weekday effects first |
| `recent_window_days` | `56` | Prefer recent non-activity history |
| `fallback_window_days` | `112` | Extend search if recent history is thin |
| `min_local_baseline_obs` | `2` | Hard minimum |
| `recommended_local_baseline_obs` | `4` | Below this threshold, flag baseline quality as weak |
| `view_transform` | `log1p` | Use `log(view_uv + 1)` when `view_uv` exists |
| `payday_anchor` | `27` | Default payday anchor for positional distance |
| `payday_spec` | `quadratic_distance` | Model position, not a literal payday amount |
| `winsorize_pct` | `0.01` | Optional robustness trim for heavy tails |

## Local Baseline Construction

For category `c` on date `t`, construct the baseline from historical observations only.

Rules:

1. use non-activity dates only
2. match the same weekday first
3. search a recent window before falling back to older history
4. average the matched observations when the hard minimum is met

Define:

`LocalBaseline_ct = mean(historical non-activity GMV for category c matched to date t)`

Set baseline quality flags:

- `strong`: at least 4 matched observations
- `weak`: 2 or 3 matched observations
- `unavailable`: fewer than 2 matched observations

Do not impute a LocalBaseline when the hard minimum is not met.

## LocalGap Definition

Define:

`LocalGap_ct = ActualGMV_ct - LocalBaseline_ct`

Estimate the main model on activity-period samples with non-missing `LocalBaseline_ct`.

## Incremental Decomposition

Use LocalGap as the quantity to decompose.

Channel references:

- `RefView_c`: historical non-activity reference for exposure
- `RefDiscount_c`: historical non-activity reference for discount

Excess terms:

- `ExcessView_ct = log(view_uv + 1) - RefView_c`
- `ExcessDiscount_ct = discount_rate - RefDiscount_c`
- `ExcessInter_ct = ExcessDiscount_ct * ExcessView_ct`

If the required source field is missing, suppress the corresponding channel instead of inferring it.

## Default Regression

Recommended baseline specification:

`LocalGap_ct = alpha + mu_c + beta1*ExcessDiscount_ct + beta2*ExcessView_ct + beta3*ExcessInter_ct + gamma1*dist2pay_t + gamma2*dist2pay_t^2 + epsilon_ct`

Recommended fixed effects:

- category fixed effects by default
- optional month fixed effects when time coverage is long enough

## Diagnostics

Always report:

- share of activity rows with available LocalBaseline
- baseline quality distribution
- category coverage after estimation filters
- reconciliation between observed LocalGap and explained components

## Fallback Rules

Apply these rules in order:

1. if `view_uv` is missing, run a discount-only LocalGap specification
2. if `discount_rate` is missing, run an exposure-only LocalGap specification
3. if both are missing, compute LocalGap totals only and suppress channel attribution
4. if LocalBaseline is unavailable for too many rows, downgrade LocalGap from main result to limited evidence

## Interpretation

Interpret coefficients as associations with `LocalGap` conditional on the local baseline design, not as automatically clean causal channels.

Special rules:

- interpret the quadratic payday term as a positional curve around the payday anchor
- interpret a negative interaction as diminishing returns or crowding, not automatically as cannibalization
- treat decomposition as the main accounting layer only when coverage and reconciliation are acceptable
