# Workflow

## Default Order

Run the workflow in this order unless the selected mode narrows scope:

1. Build or validate the category-day panel.
2. Run descriptive statistics.
3. Run DID or event-study if requested and feasible.
4. Run LocalGap.
5. Run category decomposition.
6. Generate report-ready outputs.

## Step 1: Build or Validate the Panel

Entry criteria:

- raw source tables or an existing panel are available

Exit criteria:

- category-day panel exists
- required fields are validated
- downgrade log is started if anything is missing

Skip logic:

- skip panel construction only when a valid panel already exists

## Step 2: Run Descriptive Statistics

Entry criteria:

- panel exists
- activity and non-activity rows both exist

Exit criteria:

- activity vs non-activity summary table is produced
- significance tests are produced when data supports them

Skip logic:

- do not skip in `full` mode unless the user explicitly asks to suppress descriptive output

## Step 3: Run DID or Event-Study

Entry criteria:

- mode includes DID
- treatment intensity can be defined
- pre-period coverage is sufficient

Exit criteria:

- coefficient table or event-study summary is produced
- pretrend diagnostics are reported
- caveats are recorded

Skip logic:

- skip when mode excludes DID
- skip when treatment definition or pretrend coverage is not defensible

## Step 4: Run LocalGap

Entry criteria:

- panel exists
- LocalBaseline can be constructed for at least part of the activity sample

Exit criteria:

- LocalGap summary is produced
- model diagnostics are produced
- baseline quality flags are reported

Skip logic:

- skip only in `descriptive_only`, `did_only`, or `report_only` modes
- downgrade if LocalBaseline coverage is too weak

## Step 5: Run Category Decomposition

Entry criteria:

- LocalGap results exist
- category coverage is sufficient for grouped summaries

Exit criteria:

- overall, monthly, and category-level summaries are produced

Skip logic:

- skip when channel inputs are missing and only total LocalGap can be reported

## Step 6: Generate Report Outputs

Entry criteria:

- at least one analysis section has produced usable output

Exit criteria:

- tables are organized for the selected mode
- narrative includes caveats and downgrade disclosures

## Quality Checks

Run these checks across the workflow:

- report missingness before interpretation
- report unavailable sections explicitly rather than silently omitting them
- keep downgrade reasons attached to the final narrative
