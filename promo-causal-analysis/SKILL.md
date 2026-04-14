---
name: promo-causal-analysis
description: Evaluate and optimize retail promotions under cyclical demand. Use when Codex needs to build a category-day panel from orders, exposure, and activity tables; run business-oriented EDA; use PSM plus DID or event study for directional causal evidence; use LocalGap as the main incremental accounting layer; estimate continuous dose response with GPS; prioritize categories with uplift modeling; and produce business-ready recommendations without overstating causal claims.
---

# Retail Promotion Causal Evaluation and Optimization

## Overview

Use this skill for retail promotion questions where sales move with payday, month-end, weekday, or other recurring demand cycles. The core problem is not whether activity-period sales changed, but whether the observed change exceeds what would have happened naturally under the same cyclical position.

Default to `category x day` as the analysis unit because it is detailed enough to preserve operational variation while still stable enough for panel construction, causal diagnostics, and strategy output. Treat `LocalGap` as the main incremental accounting layer. Treat `PSM + DID / event study` as auxiliary causal evidence, `GPS` as the continuous dose-response layer, and `uplift` as the resource-allocation layer.

## When to Use

Use this skill when:

- the business problem is promotion effectiveness or promotion optimization rather than pure forecasting
- activity timing overlaps with payday, month-end, weekday, or other cyclical demand patterns
- the available data can be aggregated to `category x day`
- the user wants both incremental accounting and action-oriented optimization output
- the output must support business reporting with cautious causal language

Do not use this skill when:

- there is no reliable activity flag and no defensible way to reconstruct it
- no daily sales measure exists
- the user explicitly wants a different identification strategy as the primary method
- the task is user-level personalization and the available data is only category-day or store-day

## Input Contract

Expected inputs:

- `orders`
- `exposure`
- `activity_calendar`
- or an existing `category-day panel`

Required fields:

- `date`
- category key such as `category_name_cn` or `category_id`
- sales measure such as `gmv` or `sku_sale_amt`
- reliable `is_activity` flag, either directly present or derivable from `activity_calendar`

Optional but valuable fields:

- `view_uv`
- `buy_uv`
- `discount_rate`
- `order_cnt`
- `sale_num`
- activity name, type, or campaign identifier

Default grain:

- output analysis grain is `category x day`
- raw `orders` and `exposure` may be more granular and must be aggregated upward before modeling

Missing and zero handling:

- treat missing structural fields as blocking issues, not as zeros
- keep legitimate zero-sales or zero-exposure days because they carry signal for baseline and zero-inflation checks
- report missingness and zero shares before interpretation

Exposure at `SKU x day` only:

- default to aggregating `SKU x day` exposure to `category x day` using an explicit SKU-to-category mapping from the order or product dimension
- if no mapping exists, disclose that exposure-based modules are unavailable and downgrade accordingly

Read [references/data_contract.md](references/data_contract.md) before execution.

## Core Assumptions and Causal Logic

Promotion periods often coincide with natural demand peaks. Natural cyclical demand, exposure amplification, and deeper discounting can all move at the same time. If those layers are not separated, raw activity lift will systematically overstate promotion increment.

Use each module to answer a different question:

- `EDA`: what visibly changes between activity and non-activity periods
- `PSM + DID / event study`: does a higher-treatment group move differently from a matched lower-treatment group in a direction consistent with promotion effectiveness
- `LocalGap`: what incremental gap remains after comparing each activity observation against a local natural baseline
- `GPS`: how does response change as treatment intensity increases continuously
- `uplift`: where should incremental resources be concentrated or withheld

Unified method position:

- `LocalGap` is the main incremental accounting method
- `PSM + DID / event study` is auxiliary causal support, not the final increment estimate
- `GPS` identifies continuous dose-response shape and saturation risk
- `uplift` ranks allocation priority; it does not replace causal identification by itself

Do not treat DID as the final increment because treatment intensity is often endogenous and parallel trends are fragile in cyclical retail settings. Use DID to test direction and robustness. Use LocalGap to anchor the main incremental statement because it conditions on a local natural benchmark rather than a global average.

## Workflow

### Step 1: Build category-day panel

Objective:

