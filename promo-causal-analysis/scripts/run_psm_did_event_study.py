from __future__ import annotations

import argparse

import numpy as np

from utils import (
    choose_available_columns,
    load_pandas,
    load_statsmodels_api,
    load_statsmodels_formula_api,
    normalize_numeric_columns,
    parse_csv_list,
    read_table,
    standardize_columns,
    write_json,
    write_table,
)


DEFAULT_MATCHING_COVARIATES = ["gmv", "view_uv", "discount_rate", "sale_num", "order_cnt", "buy_uv"]


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


def build_matching_frame(panel, candidate_categories, covariates):
    pd = load_pandas()
    subset = panel[panel["category_name_cn"].isin(candidate_categories)].copy()
    history = subset[subset["is_activity"] == 0].copy()
    if history.empty:
        first_activity = subset.loc[subset["is_activity"] == 1, "date"].min()
        if pd.notna(first_activity):
            history = subset[subset["date"] < first_activity].copy()
    if history.empty:
        history = subset.copy()

    available_covariates = choose_available_columns(history, covariates)
    if not available_covariates:
        return pd.DataFrame({"category_name_cn": sorted(candidate_categories)})

    aggregated = history.groupby("category_name_cn", as_index=False)[available_covariates].mean()
    rename_map = {column: f"{column}_baseline" for column in available_covariates}
    aggregated = aggregated.rename(columns=rename_map)
    return aggregated


def estimate_propensity(matching_frame, treated_categories):
    sm = load_statsmodels_api()
    frame = matching_frame.copy()
    frame["treated"] = frame["category_name_cn"].isin(treated_categories).astype(int)
    covariate_columns = [column for column in frame.columns if column not in {"category_name_cn", "treated"}]
    if not covariate_columns or frame["treated"].nunique() < 2:
        frame["propensity_score"] = frame["treated"].mean() if not frame.empty else 0.5
        return frame, covariate_columns, "fallback_constant"

    for column in covariate_columns:
        frame[column] = frame[column].fillna(frame[column].median())

    design = sm.add_constant(frame[covariate_columns], has_constant="add")
    try:
        model = sm.GLM(frame["treated"], design, family=sm.families.Binomial()).fit()
        propensity = model.predict(design)
        frame["propensity_score"] = np.clip(propensity, 1e-4, 1 - 1e-4)
        return frame, covariate_columns, "glm_binomial"
    except Exception:
        frame["propensity_score"] = frame["treated"].mean()
        return frame, covariate_columns, "fallback_constant"


def nearest_neighbor_match(propensity_frame, control_categories, caliper: float):
    control_pool = propensity_frame[propensity_frame["category_name_cn"].isin(control_categories)].copy()
    used_controls: set[str] = set()
    matched_controls: dict[str, str] = {}

    treated_rows = propensity_frame[propensity_frame["treated"] == 1].sort_values("propensity_score")
    for _, treated_row in treated_rows.iterrows():
        if control_pool.empty:
            break
        available_controls = control_pool[~control_pool["category_name_cn"].isin(used_controls)].copy()
        if available_controls.empty:
            break
        available_controls["distance"] = (available_controls["propensity_score"] - treated_row["propensity_score"]).abs()
        available_controls = available_controls.sort_values("distance")
        best = available_controls.iloc[0]
        if best["distance"] <= caliper:
            matched_controls[treated_row["category_name_cn"]] = best["category_name_cn"]
            used_controls.add(best["category_name_cn"])
    return set(matched_controls.keys()), set(matched_controls.values())


def prepare_sample(panel, treated_categories, control_categories):
    sample = panel[panel["category_name_cn"].isin(treated_categories | control_categories)].copy()
    sample["treated"] = sample["category_name_cn"].isin(treated_categories).astype(int)
    sample["post"] = sample["is_activity"].astype(int)
    activity_dates = sorted(sample.loc[sample["is_activity"] == 1, "date"].dropna().unique())
    if activity_dates:
        event_date = activity_dates[0]
        sample["relative_day"] = (sample["date"] - event_date).dt.days
    else:
        event_date = None
        sample["relative_day"] = np.nan
    return sample, event_date


def fit_did(sample, metric: str):
    smf = load_statsmodels_formula_api()
    formula = f"{metric} ~ treated * post + C(category_name_cn) + C(date)"
    return smf.ols(formula=formula, data=sample).fit(cov_type="HC1")


def pretrend_diagnostic(sample, metric: str):
    smf = load_statsmodels_formula_api()
    pre = sample[sample["post"] == 0].copy()
    if pre.empty or pre["treated"].nunique() < 2 or pre["date"].nunique() < 3:
        return {"status": "insufficient_preperiod"}
    model = smf.ols(f"{metric} ~ treated * relative_day + C(category_name_cn)", data=pre).fit(cov_type="HC1")
    term = "treated:relative_day"
    return {
        "status": "ok",
        "coefficient": float(model.params.get(term, 0.0)),
        "pvalue": float(model.pvalues.get(term, 1.0)),
    }


