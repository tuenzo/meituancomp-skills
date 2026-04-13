# Overview

## Problem Framing

Use this skill for promotion-effect analysis when sales are confounded by recurring demand cycles such as payday, month-end, or fixed weekday structure.

In this setting, raw activity-period lift is not a reliable effect estimate because the promotion window can overlap with naturally stronger demand days.

## Why LocalGap First

Default to a LocalGap-first workflow because it compares each activity-period observation against a local historical non-activity reference rather than against a global average.

This makes the baseline more sensitive to recurring calendar structure and usually easier to explain to business users.

## Role of DID and Event-Study

Use DID or event-study as supporting diagnostics when the user wants a treatment-control view.

In this skill, DID is not the default final answer because:

- treatment intensity is often constructed from realized exposure or discount lift
- activity timing may overlap with cyclical demand shocks
- treatment assignment is rarely cleanly exogenous

Treat the DID section as a directional or robustness layer unless stronger identification is explicitly justified.

## Analysis Objects

Prioritize these objects in order:

1. `LocalGap`
2. exposure or discount channel decomposition when variables exist
3. DID or event-study diagnostics when requested
4. descriptive before-after comparisons as context only

## Scope Boundary

Do not use this skill as a generic forecasting workflow.

Do not use it when:

- the problem is pure demand prediction
- no reliable activity flag exists
- the user explicitly asks for a different causal framework and does not want LocalGap