- create a validated `category x day` panel that can support all downstream modules

Key actions:

- standardize column names and date formats
- aggregate `orders` and `exposure` to `category x day`
- merge `activity_calendar`
- add `weekday`, `month`, `day_of_month`, `dist2pay`, and `is_month_end`
- record missingness, zero shares, duplicate keys, and downgrade decisions

Recommended modeling choices:

- use `category x day` as the default analysis grain
- preserve zero-sales and zero-exposure rows when they are real observations
- mark unavailable fields rather than fabricating them

Output:

- validated category-day panel
- panel metadata and downgrade log

References and scripts:

- [references/data_contract.md](references/data_contract.md)
- [references/workflow.md](references/workflow.md)
- [scripts/build_category_day_panel.py](scripts/build_category_day_panel.py)

### Step 2: Business-oriented EDA

Objective:

- establish business context before causal language

Key actions:

- compare activity vs non-activity means, medians, zero shares, and distributions
- break out weekday, payday-position, month-end, and category patterns
- review exposure, discount, conversion, and GMV together

Recommended modeling choices:

- report statistical tests only as descriptive support
- inspect both overall and category-level summaries
- call out zero inflation, heavy tails, and sparsity before modeling

Output:

- descriptive summary tables
- cyclical pattern summary
- business interpretation of raw contrasts

References and scripts:

- [references/workflow.md](references/workflow.md)
- [references/report_template.md](references/report_template.md)
- [scripts/run_descriptive_stats.py](scripts/run_descriptive_stats.py)

### Step 3: PSM + DID / event study

Objective:

- generate directional causal support under a cleaner comparison design than raw EDA

Key actions:

- construct treatment intensity from exposure lift, discount lift, or a documented activity-intensity measure
- use propensity-score matching to improve treated-control comparability
- estimate DID and event-study style diagnostics on the matched sample
- run placebo and pretrend checks when feasible

Recommended modeling choices:

- match on pre-period category characteristics rather than post-treatment outcomes
- compare `top 25% vs rest 75%` and `top 25% vs bottom 25%`
- treat the output as directional evidence even when coefficients are significant

Output:

- matching diagnostics
- DID coefficient table
- event-study or pretrend diagnostic summary
- placebo or sensitivity notes

References and scripts:

- [references/did_event_study.md](references/did_event_study.md)
- [references/interpretation_rules.md](references/interpretation_rules.md)
- [scripts/run_psm_did_event_study.py](scripts/run_psm_did_event_study.py)

### Step 4: Local baseline and incremental decomposition

Objective:

- estimate increment relative to a local natural baseline and decompose the main drivers

Key actions:

- build `LocalBaseline` from historical non-activity dates
- compute `LocalGap`
- estimate excess exposure, excess discount, and interaction terms
- summarize total, monthly, and category-level decomposition

Recommended modeling choices:

- use historical non-activity observations only
- match same weekday first and prefer recent windows before older fallback windows
- mark baseline quality as `strong`, `weak`, or `unavailable`

Output:

- LocalBaseline coverage report
- LocalGap summary
- incremental decomposition at overall, monthly, and category levels

References and scripts:

- [references/localgap_method.md](references/localgap_method.md)
- [references/interpretation_rules.md](references/interpretation_rules.md)
- [scripts/run_localgap_model.py](scripts/run_localgap_model.py)
- [scripts/run_category_decomposition.py](scripts/run_category_decomposition.py)

### Step 5: GPS continuous treatment response

Objective:

- estimate how outcome changes as treatment intensity increases continuously

Key actions:

- define a continuous treatment such as `discount_rate`, `view_uv`, or a combined intensity score
- estimate the generalized propensity score
- fit a response surface and derive a dose-response curve
- check for saturation, diminishing returns, or unstable support

Recommended modeling choices:

- restrict interpretation to regions with overlap and support
- compare continuous response shape with LocalGap decomposition
- treat steep tails or sparse support as weak evidence

Output:

- GPS diagnostics
- dose-response curve
- saturation and diminishing-return interpretation

References and scripts:

- [references/gps_method.md](references/gps_method.md)
- [references/interpretation_rules.md](references/interpretation_rules.md)
- [scripts/run_gps_response.py](scripts/run_gps_response.py)

