# Interpretation Rules

## Core Guardrails

Apply these guardrails to every narrative output:

1. Do not equate raw activity-period GMV lift with causal promotion effect.
2. Treat `LocalGap` as the main effect object in this skill.
3. Treat DID and event-study as directional validation unless the user explicitly requests a different identification strategy and the assumptions are defended.
4. Interpret quadratic payday terms as a position curve, not as a clean additive payday amount.
5. Treat decomposition that materially over-explains the observed LocalGap as exploratory only.

## Language Rules

Use cautious wording that matches the evidence quality.

Preferred wording:

- "associated with"
- "consistent with"
- "directionally supports"
- "suggests incremental lift relative to the local baseline"
- "should be interpreted with caution"

Avoid stronger wording unless the underlying conditions are met.

Avoid by default:

- "proves"
- "caused"
- "the promotion created"
- "clean causal estimate"

## When Incremental Language Is Allowed

Use "incremental" only when all conditions below hold:

- a valid LocalBaseline is available for the reported slice
- the sample quality is disclosed
- the result is framed relative to the local baseline, not as a raw before-after difference

If any condition fails, fall back to "difference" or "association".

## DID-Specific Guardrails

If treatment is constructed from realized exposure or discount intensity, describe the design as an intensity-group comparison.

If pretrend checks fail or are unstable:

- do not use strong causal wording
- state that the DID evidence is not fully supportive
- keep DID as a robustness or directional section only

## Decomposition Guardrails

When reporting exposure, discount, and residual components:

- make clear whether components sum closely to the observed LocalGap
- call out large residuals directly
- label component shares as attribution-style summaries, not mechanical truth

If channel inputs are missing or weak, suppress the unavailable components instead of inferring them.

## Required Caveats

Add at least one explicit caveat when any of the following holds:

- weak LocalBaseline coverage
- sparse category slices
- missing exposure or discount fields
- unstable pretrend checks
- short activity windows

## Reporting Template

Prefer this pattern:

1. State the observable pattern.
2. State the modeling object used to adjust for cyclical demand.
3. State what the result supports and what it does not support.
4. State the main caveat.
