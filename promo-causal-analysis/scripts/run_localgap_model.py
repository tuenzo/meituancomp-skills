from __future__ import annotations

import argparse
from typing import Any

from utils import (
    load_pandas,
    load_statsmodels_formula_api,
    normalize_numeric_columns,
    read_table,
    standardize_columns,
    write_json,
    write_table,
)

def compute_local_baseline(
    panel,
    recent_window_days: int,
    fallback_window_days: int,
    min_obs: int,
    recommended_obs: int,
):
    pd = load_pandas()
    rows: list[dict[str, Any]] = []
    panel = panel.sort_values(["category_name_cn", "date"]).copy()

    for category, group in panel.groupby("category_name_cn", sort=False):
        history = group[group["is_activity"] == 0].copy()
        for _, row in group.iterrows():
            current_date = row["date"]
            weekday = row["weekday"]
            candidates = history[(history["date"] < current_date) & (history["weekday"] == weekday)]

            recent_cutoff = current_date - pd.Timedelta(days=recent_window_days)
            fallback_cutoff = current_date - pd.Timedelta(days=fallback_window_days)

            recent = candidates[candidates["date"] >= recent_cutoff]
            extended = candidates[candidates["date"] >= fallback_cutoff]

            if len(recent) >= min_obs:
                chosen = recent
            elif len(extended) >= min_obs:
                chosen = extended
            else:
                chosen = candidates

            baseline = None
            baseline_obs = int(len(chosen))
            quality = "unavailable"
            if baseline_obs >= min_obs:
                baseline = float(chosen["gmv"].mean())
                quality = "strong" if baseline_obs >= recommended_obs else "weak"

            rows.append(
                {
                    "category_name_cn": category,
                    "date": current_date,
                    "local_baseline": baseline,
                    "baseline_obs": baseline_obs,
                    "baseline_quality": quality,
                }
            )
    baseline_df = pd.DataFrame(rows)
    merged = panel.merge(baseline_df, on=["category_name_cn", "date"], how="left")
    merged["local_gap"] = merged["gmv"] - merged["local_baseline"]
    return merged


def add_reference_terms(panel):
    pd = load_pandas()
    non_activity = panel[panel["is_activity"] == 0].copy()
    refs = non_activity.groupby("category_name_cn", as_index=False).agg(
        ref_view=("view_uv", "median") if "view_uv" in panel.columns else ("gmv", "size"),
        ref_discount=("discount_rate", "median") if "discount_rate" in panel.columns else ("gmv", "size"),
    )
    if "view_uv" not in panel.columns:
        refs = refs.drop(columns=["ref_view"])
    if "discount_rate" not in panel.columns:
        refs = refs.drop(columns=["ref_discount"])

    merged = panel.merge(refs, on="category_name_cn", how="left")
    if "view_uv" in merged.columns and "ref_view" in merged.columns:
        merged["log_view_uv"] = (merged["view_uv"].fillna(0) + 1).map(__import__("math").log)
        merged["log_ref_view"] = (merged["ref_view"].fillna(0) + 1).map(__import__("math").log)
        merged["excess_view"] = merged["log_view_uv"] - merged["log_ref_view"]
    if "discount_rate" in merged.columns and "ref_discount" in merged.columns:
        merged["excess_discount"] = merged["discount_rate"] - merged["ref_discount"]
    if {"excess_view", "excess_discount"}.issubset(merged.columns):
        merged["excess_inter"] = merged["excess_view"] * merged["excess_discount"]
    return merged


def fit_model(activity_sample, include_month_fe: bool):
    smf = load_statsmodels_formula_api()
    terms = []
    for column in ["excess_discount", "excess_view", "excess_inter", "dist2pay"]:
        if column in activity_sample.columns:
            terms.append(column)
    if "dist2pay" in activity_sample.columns:
        activity_sample["dist2pay_sq"] = activity_sample["dist2pay"] ** 2
        terms.append("dist2pay_sq")
    if not terms:
        return None

    rhs = terms + ["C(category_name_cn)"]
    if include_month_fe and activity_sample["month"].nunique() > 1:
        rhs.append("C(month)")
    formula = "local_gap ~ " + " + ".join(rhs)
    model = smf.ols(formula=formula, data=activity_sample).fit(cov_type="HC1")
    return model


def parse_args():
    parser = argparse.ArgumentParser(description="Run the LocalGap main analysis.")
    parser.add_argument("--panel", required=True, help="Path to the category-day panel.")
    parser.add_argument("--panel-output", required=True, help="Path to the enriched panel output.")
    parser.add_argument("--summary-output", required=True, help="Path to the LocalGap summary JSON.")
    parser.add_argument("--recent-window-days", type=int, default=56)
    parser.add_argument("--fallback-window-days", type=int, default=112)
    parser.add_argument("--min-local-baseline-obs", type=int, default=2)
    parser.add_argument("--recommended-local-baseline-obs", type=int, default=4)
    parser.add_argument("--include-month-fe", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    pd = load_pandas()
    panel = standardize_columns(read_table(args.panel), required=["date", "category_name_cn", "is_activity", "gmv"])
    panel = normalize_numeric_columns(panel, ["gmv", "view_uv", "discount_rate", "buy_uv", "dist2pay"])

    if "weekday" not in panel.columns:
        panel["weekday"] = panel["date"].dt.day_name()
    if "month" not in panel.columns:
        panel["month"] = panel["date"].dt.to_period("M").astype(str)
    if "dist2pay" not in panel.columns:
        panel["dist2pay"] = panel["date"].dt.day - 27

    enriched = compute_local_baseline(
        panel,
        recent_window_days=args.recent_window_days,
        fallback_window_days=args.fallback_window_days,
        min_obs=args.min_local_baseline_obs,
        recommended_obs=args.recommended_local_baseline_obs,
    )
    enriched = add_reference_terms(enriched)

    activity_sample = enriched[(enriched["is_activity"] == 1) & enriched["local_baseline"].notna()].copy()
    model = None
    if not activity_sample.empty:
        try:
            model = fit_model(activity_sample, include_month_fe=args.include_month_fe)
        except SystemExit:
            model = None

    write_table(enriched, args.panel_output)

    quality_counts = (
        enriched.loc[enriched["is_activity"] == 1, "baseline_quality"]
        .fillna("unavailable")
        .value_counts()
        .to_dict()
    )
    summary = {
        "activity_rows": int((enriched["is_activity"] == 1).sum()),
        "estimable_rows": int(len(activity_sample)),
        "baseline_quality": quality_counts,
        "mean_local_gap": float(activity_sample["local_gap"].mean()) if not activity_sample.empty else None,
        "coverage_rate": float(len(activity_sample) / max(int((enriched["is_activity"] == 1).sum()), 1)),
        "coefficients": {},
    }
    if model is not None:
        summary["coefficients"] = {
            name: float(value)
            for name, value in model.params.items()
            if name in {"Intercept", "excess_discount", "excess_view", "excess_inter", "dist2pay", "dist2pay_sq"}
        }
        summary["r_squared"] = float(model.rsquared)
        summary["nobs"] = int(model.nobs)
    write_json(summary, args.summary_output)


if __name__ == "__main__":
    main()
