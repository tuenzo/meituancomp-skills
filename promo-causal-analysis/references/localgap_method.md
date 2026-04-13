# LocalGap Method

## Role

Treat LocalGap as the default main analysis object for this skill.

Use it to estimate promotion-period deviations from a local historical non-activity baseline that respects cyclical demand structure better than a global average.

## Entry Criteria

Run LocalGap only after the category-day panel passes the contract in [data_contract.md](data_contract.md).

Minimum entry conditions:

- panel exists
- `gmv` and `is_activity` are available
- historical non-activity observations exist
- at least 2 matched observations are available for each estimated category-day cell

## Default Parameters

Treat these as configurable defaults rather than fixed truths.

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

1. Use non-activity dates only.
2. Match the same weekday first.
3. Search the recent window before falling back to older history.
4. Average the matched observations when the hard minimum is met.

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

Estimate the main LocalGap regression on activity-period samples with non-missing `LocalBaseline_ct`.

## Reference Levels for Channel Decomposition

Construct channel references from historical non-activity observations for the same category.

Recommended defaults:

- `RefView_c`: median of `log(view_uv + 1)` on valid historical non-activity dates
- `RefDiscount_c`: median of `discount_rate` on valid historical non-activity dates

If the required source variable is missing, mark the reference as unavailable and drop the related component from the model and report.

## Excess Terms

When variables exist, define:

- `ExcessView_ct = log(view_uv + 1) - RefView_c`
- `ExcessDiscount_ct = discount_rate - RefDiscount_c`
- `ExcessInter_ct = ExcessDiscount_ct * ExcessView_ct`

Use the centered interaction term above. Do not multiply raw levels and subtract a mixed reference after estimation.

## Default Regression

Use the activity-only estimation sample.

Recommended baseline specification:

`LocalGap_ct = alpha + mu_c + beta1*ExcessDiscount_ct + beta2*ExcessView_ct + beta3*ExcessInter_ct + gamma1*dist2pay_t + gamma2*dist2pay_t^2 + epsilon_ct`

Recommended fixed effects:

- category fixed effects by default
- optional month fixed effects when time coverage is long enough

## Diagnostics

Report at least:

- share of activity rows with available LocalBaseline
- baseline quality distribution: strong, weak, unavailable
- category coverage after estimation filters
- whether coefficient signs and magnitudes are stable under reasonable robustness checks

## Fallback Rules

Apply these fallback rules in order:

1. If `view_uv` is missing, run a discount-only LocalGap specification.
2. If `discount_rate` is missing, run an exposure-only LocalGap specification.
3. If both are missing, compute LocalGap summaries only and avoid channel attribution.
4. If LocalBaseline is unavailable for too many rows, downgrade to descriptive comparison and disclose that LocalGap is not estimable.

## Interpretation

Interpret coefficients as associations with LocalGap conditional on the local baseline design, not as automatically clean causal channels.

Special rules:

- interpret the quadratic payday terms as a positional curve around the payday anchor
- interpret a negative interaction as diminishing returns or crowding between exposure and discount, not automatically as cannibalization
- interpret category decomposition as explanatory allocation only when model coverage and fit are acceptable
