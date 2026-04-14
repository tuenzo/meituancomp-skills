# PSM + DID / Event Study

## Role

Use this module for directional causal support when the user wants more than descriptive comparison but the main incremental statement should still come from LocalGap.

Treat this module as auxiliary evidence. Even after matching, it does not replace the LocalGap accounting layer.

## Questions It Answers

- does a higher-intensity group move differently than a comparable lower-intensity group
- are the directional findings consistent with the business story
- do pretrend and placebo diagnostics materially weaken the claim

## Default Parameters

| Parameter | Default | Notes |
| --- | --- | --- |
| `treatment_quantile` | `0.75` | Top quartile defines the higher-intensity group |
| `clean_control_quantile` | `0.25` | Bottom quartile defines the cleaner control |
| `grouping_window` | `activity_period_mean` | Build treatment intensity from activity-window means |
| `event_window_pre` | `14` | Default lookback for event-study diagnostics |
| `event_window_post` | `14` | Default look-forward for event-study diagnostics |
| `matching_method` | `psm_nearest_neighbor` | One-to-one nearest propensity-score matching by default |
| `matching_caliper` | `0.1` | Apply when propensity support is thin |

## Treatment Construction

Default treatment variables:

- exposure lift
- discount lift
- documented combined intensity score when both exposure and discount are present

Define lift relative to a historical non-activity reference for the same category. Prefer local historical reference over cross-sectional rank alone.

Default comparisons:

- `top 25% vs rest 75%`
- `top 25% vs bottom 25%`

## Matching Logic

Use pre-treatment or non-activity covariates for matching, such as:

- baseline GMV
- baseline exposure
- baseline discount
- category size proxies
- pre-period trend summaries

Do not match on post-treatment outcomes.

If the covariate set is too thin for credible matching, disclose the downgrade and treat the resulting DID as weaker evidence.

## Estimation

Recommended sequence:

1. define treatment and control groups
2. estimate propensity scores
3. match treated and control categories or slices
4. run DID on the matched sample
5. run event-study or pretrend checks
6. run placebo timing or sensitivity checks when feasible

## Diagnostics

Always report:

- treatment definition
- matching variables
- matched sample size
- balance diagnostics or a clear balance limitation
- DID coefficient
- pretrend or event-study result
- placebo result when available

## Interpretation

Use these rules:

- significant DID with acceptable balance and stable pretrend can support directional consistency
- weak balance, failing pretrend, or strong placebo blocks strong language
- disagreement between exposure-based and discount-based DID should be discussed, not averaged away

## Guardrail

If treatment is built from realized activity-period intensity, describe the design as matched intensity-group comparison rather than a clean exogenous treatment assignment.