def placebo_diagnostic(sample, metric: str):
    smf = load_statsmodels_formula_api()
    pre = sample[sample["post"] == 0].copy()
    if pre.empty or pre["treated"].nunique() < 2 or pre["date"].nunique() < 4:
        return {"status": "insufficient_preperiod"}
    sorted_dates = sorted(pre["date"].dropna().unique())
    cutoff = sorted_dates[len(sorted_dates) // 2]
    pre["placebo_post"] = (pre["date"] >= cutoff).astype(int)
    model = smf.ols(f"{metric} ~ treated * placebo_post + C(category_name_cn) + C(date)", data=pre).fit(cov_type="HC1")
    term = "treated:placebo_post"
    return {
        "status": "ok",
        "coefficient": float(model.params.get(term, 0.0)),
        "pvalue": float(model.pvalues.get(term, 1.0)),
        "cutoff": str(cutoff),
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Run PSM plus DID and event-study style diagnostics.")
    parser.add_argument("--panel", required=True, help="Path to the category-day panel.")
    parser.add_argument("--metric", default="gmv", help="Outcome metric for DID.")
    parser.add_argument("--intensity-variable", required=True, help="Variable used to define treatment intensity.")
    parser.add_argument("--matching-covariates", help="Comma-separated pre-treatment covariates.")
    parser.add_argument("--summary-output", required=True, help="Path to the DID summary JSON.")
    parser.add_argument("--groups-output", required=True, help="Path to the group assignment CSV.")
    parser.add_argument("--matched-sample-output", help="Optional path to the matched sample CSV.")
    parser.add_argument("--treatment-quantile", type=float, default=0.75)
    parser.add_argument("--clean-control-quantile", type=float, default=0.25)
    parser.add_argument("--matching-caliper", type=float, default=0.1)
    return parser.parse_args()


def main():
    args = parse_args()
    pd = load_pandas()
    required = ["date", "category_name_cn", "is_activity", args.metric, args.intensity_variable]
    panel = standardize_columns(read_table(args.panel), required=required)
    panel = normalize_numeric_columns(panel, [args.metric, args.intensity_variable, *DEFAULT_MATCHING_COVARIATES])

    user_covariates = parse_csv_list(args.matching_covariates)
    covariates = user_covariates or DEFAULT_MATCHING_COVARIATES

    lift_table = build_lift_table(panel, args.intensity_variable)
    groups = assign_groups(lift_table, args.treatment_quantile, args.clean_control_quantile)

    group_rows = []
    matched_sample_frames = []
    summary = {
        "metric": args.metric,
        "intensity_variable": args.intensity_variable,
        "treatment_quantile": args.treatment_quantile,
        "clean_control_quantile": args.clean_control_quantile,
        "comparisons": {},
    }

    for comparison_name, (treated_categories, control_categories) in groups.items():
        if not treated_categories or not control_categories:
            summary["comparisons"][comparison_name] = {"status": "insufficient_groups"}
            continue

        candidate_categories = treated_categories | control_categories
        matching_frame = build_matching_frame(panel, candidate_categories, covariates)
        propensity_frame, used_covariates, propensity_model = estimate_propensity(matching_frame, treated_categories)
        propensity_frame["comparison"] = comparison_name
        propensity_frame["initial_group"] = np.where(
            propensity_frame["treated"] == 1,
            "treated",
            np.where(propensity_frame["category_name_cn"].isin(control_categories), "control", "other"),
        )

        matched_treated, matched_control = nearest_neighbor_match(
            propensity_frame[propensity_frame["category_name_cn"].isin(candidate_categories)],
            control_categories,
            caliper=args.matching_caliper,
        )
        if not matched_treated or not matched_control:
            matched_treated = treated_categories
            matched_control = control_categories
            match_status = "matching_failed_fallback_to_unmatched"
        else:
            match_status = "matched"

        propensity_frame["matched"] = propensity_frame["category_name_cn"].isin(matched_treated | matched_control)
        group_rows.append(propensity_frame)

        sample, event_date = prepare_sample(panel, matched_treated, matched_control)
        if sample.empty:
            summary["comparisons"][comparison_name] = {"status": "empty_sample"}
            continue

        try:
            model = fit_did(sample, args.metric)
            coef_name = "treated:post"
            result = {
                "status": "ok",
                "match_status": match_status,
                "propensity_model": propensity_model,
                "matching_covariates": used_covariates,
                "treated_categories_before_match": len(treated_categories),
                "control_categories_before_match": len(control_categories),
                "treated_categories_after_match": len(matched_treated),
                "control_categories_after_match": len(matched_control),
                "event_date": str(event_date) if event_date is not None else None,
                "did_coefficient": float(model.params.get(coef_name, 0.0)),
                "did_pvalue": float(model.pvalues.get(coef_name, 1.0)),
                "nobs": int(model.nobs),
                "pretrend": pretrend_diagnostic(sample, args.metric),
                "placebo": placebo_diagnostic(sample, args.metric),
            }
        except SystemExit:
            result = {"status": "statsmodels_unavailable", "match_status": match_status}
        summary["comparisons"][comparison_name] = result
        matched_sample_frames.append(sample.assign(comparison=comparison_name))

    groups_df = pd.concat(group_rows, ignore_index=True) if group_rows else pd.DataFrame()
    write_table(groups_df, args.groups_output)
    if args.matched_sample_output and matched_sample_frames:
        write_table(pd.concat(matched_sample_frames, ignore_index=True), args.matched_sample_output)
    write_json(summary, args.summary_output)


if __name__ == "__main__":
    main()
