# Uplift Method

## Role

Use uplift to convert heterogeneous response into allocation priority. This is the optimization layer, not the core identification layer.

## Questions It Answers

- which categories or category-period slices deserve more promotional resources
- which slices should be handled selectively
- which slices should likely not be disturbed

## Default Design

- work at `category x day` or an aggregated category slice
- define treatment intensity from a documented business lever
- use time-based validation, never random leakage-prone row splits

## Modeling Guidance

- use uplift to predict differential response under higher versus lower treatment intensity
- aggregate fold-level output to category recommendations
- require fold stability before assigning hard action buckets

## Typical Action Buckets

- `Prioritize`
- `Selective`
- `Observe`
- `Do Not Disturb`

## Interpretation

Treat uplift as ranking logic. If uplift conflicts with GPS or LocalGap, prioritize business safety and the stronger evidentiary layer rather than forcing a single model to dominate.
