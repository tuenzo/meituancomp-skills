# Report Template

## Default Structure

Use the sections below when the user asks for full analysis or report-ready output:

1. Data summary
2. Descriptive comparison
3. DID or event-study diagnostics if run
4. LocalGap main findings
5. Category decomposition
6. Caveats and limits

## Section Templates

### Data Summary

Use this pattern:

"The analysis uses a category-day panel built from the available source tables. The panel covers [date range], includes [category count] categories, and identifies [activity day count] activity dates. Missing exposure, discount, or conversion fields are disclosed before model interpretation."

### Descriptive Comparison

Use this pattern:

"Activity periods show [higher/lower/similar] GMV than non-activity periods, along with differences in [exposure/discount/conversion]. These raw contrasts are descriptive only and may still reflect cyclical demand timing."

### DID or Event-Study

Use this pattern:

"A DID or event-study diagnostic comparing higher-intensity and lower-intensity groups provides [supportive/mixed/weak] directional evidence. Because treatment intensity is constructed from realized exposure or discount patterns, this section should be read as supportive rather than definitive."

### LocalGap Findings

Use this pattern:

"Relative to the local historical non-activity baseline, activity-period observations show a LocalGap of [summary]. The estimated channel terms indicate that LocalGap is [more/less] associated with excess exposure, excess discount, and their interaction, subject to baseline quality and data coverage."

### Category Decomposition

Use this pattern:

"Category-level results suggest three broad patterns: exposure-driven categories, residual-heavy categories, and mixed categories. These labels summarize model attribution patterns rather than immutable business truths."

### Caveats

Use this pattern:

"Results should be interpreted with caution because [main caveat]. In particular, [secondary caveat] limits how strongly the findings can be described as incremental or causal."

## Formatting Rules

Keep narrative concise and decision-oriented.

Do not pad the report with file inventories or script logs unless the user asks for implementation detail.
