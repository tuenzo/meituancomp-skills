---
name: promo-causal-analysis
description: Evaluate and optimize retail promotions under cyclical demand. Use when Codex needs to build a category-day panel from orders, exposure, and activity tables; run business-oriented EDA; use PSM plus DID or event study for directional causal evidence; use LocalGap as the main incremental accounting layer; estimate continuous dose response with GPS; prioritize categories with uplift modeling; and produce business-ready recommendations without overstating causal claims.
---

# Retail Promotion Causal Evaluation and Optimization

## Overview

Use this skill for retail promotion analysis when activity timing overlaps with payday, month-end, weekday, or other recurring demand cycles. The main challenge is separating natural cyclical fluctuation from true promotion increment.

Default to `category x day` as the working grain. Treat `LocalGap` as the main incremental accounting layer. Treat `PSM + DID / event study` as auxiliary causal support, `GPS` as the continuous dose-response layer, and `uplift` as the prioritization layer.

## When to Use

Use this skill when:

- the problem is promotion effectiveness or promotion optimization
- the data can be represented at `category x day`
- activity timing is confounded by cyclical demand
- the output needs both increment accounting and business recommendations

Do not use this skill when:

- there is no reliable activity flag and no defensible way to reconstruct it
- there is no daily sales measure
- the user explicitly wants another identification strategy as the primary method
- the task is user-level personalization without user-level treatment and outcome data

## Input Contract

Accept either:

- raw `orders`, `exposure`, and `activity_calendar` tables
- an existing `category-day panel`

Minimum required fields:

- `date`
- category identifier
- sales measure such as `gmv`
- reliable `is_activity`

Read [references/data_contract.md](references/data_contract.md) for:

- required and optional fields
- default grain rules
- missing and zero handling
- `SKU x day` exposure roll-up
- module-level downgrade rules

## Unified Method Position

Use the workflow with this evidence hierarchy:

1. `LocalGap` for main increment
2. `GPS` for dose-response and saturation
3. `uplift` for allocation priority
4. `PSM + DID / event study` for directional support
5. `EDA` for business context only

Do not treat DID as the final increment estimate. Do not treat uplift as stand-alone causal proof.

## Workflow

### Step 1: Build category-day panel

- objective: create the common analysis table
- output: validated panel plus downgrade log

### Step 2: Business-oriented EDA

- objective: show raw activity vs non-activity patterns before causal interpretation
- output: descriptive tables and cyclical pattern summary

### Step 3: PSM + DID / event study

- objective: generate directional causal support on a cleaner comparison design
- output: matching diagnostics, DID summary, pretrend or placebo checks

### Step 4: Local baseline and incremental decomposition

- objective: produce the main increment estimate relative to a local natural baseline
- output: LocalGap summary plus overall, monthly, and category-level decomposition

### Step 5: GPS continuous treatment response

- objective: estimate continuous response shape and diminishing returns
- output: GPS diagnostics plus dose-response curve

### Step 6: Uplift prioritization

- objective: convert heterogeneous response into allocation priorities
- output: uplift scores, action buckets, and recommendation inputs

Read [references/workflow.md](references/workflow.md) for entry criteria, skip logic, and quality checks.

## Reference Map

Load only the references needed for the current task:

- [references/overview.md](references/overview.md): business framing and evidence hierarchy
- [references/data_contract.md](references/data_contract.md): input contract and downgrade rules
- [references/workflow.md](references/workflow.md): step-by-step execution logic
- [references/did_event_study.md](references/did_event_study.md): PSM + DID / event-study design
- [references/localgap_method.md](references/localgap_method.md): LocalBaseline, LocalGap, decomposition
- [references/gps_method.md](references/gps_method.md): continuous treatment response
- [references/uplift_method.md](references/uplift_method.md): prioritization logic
- [references/how_to_read_results.md](references/how_to_read_results.md): conflict resolution across modules
- [references/recommendation_template.md](references/recommendation_template.md): business recommendation structure
- [references/report_template.md](references/report_template.md): report-ready writing pattern
- [references/interpretation_rules.md](references/interpretation_rules.md): causal language guardrails
- [references/troubleshooting.md](references/troubleshooting.md): failure modes and downgrade handling

## Script Map

Use these scripts when execution is requested:

- [scripts/build_category_day_panel.py](scripts/build_category_day_panel.py)
- [scripts/run_descriptive_stats.py](scripts/run_descriptive_stats.py)
- [scripts/run_psm_did_event_study.py](scripts/run_psm_did_event_study.py)
- [scripts/run_localgap_model.py](scripts/run_localgap_model.py)
- [scripts/run_category_decomposition.py](scripts/run_category_decomposition.py)
- [scripts/run_gps_response.py](scripts/run_gps_response.py)
- [scripts/run_uplift_prioritization.py](scripts/run_uplift_prioritization.py)
- [scripts/generate_report_tables.py](scripts/generate_report_tables.py)

Use [scripts/utils.py](scripts/utils.py) for shared helpers.

## Guardrails

- do not treat EDA as causal evidence
- do not treat DID or event study as the final increment layer
- do not ignore missingness, zero inflation, or weak overlap
- do not extrapolate unsupported GPS tails
- do not use leakage-prone random splits for uplift
- do not force user-level uplift from aggregate data

## Deliverables

For a full run, produce:

- panel quality summary
- EDA summary
- PSM + DID / event-study diagnostics
- LocalGap main increment summary
- decomposition outputs
- GPS dose-response summary
- uplift prioritization output
- business-ready recommendation section with caveats
