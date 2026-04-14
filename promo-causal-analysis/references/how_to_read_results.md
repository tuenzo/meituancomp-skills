# How to Read Results Together

## Evidence Hierarchy

Use this hierarchy when synthesizing conclusions:

1. `LocalGap` for main increment
2. `GPS` for scaling logic
3. `uplift` for prioritization
4. `PSM + DID / event study` for directional support
5. `EDA` for context

## Conflict Rules

### DID positive but placebo also strong

- downgrade DID immediately
- keep LocalGap as the main increment statement
- use GPS only if overlap remains acceptable

### LocalGap large but GPS flattens

- conclude that current increment exists
- avoid recommending aggressive intensity scaling
- shift optimization focus toward targeting or execution quality

### GPS favorable but uplift says `Do Not Disturb`

- interpret the average response as positive but heterogeneous
- keep the slice out of the top-priority bucket
- require additional evidence before scaling

### Uplift unstable across folds

- collapse action buckets to a more conservative scheme
- keep recommendations exploratory
- avoid automation or hard-coded policy change
