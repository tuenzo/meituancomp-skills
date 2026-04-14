from __future__ import annotations

import argparse

import numpy as np

from utils import (
    build_time_folds,
    choose_available_columns,
    load_pandas,
    normalize_numeric_columns,
    parse_csv_list,
    read_table,
    standardize_columns,
    write_json,
    write_table,
)


DEFAULT_FEATURES = ["gmv", "view_uv", "discount_rate", "sale_num", "order_cnt", "buy_uv", "dist2pay", "is_month_end"]


def parse_args():
    parser = argparse.ArgumentParser(description="Run uplift-based prioritization with time-safe folds.")
    parser.add_argument("--panel", required=True, help="Path to the category-day or enriched panel.")
    parser.add_argument("--treatment-variable", required=True, help="Variable used to define higher vs lower treatment.")
    parser.add_argument("--outcome-variable", default="local_gap", help="Outcome variable. Defaults to local_gap.")
    parser.add_argument("--features", help="Comma-separated feature list.")
    parser.add_argument("--summary-output", required=True, help="Path to summary JSON.")
    parser.add_argument("--scores-output", required=True, help="Path to category-level uplift scores CSV.")
    parser.add_argument("--treatment-quantile", type=float, default=0.75, help="Quantile used to define the high-treatment flag.")
    return parser.parse_args()


def fit_linear_uplift(train_df, features, outcome_variable):
    frame = train_df.copy()
    for column in features:
        frame[column] = frame[column].fillna(frame[column].median())
    x_base = frame[features].to_numpy(dtype=float) if features else np.empty((len(frame), 0))
    treated = frame["treated"].to_numpy(dtype=float).reshape(-1, 1)
    interaction = x_base * treated if features else np.empty((len(frame), 0))
    design = np.column_stack([np.ones(len(frame)), treated, x_base, interaction])
    target = frame[outcome_variable].to_numpy(dtype=float)
    coefficients, _, _, _ = np.linalg.lstsq(design, target, rcond=None)
    return coefficients


def predict_uplift(df, coefficients, features):
    frame = df.copy()
    for column in features:
        frame[column] = frame[column].fillna(frame[column].median())
    x_base = frame[features].to_numpy(dtype=float) if features else np.empty((len(frame), 0))
    ones = np.ones((len(frame), 1))
    treated_one = np.ones((len(frame), 1))
    treated_zero = np.zeros((len(frame), 1))
    interaction_one = x_base * treated_one if features else np.empty((len(frame), 0))
    interaction_zero = x_base * treated_zero if features else np.empty((len(frame), 0))
    design_one = np.column_stack([ones, treated_one, x_base, interaction_one])
    design_zero = np.column_stack([ones, treated_zero, x_base, interaction_zero])
    return design_one @ coefficients - design_zero @ coefficients


def assign_bucket(mean_uplift: float, stability: float | None):
    if stability is None:
        return "Observe"
    if mean_uplift > 0 and stability >= 0.67:
        return "Prioritize"
    if mean_uplift > 0:
        return "Selective"
    if mean_uplift < 0 and stability >= 0.67:
        return "Do Not Disturb"
    return "Observe"


def main():
    args = parse_args()
    pd = load_pandas()
    required = ["date", "category_name_cn", args.treatment_variable, args.outcome_variable]
    panel = standardize_columns(read_table(args.panel), required=required)
    panel = normalize_numeric_columns(panel, [args.treatment_variable, args.outcome_variable, *DEFAULT_FEATURES])

    if "is_activity" in panel.columns:
        working = panel[panel["is_activity"] == 1].copy()
    else:
        working = panel.copy()
    working = working.dropna(subset=[args.treatment_variable, args.outcome_variable]).copy()
    if working.empty:
        write_json({"status": "empty_sample"}, args.summary_output)
        write_table(pd.DataFrame(), args.scores_output)
        return

    features = parse_csv_list(args.features) or DEFAULT_FEATURES
    features = [
        column
        for column in choose_available_columns(working, features)
        if column not in {args.outcome_variable, args.treatment_variable, "treated"}
    ]
    threshold = float(working[args.treatment_variable].quantile(args.treatment_quantile))
    working["treated"] = (working[args.treatment_variable] >= threshold).astype(int)

    folds = build_time_folds(working)
    if not folds:
        write_json({"status": "insufficient_folds"}, args.summary_output)
        write_table(pd.DataFrame(), args.scores_output)
        return

    fold_rows = []
    for fold_id, (train_index, test_index) in enumerate(folds, start=1):
        train_df = working.loc[train_index].dropna(subset=[args.outcome_variable]).copy()
        test_df = working.loc[test_index].dropna(subset=[args.outcome_variable]).copy()
        if train_df.empty or test_df.empty or train_df["treated"].nunique() < 2:
            continue
        coefficients = fit_linear_uplift(train_df, features, args.outcome_variable)
        test_df["predicted_uplift"] = predict_uplift(test_df, coefficients, features)
        test_df["fold_id"] = fold_id
        fold_rows.append(test_df[["category_name_cn", "predicted_uplift", "fold_id"]])

    if not fold_rows:
        write_json({"status": "insufficient_estimable_folds"}, args.summary_output)
        write_table(pd.DataFrame(), args.scores_output)
        return

    scores = pd.concat(fold_rows, ignore_index=True)
    category_scores = (
        scores.groupby("category_name_cn", as_index=False)
        .agg(
            mean_uplift=("predicted_uplift", "mean"),
            fold_count=("fold_id", "nunique"),
            positive_fold_share=("predicted_uplift", lambda values: float((values > 0).mean())),
        )
    )
    category_scores["stability"] = category_scores["positive_fold_share"].apply(lambda value: max(value, 1 - value))
    category_scores["action_bucket"] = category_scores.apply(
        lambda row: assign_bucket(float(row["mean_uplift"]), float(row["stability"])),
        axis=1,
    )
    category_scores = category_scores.sort_values(["action_bucket", "mean_uplift"], ascending=[True, False])

    summary = {
        "status": "ok",
        "treatment_variable": args.treatment_variable,
        "outcome_variable": args.outcome_variable,
        "threshold": threshold,
        "features": features,
        "fold_count": int(scores["fold_id"].nunique()),
        "bucket_counts": category_scores["action_bucket"].value_counts().to_dict(),
    }
    write_json(summary, args.summary_output)
    write_table(category_scores, args.scores_output)


if __name__ == "__main__":
    main()
