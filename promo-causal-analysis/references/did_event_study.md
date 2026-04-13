# DID and Event-Study

## Role

Use this reference when the user requests a treatment-control style diagnostic in addition to, or instead of, the LocalGap section.

Treat DID and event-study as supporting evidence unless a stronger identification claim is explicitly justified.

## Default Parameters

Use these configurable defaults:

| Parameter | Default | Notes |
| --- | --- | --- |
| `treatment_quantile` | `0.75` | Top quartile defines the high-intensity group |
| `clean_control_quantile` | `0.25` | Bottom quartile for cleaner robustness comparison |
| `grouping_window` | `activity_period_mean` | Build treatment groups from mean intensity over the activity window |
| `event_window_pre` | `14` | Default lookback for event-study graphics |
| `event_window_post` | `14` | Default look-forward for event-study graphics |
| `min_pre_periods` | `3` | Minimum count for pretrend inspection |

## Treatment Construction

Support two intensity types:

- exposure lift
- discount lift

Define lift relative to a documented historical non-activity reference for the same category. Prefer historical local reference over cross-sectional rank only.

Default grouping:

- top 25% versus rest 75%
- top 25% versus bottom 25% as the cleaner robustness version

Do not switch between grouping definitions without stating it clearly.

## Modeling Notes

When treatment is defined from realized activity-period intensity, the design is closer to a high-intensity versus low-intensity comparison than to a clean exogenous treatment assignment.

State that limitation directly in any summary.

## Diagnostics

Always report:

- treatment definition
- reference period used to construct lift
- pretrend plot or equivalent coefficient summary
- whether pretrend evidence is supportive, mixed, or weak

If pretrend fails, keep the section but weaken the claim.

## Interpretation

Use these rules:

- supportive pretrends plus stable coefficients can support directional consistency
- failing pretrends block strong causal wording
- disagreement between exposure and discount DID should be discussed, not averaged away

## Exit Conditions

A usable DID section requires:

- documented treatment construction
- estimable model or event-study coefficients
- a written caveat on endogeneity risk when relevant
