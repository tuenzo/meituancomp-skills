# Workflow

## Default Order

Run the workflow in this order unless the user explicitly narrows scope:

1. Build category-day panel
2. Business-oriented EDA
3. PSM + DID / event study
4. Local baseline and incremental decomposition
5. GPS continuous treatment response
6. Uplift prioritization
7. Report synthesis and recommendation writing

## Step 1: Build category-day panel

Objective:

- establish the common analysis table used by every downstream module

Entry criteria:

- raw source tables or an existing panel are available

Exit criteria:

- panel exists
- required fields are validated
- downgrade log is started

Skip logic:

- skip construction only when the supplied panel already satisfies the contract

## Step 2: Business-oriented EDA

Objective:

- show what changed during activity periods before invoking causal language

Entry criteria:

- panel exists
- both activity and non-activity rows exist

Exit criteria:

- descriptive table is produced
- cyclical and category-level pattern summary is produced

Skip logic:

- do not skip in a full run unless the user explicitly suppresses EDA

## Step 3: PSM + DID / event study

Objective:

- test whether higher-intensity or treated slices move differently than comparable controls

Entry criteria:

- treatment intensity can be defined
- matching covariates or a documented downgrade path exist
- pre-period coverage is sufficient

Exit criteria:

- matching diagnostics are produced
- DID and pretrend or event-study summary is produced
- placebo or sensitivity notes are produced when feasible

Skip logic:

- skip if treatment construction is not defensible
- skip if pre-period coverage is too weak

## Step 4: Local baseline and incremental decomposition

Objective:

- produce the main incremental estimate relative to a local natural benchmark

Entry criteria:

- panel exists
- LocalBaseline is estimable for at least part of the activity sample

Exit criteria:

- LocalGap summary is produced
- baseline quality flags are reported
- total, monthly, and category-level decomposition is produced when inputs allow it

Skip logic:

- downgrade or skip when non-activity history is too thin

## Step 5: GPS continuous treatment response

Objective:

- estimate dose-response shape for continuous treatment intensity

Entry criteria:

- continuous treatment variable exists
- overlap is sufficient to estimate support

Exit criteria:

- GPS diagnostics are produced
- dose-response curve is produced
- saturation or diminishing-return notes are recorded

Skip logic:

- skip when support is too weak or treatment is effectively binary only

## Step 6: Uplift prioritization

Objective:

- translate heterogeneous response into a resource-allocation ranking

Entry criteria:

- outcome variable exists
- treatment variable exists
- time-safe fold design is possible

Exit criteria:

- uplift scores are produced
- action buckets are assigned
- stability notes are recorded

Skip logic:

- skip when the sample is too thin for stable folds
- skip when only user-level personalization is requested without user-level data

## Step 7: Report synthesis and recommendation writing

Objective:

- convert analytical outputs into business-ready recommendations

Entry criteria:

- at least one analysis module has produced usable output

Exit criteria:

- narrative integrates EDA, causal support, increment accounting, dose-response, and prioritization
- downgrade reasons remain visible

## Quality Checks

Run these checks across the workflow:

- report missingness and zero shares before interpretation
- report unavailable sections explicitly rather than silently omitting them
- attach downgrade reasons to the final narrative
- prioritize LocalGap over DID when the modules disagree
