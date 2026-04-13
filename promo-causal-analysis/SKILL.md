---
name: promo-causal-analysis
description: Analyze promotion effectiveness under cyclical retail demand with a LocalGap-first workflow. Use when Codex needs to work from raw orders, exposure, activity calendars, or an existing category-day panel to produce descriptive comparisons, optional DID or event-study diagnostics, LocalGap estimation, decomposition, and report-ready conclusions while guarding against overstating causal effects from payday or month-end cycles.
---

# Promo Causal Analysis

## Overview

Use this skill as the standard entry point for promotion analysis when activity windows overlap with payday, month-end, or other cyclical demand patterns.

Default to a LocalGap-first workflow. Use DID or event-study only as supporting diagnostics unless the user explicitly requests another causal design.

## Operating Modes

Support these modes:

- `full`
- `descriptive_only`
- `did_only`
- `localgap_only`
- `report_only`

Infer the mode from the user request when possible. Default to `full` when the request does not narrow scope.

## Required Inputs

Accept either:

- raw `orders`, `exposure`, and `activity_calendar` tables
- an existing category-day panel

Read [references/data_contract.md](references/data_contract.md) before modeling. Do not guess missing contracts.

## Outputs

Produce only the outputs that fit the selected mode. Typical deliverables are:

- panel quality summary
- descriptive statistics table
- DID or event-study diagnostics when requested and feasible
- LocalGap model summary
- overall, monthly, and category-level decomposition
- report-ready narrative with explicit caveats

## Default Workflow

Run the workflow in this order unless the mode narrows scope:

1. Build or validate the category-day panel.
2. Run descriptive statistics.
3. Run DID or event-study if requested and data quality supports it.
4. Run LocalGap as the main analysis.
5. Run category-level decomposition.
6. Generate decision-oriented narrative and tables.

Read [references/workflow.md](references/workflow.md) for entry criteria, exit criteria, and skip logic.

## Reference Map

Load only the references needed for the current task:

- [references/overview.md](references/overview.md): business framing and LocalGap-first rationale
- [references/data_contract.md](references/data_contract.md): input and output contract, required fields, fallback rules
- [references/workflow.md](references/workflow.md): end-to-end execution order and quality checks
- [references/localgap_method.md](references/localgap_method.md): LocalBaseline, LocalGap, regression design, parameters
- [references/did_event_study.md](references/did_event_study.md): treatment construction and interpretation limits
- [references/interpretation_rules.md](references/interpretation_rules.md): causal language guardrails
- [references/report_template.md](references/report_template.md): report structure and wording templates
- [references/troubleshooting.md](references/troubleshooting.md): failure modes and downgrade paths

## Script Map

Call scripts in this order when execution is requested:

- [scripts/build_category_day_panel.py](scripts/build_category_day_panel.py)
- [scripts/run_descriptive_stats.py](scripts/run_descriptive_stats.py)
- [scripts/run_did_event_study.py](scripts/run_did_event_study.py)
- [scripts/run_localgap_model.py](scripts/run_localgap_model.py)
- [scripts/run_category_decomposition.py](scripts/run_category_decomposition.py)
- [scripts/generate_report_tables.py](scripts/generate_report_tables.py)

Use [scripts/utils.py](scripts/utils.py) for shared helpers rather than re-implementing transformations in each script.

## Execution Rules

Follow these rules every time:

- Treat `LocalGap` as the main effect object in this skill.
- Treat DID or event-study as directional support, not as the default final effect estimate.
- Disclose downgrade decisions when required inputs or sample quality are insufficient.
- Use cautious language when cycles, endogenous treatment intensity, or weak baselines limit causal interpretation.
- Prefer parameterized defaults over hard-coded assumptions when scripts expose configurable options.
