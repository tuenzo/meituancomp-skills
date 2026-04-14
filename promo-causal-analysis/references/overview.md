# Overview

## Problem Framing

Use this skill for retail promotion evaluation when the business question is not only "did sales rise" but "how much of the rise is incremental after accounting for natural cyclical demand."

The key risk is misreading payday, month-end, or weekday-driven demand as promotion increment.

## Unified Method Position

Use the modules in this order of authority:

1. `LocalGap` for main incremental accounting
2. `GPS` for continuous response shape and saturation
3. `uplift` for allocation priority
4. `PSM + DID / event study` for auxiliary causal support
5. `EDA` for business context only

## Why Category-Day

Default to `category x day` because it balances two needs:

- enough granularity to preserve operational variation
- enough stability to support matching, baseline construction, decomposition, and prioritization

## Scope Boundary

Do not use this skill as a pure forecasting workflow.

Do not use it for user-level personalization unless user-level treatment and outcome data are actually available.