### Step 6: Uplift prioritization

Objective:

- turn heterogeneous response estimates into allocation priorities

Key actions:

- build time-safe uplift features at `category x day` or aggregated category slices
- score expected incremental response under higher vs lower intervention intensity
- rank categories or category-period slices into action buckets
- convert model output into a prioritization list for business action

Recommended modeling choices:

- use time-based folds rather than random row splits
- stay above user-level unless user-level treatment assignment and outcomes are genuinely available
- use uplift to rank allocation, not to claim identification by itself

Output:

- uplift scores
- priority buckets such as `Prioritize`, `Selective`, `Observe`, `Do Not Disturb`
- resource-allocation suggestions

References and scripts:

- [references/uplift_method.md](references/uplift_method.md)
- [references/recommendation_template.md](references/recommendation_template.md)
- [scripts/run_uplift_prioritization.py](scripts/run_uplift_prioritization.py)

## How to Read Results Together

Interpret the modules in layers:

1. `EDA` provides context only.
2. `PSM + DID / event study` provides directional causal support.
3. `LocalGap` provides the main incremental accounting statement.
4. `GPS` refines the continuous response shape and scaling logic.
5. `uplift` turns heterogeneous response into prioritization decisions.

Conflict handling:

- if DID is positive but placebo is also strong, downgrade DID to weak directional evidence and rely more on LocalGap plus GPS
- if LocalGap is large but the GPS curve flattens quickly, conclude that increment exists but marginal scaling room may be limited
- if GPS looks favorable but uplift falls into `Do Not Disturb`, conclude that the average dose-response is positive while the target slice is not a high-priority allocation target under current heterogeneity
- if uplift is unstable across folds, keep the ranking exploratory and avoid operational hard-coding

Read [references/how_to_read_results.md](references/how_to_read_results.md) when writing the final synthesis.

## Recommendation Template

### Overall strategy

- summarize whether promotions appear to generate incremental value after cyclical adjustment
- state whether the main lever is exposure, discount, or mixed execution
- state whether scaling should be broad, selective, or conservative

### Full-category strategy

- identify categories where LocalGap is positive and GPS still shows room to increase treatment
- recommend broader allocation only when uplift ranks are stable and not in `Observe` or `Do Not Disturb`

### Head-category strategy

- separate head categories into `scale`, `optimize`, `hold`, or `avoid disturbance`
- use uplift ranking to choose priority
- use GPS to determine whether more intensity is justified
- use LocalGap to quantify the current incremental contribution

Read [references/recommendation_template.md](references/recommendation_template.md) before drafting business recommendations.

## Guardrails

- do not treat EDA as causal evidence
- do not treat DID or event study as the final increment estimate
- do not ignore zero inflation, sparsity, or missing-field patterns
- do not estimate GPS in unsupported treatment regions and then over-interpret the tails
- do not use random splits with time leakage for uplift validation
- do not force user-level uplift when the data is only category-day or store-day
- do not over-interpret uplift quadrants when fold stability is weak
- do not claim exposure or discount attribution when the required inputs are missing

## Deliverable Checklist

- category-day panel summary with data-quality notes
- business-oriented EDA summary
- PSM + DID / event-study diagnostics with caveats
- LocalGap main increment summary
- overall, monthly, and category-level decomposition
- GPS dose-response summary
- uplift prioritization table
- business recommendation section covering overall, full-category, and head-category actions
- explicit caveats on data coverage, overlap, baseline quality, and causal scope

## Merge Notes

- retained from the earlier framework: the LocalGap-first stance, cyclical-demand caution, payday and weekday controls, and category-level interpretation logic
- retained from the execution-oriented draft: the stepwise workflow, input contract discipline, output checklist, and report-oriented delivery structure
- merged repeated DID statements into one stronger rule: DID or event study is auxiliary causal evidence, not the final increment layer
- elevated new scope from the current merge request: PSM, GPS, uplift, and recommendation logic are now first-class workflow modules
- kept the skill reusable by separating detailed execution rules into references and scripts while making the main `SKILL.md` explicit enough to route the full workflow
