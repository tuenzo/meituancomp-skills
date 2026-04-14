# Report Template

## Default Structure

Use this section order for a full business-facing output:

1. Data summary
2. Business-oriented EDA
3. PSM + DID / event study
4. LocalGap main increment
5. GPS dose-response
6. Uplift prioritization
7. Recommendation summary
8. Caveats and limits

## Section Templates

### Data Summary

"The analysis uses a category-day panel built from the available source tables. The panel covers [date range], includes [category count] categories, and identifies [activity day count] activity dates. Missing fields and downgraded modules are disclosed before interpretation."

### Business-Oriented EDA

"Activity periods show [higher/lower/similar] GMV than non-activity periods, together with differences in [exposure/discount/conversion]. These contrasts are descriptive only and may still reflect cyclical demand timing."

### PSM + DID / Event Study

"A matched DID or event-study comparison between higher-intensity and lower-intensity groups provides [supportive/mixed/weak] directional evidence. This layer should be read as auxiliary causal support rather than as the final increment estimate."

### LocalGap Main Increment

"Relative to the local historical non-activity baseline, activity-period observations show a LocalGap of [summary]. This is the main incremental accounting layer in the workflow."

### GPS Dose-Response

"The GPS dose-response curve suggests [monotonic growth / diminishing returns / flat response / unstable tail behavior] over the supported treatment range. Interpretation outside supported overlap should be avoided."

### Uplift Prioritization

"Uplift scoring suggests that [category group] should be prioritized, while [category group] should be treated selectively or left undisturbed. These recommendations depend on fold stability and should not be interpreted as standalone causal proof."

### Recommendation Summary

"Taken together, the evidence supports [scale / optimize / hold / reduce disturbance] as the primary strategy. The conclusion is anchored on LocalGap, refined by GPS, and prioritized through uplift."

### Caveats

"Results should be interpreted with caution because [main caveat]. In particular, [secondary caveat] limits how strongly the findings can be described as incremental or causal."

## Formatting Rules

Keep narrative concise and decision-oriented.

Do not pad the report with file inventories or script logs unless the user asks for implementation detail.
