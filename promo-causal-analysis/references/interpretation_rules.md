# Interpretation Rules

## Core Guardrails

Apply these guardrails to every narrative output:

1. Do not equate raw activity-period GMV lift with causal promotion effect.
2. Treat `LocalGap` as the main effect object in this skill.
3. Treat `PSM + DID / event study` as directional validation unless the user explicitly requests a different identification strategy and the assumptions are defended.
4. Interpret quadratic payday terms as a position curve, not as a clean additive payday amount.
5. Treat decomposition that materially over-explains the observed LocalGap as exploratory only.
6. Treat `GPS` as a dose-response layer and not as a license to extrapolate unsupported treatment regions.
7. Treat `uplift` as a prioritization layer and not as stand-alone causal proof.

## Language Rules

Use cautious wording that matches the evidence quality.

Preferred wording:

- "associated with"
- "consistent with"
- "directionally supports"
- "suggests incremental lift relative to the local baseline"
- "should be interpreted with caution"

Avoid by default:

- "proves"
- "caused"
- "the promotion created"
- "clean causal estimate"

## When Incremental Language Is Allowed

Use "incremental" only when all conditions below hold:

- a valid LocalBaseline is available for the reported slice
- sample quality is disclosed
- the result is framed relative to the local baseline rather than as raw before-after lift

If any condition fails, fall back to "difference" or "association".

## PSM + DID-Specific Guardrails

If treatment is constructed from realized exposure or discount intensity, describe the design as an intensity-group comparison.

If pretrend checks fail or matching balance is weak:

- do not use strong causal wording
- state that the DID evidence is not fully supportive
- keep the module as robustness or directional context only

## Decomposition Guardrails

When reporting exposure, discount, and residual components:

- make clear whether components reconcile closely to observed LocalGap
- call out large residuals directly
- label component shares as attribution-style summaries, not mechanical truth

If channel inputs are missing or weak, suppress unavailable components instead of inferring them.

## GPS and Uplift Guardrails

When reporting GPS:

- state the treatment variable clearly
- limit interpretation to supported overlap regions
- call out flat or unstable tails as weak evidence for scaling

When reporting uplift:

- use time-based validation
- do not claim stable action buckets if fold stability is poor
- do not force user-level recommendations from aggregate data

## Required Caveats

Add at least one explicit caveat when any of the following holds:

- weak LocalBaseline coverage
- sparse category slices
- missing exposure or discount fields
- unstable pretrend checks
- short activity windows
- weak GPS overlap
- unstable uplift folds

## Reporting Pattern

Prefer this pattern:

1. state the observable pattern
2. state the model layer used to adjust or validate
3. state what the result supports and what it does not support
4. state the main caveat
