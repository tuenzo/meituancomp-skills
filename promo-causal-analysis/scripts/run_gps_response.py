from __future__ import annotations

import argparse
import math

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


DEFAULT_COVARIATES = ["gmv", "view_uv", "discount_rate", "sale_num", "order_cnt", "buy_uv", "dist2pay", "is_month_end"]


def normal_density(values, means, sigma: float):
    sigma = max(float(sigma), 1e-6)
    z = (values - means) / sigma
    return (1.0 / (sigma * math.sqrt(2 * math.pi))) * np.exp(-0.5 * np.square(z))


def parse_args():
    parser = argparse.ArgumentParser(description="Run generalized propensity score dose-response estimation.")
    parser.add_argument("--panel", required=True, help="Path to the category-day or enriched panel.")
    parser.add_argument("--treatment-variable", required=True, help="Continuous treatment variable.")
    parser.add_argument("--outcome-variable", default="local_gap", help="Outcome variable. Defaults to local_gap.")
    parser.add_argument("--covariates", help="Comma-separated covariates for the treatment model.")
    parser.add_argument("--summary-output", required=True, help="Path to GPS summary JSON.")
    parser.add_argument("--curve-output", required=True, help="Path to dose-response CSV.")
    parser.add_argument("--grid-points", type=int, default=20, help="Number of grid points for the dose-response curve.")
    return parser.parse_args()


def main():
    args = parse_args()
    pd = load_pandas()
    sm = load_statsmodels_api()
    smf = load_statsmodels_formula_api()

    required = ["date", "category_name_cn", args.treatment_variable, args.outcome_variable]
    panel = standardize_columns(read_table(args.panel), required=required)
    panel = normalize_numeric_columns(panel, [args.treatment_variable, args.outcome_variable, *DEFAULT_COVARIATES])

    if "is_activity" in panel.columns:
        working = panel[panel["is_activity"] == 1].copy()
    else:
        working = panel.copy()
    working = working.dropna(subset=[args.treatment_variable, args.outcome_variable]).copy()

    selected_covariates = parse_csv_list(args.covariates) or DEFAULT_COVARIATES
    covariates = [
        column
        for column in choose_available_columns(working, selected_covariates)
        if column not in {args.treatment_variable, args.outcome_variable}
    ]

    if working.empty:
        write_json({"status": "empty_sample"}, args.summary_output)
        write_table(pd.DataFrame(), args.curve_output)
        return

    if covariates:
        covariate_frame = working[covariates].copy()
        for column in covariates:
            covariate_frame[column] = covariate_frame[column].fillna(covariate_frame[column].median())
        design = sm.add_constant(covariate_frame, has_constant="add")
        treatment_model = sm.OLS(working[args.treatment_variable], design).fit()
        predicted_treatment = treatment_model.predict(design)
    else:
        predicted_treatment = pd.Series(working[args.treatment_variable].mean(), index=working.index)

    sigma = float((working[args.treatment_variable] - predicted_treatment).std(ddof=1))
    if not np.isfinite(sigma) or sigma <= 0:
        write_json({"status": "insufficient_treatment_variation"}, args.summary_output)
        write_table(pd.DataFrame(), args.curve_output)
        return

    working["gps"] = normal_density(working[args.treatment_variable], predicted_treatment, sigma)
    working["treatment_sq"] = np.square(working[args.treatment_variable])
    working["gps_sq"] = np.square(working["gps"])
    working["treatment_x_gps"] = working[args.treatment_variable] * working["gps"]

    response_formula = (
        f"{args.outcome_variable} ~ {args.treatment_variable} + treatment_sq + gps + gps_sq + treatment_x_gps"
    )
    response_model = smf.ols(response_formula, data=working).fit(cov_type="HC1")

    lower = float(working[args.treatment_variable].quantile(0.05))
    upper = float(working[args.treatment_variable].quantile(0.95))
    if lower == upper:
        lower = float(working[args.treatment_variable].min())
        upper = float(working[args.treatment_variable].max())
    grid = np.linspace(lower, upper, max(args.grid_points, 5))

    curve_rows = []
    for dose in grid:
        gps_for_dose = normal_density(dose, predicted_treatment, sigma)
        prediction_frame = pd.DataFrame(
            {
                args.treatment_variable: dose,
                "treatment_sq": dose ** 2,
                "gps": gps_for_dose,
                "gps_sq": np.square(gps_for_dose),
                "treatment_x_gps": dose * gps_for_dose,
            }
        )
        predicted_outcome = response_model.predict(prediction_frame).mean()
        curve_rows.append({"dose": float(dose), "predicted_outcome": float(predicted_outcome)})

    curve = pd.DataFrame(curve_rows)
    increments = curve["predicted_outcome"].diff().dropna()
    diminishing = bool(not increments.empty and increments.iloc[-1] < increments.iloc[0])

    summary = {
        "status": "ok",
        "treatment_variable": args.treatment_variable,
        "outcome_variable": args.outcome_variable,
        "covariates": covariates,
        "supported_range": {"lower": lower, "upper": upper},
        "sample_size": int(len(working)),
        "sigma": sigma,
        "response_delta": float(curve["predicted_outcome"].iloc[-1] - curve["predicted_outcome"].iloc[0]),
        "diminishing_returns": diminishing,
        "model_r_squared": float(response_model.rsquared),
    }
    write_json(summary, args.summary_output)
    write_table(curve, args.curve_output)


if __name__ == "__main__":
    main()
