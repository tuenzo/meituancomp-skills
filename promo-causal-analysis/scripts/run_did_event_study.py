from __future__ import annotations

import argparse

from utils import load_pandas, load_statsmodels_formula_api, normalize_numeric_columns, read_table, standardize_columns, write_json, write_table


def build_lift_table(panel, intensity_variable: str):
    non_activity = (
        panel[panel["is_activity"] == 0]
        .groupby("category_name_cn", as_index=False)
        .agg(reference_intensity=(intensity_variable, "mean"))
    )
    activity = (
        panel[panel["is_activity"] == 1]
        .groupby("category_name_cn", as_index=False)
        .agg(activity_intensity=(intensity_variable, "mean"))
    )
    lift = activity.merge(non_activity, on="category_name_cn", how="left")
    lift["reference_intensity"] = lift["reference_intensity"].fillna(0)
    lift["lift"] = lift["activity_intensity"] - lift["reference_intensity"]
    return lift


def assign_groups(lift_table, treatment_quantile: float, clean_control_quantile: float):
    high_cutoff = lift_table["lift"].quantile(treatment_quantile)
    low_cutoff = lift_table["lift"].quantile(clean_control_quantile)
    high = set(lift_table.loc[lift_table["lift"] >= high_cutoff, "category_name_cn"])
    low = set(lift_table.loc[lift_table["lift"] <= low_cutoff, "category_name_cn"])
    rest = set(lift_table["category_name_cn"]) - high
    return {"high_vs_rest": (high, rest), "high_vs_low": (high, low)}


def prepare_sample(panel, high_group, control_group):
    sample = panel[panel["category_name_cn"].isin(high_group | control_group)].copy()
    sample["treated"] = sample["category_name_cn"].isin(high_group).astype(int)
    sample["post"] = sample["is_activity"].astype(int)
    activity_dates = sorted(panel.loc[panel["is_activity"] == 1, "date"].dropna().unique())
    if activity_dates:
        event_date = activity_dates[0]
        sample["relative_day"] = (sample["date"] - event_date).dt.days
    else:
        event_date = None
        sample["relative_day"] = None
    return sample, event_date


def fit_did(sample, metric: str):
    smf = load_statsmodels_formula_api()
    formula = f"{metric} ~ treated * post + C(category_name_cn) + C(date)"
    return smf.ols(formula=formula, data=sample).fit(cov_type="HC1")


def pretrend_diagnostic(sample, metric: str):
    pre = sample[sample["post"] == 0].copy()
    if pre.empty or pre["treated"].nunique() < 2 or pre["date"].nunique() < 3:
        return {"status": "insufficient_preperiod"}
    smf = load_statsmodels_formula_api()
    model = smf.ols(f"{metric} ~ treated * relative_day + C(category_name_cn)", data=pre).fit(cov_type="HC1")
    term = "treated:relative_day"
    return {
        "status": "ok",
        "coefficient": float(model.params.get(term, 0.0)),
        "pvalue": float(model.pvalues.get(term, 1.0)),
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Run DID and event-study style diagnostics.")
    parser.add_argument("--panel", required=True, help="Path to the category-day panel.")
    parser.add_argument("--metric", default="gmv", help="Outcome metric for DID.")
    parser.add_argument("--intensity-variable", required=True, help="Variable used to define treatment intensity.")
    parser.add_argument("--summary-output", required=True, help="Path to the DID summary JSON.")
    parser.add_argument("--groups-output", required=True, help="Path to the group assignment CSV.")
    parser.add_argument("--treatment-quantile", type=float, default=0.75)
    parser.add_argument("--clean-control-quantile", type=float, default=0.25)
    return parser.parse_args()


def main():
    args = parse_args()
    pd = load_pandas()
    panel = standardize_columns(read_table(args.panel), required=["date", "category_name_cn", "is_activity", args.metric, args.intensity_variable])
    panel = normalize_numeric_columns(panel, [args.metric, args.intensity_variable])

    lift_table = build_lift_table(panel, args.intensity_variable)
    groups = assign_groups(lift_table, args.treatment_quantile, args.clean_control_quantile)

    group_rows = []
    summary = {
        "metric": args.metric,
        "intensity_variable": args.intensity_variable,
        "treatment_quantile": args.treatment_quantile,
        "clean_control_quantile": args.clean_control_quantile,
        "comparisons": {},
    }

    for comparison_name, (high_group, control_group) in groups.items():
        if not high_group or not control_group:
            summary["comparisons"][comparison_name] = {"status": "insufficient_groups"}
            continue

        sample, event_date = prepare_sample(panel, high_group, control_group)
        for category in sorted(high_group):
            group_rows.append({"comparison": comparison_name, "category_name_cn": category, "group": "treated"})
        for category in sorted(control_group):
            group_rows.append({"comparison": comparison_name, "category_name_cn": category, "group": "control"})

        result = {"treated_categories": len(high_group), "control_categories": len(control_group), "event_date": str(event_date) if event_date is not None else None}
        try:
            model = fit_did(sample, args.metric)
            coef_name = "treated:post"
            result["status"] = "ok"
            result["did_coefficient"] = float(model.params.get(coef_name, 0.0))
            result["did_pvalue"] = float(model.pvalues.get(coef_name, 1.0))
            result["nobs"] = int(model.nobs)
        except SystemExit:
            result["status"] = "statsmodels_unavailable"
        result["pretrend"] = pretrend_diagnostic(sample, args.metric) if sample["relative_day"].notna().all() else {"status": "no_event_date"}
        summary["comparisons"][comparison_name] = result

    groups_df = pd.DataFrame(group_rows)
    write_table(groups_df, args.groups_output)
    write_json(summary, args.summary_output)


if __name__ == "__main__":
    main()
