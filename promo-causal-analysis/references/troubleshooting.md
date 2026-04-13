# Troubleshooting

## Historical Non-Activity Coverage Is Too Thin

Symptoms:

- many activity rows have no LocalBaseline
- most categories are flagged `weak` or `unavailable`

Response:

- extend the fallback history window if defensible
- aggregate to a coarser category level if sparsity is the root cause
- downgrade to descriptive analysis when LocalGap remains unavailable

## Activity Window Is Too Short

Symptoms:

- too few activity dates for stable coefficient estimates
- decomposition is unstable across minor specification changes

Response:

- report totals and descriptive contrasts only
- treat model outputs as illustrative if shown at all

## Treatment Groups Are Unbalanced

Symptoms:

- top quartile contains very few categories
- treatment definitions change drastically across windows

Response:

- report the instability
- compare top 25% versus bottom 25% as a cleaner sensitivity check
- avoid strong DID conclusions

## Pretrend Fails

Symptoms:

- event-study lead coefficients are unstable or large
- joint pretrend tests reject parallel trends

Response:

- weaken causal language immediately
- keep DID as supporting context only
- rely on LocalGap if its contract is stronger

## Exposure or Discount Data Is Missing

Symptoms:

- `view_uv` or `discount_rate` is unavailable or mostly missing

Response:

- drop the unavailable component
- suppress unsupported channel attribution
- state the narrower scope in the final report

## Category Granularity Is Too Sparse

Symptoms:

- many category-day cells are zero or missing
- baseline matching frequently fails

Response:

- aggregate categories
- report which slices were excluded
- avoid over-interpreting sparse categories

## Decomposition Does Not Reconcile

Symptoms:

- component totals materially exceed or fall short of observed LocalGap

Response:

- report the mismatch plainly
- label the decomposition exploratory
- avoid precise percentage-share claims
