from __future__ import annotations

import argparse

from utils import load_scipy_stats, read_table, safe_ratio, standardize_columns, write_json, write_table


METRICS = ["gmv", "discount_rate", "view_uv", "buy_uv", "conversion_rate"]


def build_summary(panel):
    stats = load_scipy_stats()
    activity = panel[panel["is_activity"] == 1]
    non_activity = panel[panel["is_activity"] == 0]
    rows = []

    for metric in METRICS:
        if metric == "conversion_rate" and metric not in panel.columns and {"buy_uv", "view_uv"}.issubset(panel.columns):
            panel[metric] = safe_ratio(panel["buy_uv"], panel["view_uv"]).fillna(0)
            activity = panel[panel["is_activity"] == 1]
            non_activity = panel[panel["is_activity"] == 0]
        if metric not in panel.columns:
            continue

        series_a = activity[metric].dropna()
        series_n = non_activity[metric].dropna()
        row = {
            "metric": metric,
            "activity_mean": float(series_a.mean()) if not series_a.empty else None,
            "non_activity_mean": float(series_n.mean()) if not series_n.empty else None,
            "mean_diff": float(series_a.mean() - series_n.mean()) if not series_a.empty and not series_n.empty else None,
        }
        if stats and len(series_a) > 1 and len(series_n) > 1:
            ttest = stats.ttest_ind(series_a, series_n, equal_var=False, nan_policy="omit")
            mw = stats.mannwhitneyu(series_a, series_n, alternative="two-sided")
            row["welch_t_pvalue"] = float(ttest.pvalue)
            row["mann_whitney_pvalue"] = float(mw.pvalue)
        else:
            row["welch_t_pvalue"] = None
            row["mann_whitney_pvalue"] = None
        rows.append(row)
    return rows


def parse_args():
    parser = argparse.ArgumentParser(description="Run descriptive activity vs non-activity statistics.")
    parser.add_argument("--panel", required=True, help="Path to the category-day panel.")
    parser.add_argument("--output", required=True, help="Path to the output CSV summary.")
    parser.add_argument("--metadata-output", required=True, help="Path to the output JSON metadata.")
    return parser.parse_args()


def main():
    args = parse_args()
    panel = standardize_columns(read_table(args.panel), required=["date", "category_name_cn", "is_activity", "gmv"])
    summary_rows = build_summary(panel)

    pd = __import__("pandas")
    summary = pd.DataFrame(summary_rows)
    write_table(summary, args.output)
    write_json(
        {
            "activity_rows": int((panel["is_activity"] == 1).sum()),
            "non_activity_rows": int((panel["is_activity"] == 0).sum()),
            "metric_count": int(len(summary_rows)),
            "scipy_available": load_scipy_stats() is not None,
        },
        args.metadata_output,
    )


if __name__ == "__main__":
    main()
