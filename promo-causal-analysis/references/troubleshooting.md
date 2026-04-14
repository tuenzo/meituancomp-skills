# Troubleshooting

## Historical Non-Activity Coverage Is Too Thin

Symptoms:

- many activity rows have no LocalBaseline
- most categories are flagged `weak` or `unavailable`

Response:

- extend the fallback history window if defensible
- aggregate to a coarser category level if sparsity is the root cause
- downgrade LocalGap from main accounting to limited evidence if coverage remains weak

## Activity Window Is Too Short

Symptoms:

- too few activity dates for stable coefficient estimates
- decomposition or uplift ranks change sharply under small perturbations

Response:

- report totals and descriptive contrasts only
- keep model outputs illustrative if shown at all

## Matching Balance Is Weak

Symptoms:

- treated and control groups still differ substantially after matching
- matched sample size collapses after caliper filtering

Response:

- weaken causal language
- report DID as auxiliary only
- rely more heavily on LocalGap and GPS

## Pretrend Fails

Symptoms:

- event-study lead coefficients are unstable or large
- placebo timing also looks strong

Response:

- downgrade DID to weak directional evidence
- do not let DID overturn a stronger LocalGap reading

## Exposure Only Exists at SKU-Day Without Mapping

Symptoms:

- `view_uv` exists but category mapping cannot be recovered

Response:

- skip exposure-based modules
- state that the exposure signal is unavailable at the required grain

## GPS Support Is Weak

Symptoms:

- treatment distribution is highly concentrated
- curve tails are driven by very few observations

Response:

- trim unsupported tails
- interpret only the supported region
- skip GPS if support remains too weak

## Uplift Folds Are Unstable

Symptoms:

- action buckets flip across time folds
- high scores appear only in one fold

Response:

- keep uplift exploratory
- use broader action buckets
- avoid hard operational commitment

## Category Granularity Is Too Sparse

Symptoms:

- many category-day cells are zero or missing
- baseline matching frequently fails

Response:

- aggregate categories
- report excluded slices explicitly
- avoid over-interpreting sparse categories
