from __future__ import annotations

import argparse
import json
from pathlib import Path

from utils import load_pandas, read_table, standardize_columns, write_json, write_table


def load_coefficients(summary_path: str | Path) -> dict[str, float]:
    payload = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    return payload.get("coefficients", {})


def classify_category(row):
    exposure = abs(row.get("exposure_component", 0.0))
    discount = abs(row.get("discount_component", 0.0))
    interaction = abs(row.get("interaction_component", 0.0))
    residual = abs(row.get("residual_component", 0.0))
    if residual > max(exposure, discount, interaction):
        return "residual-heavy"
    if exposure > max(discount, interaction, residual):
        return "exposure-driven"
    return "mixed"


def component_series(df, column: str):
    if column in df.columns:
        return df[column].fillna(0)
    return 0


def parse_args():
    parser = argparse.ArgumentParser(description="Summarize overall, monthly, and category-level decomposition.")
    parser.add_argument("--panel", required=True, help="Path to the enriched LocalGap panel.")
    parser.add_argument("--localgap-summary", required=True, help="Path to the LocalGap summary JSON.")
    parser.add_argument("--output-dir", required=True, help="Directory for decomposition tables.")
    return parser.parse_args()


def main():
    args = parse_args()
    pd = load_pandas()
    panel = standardize_columns(read_table(args.panel), required=["date", "category_name_cn", "is_activity", "gmv"])
    coefficients = load_coefficients(args.localgap_summary)

    working = panel[panel["is_activity"] == 1].copy()
    working["local_gap"] = working.get("local_gap", working["gmv"])
    working["exposure_component"] = component_series(working, "excess_view") * coefficients.get("excess_view", 0.0)
    working["discount_component"] = component_series(working, "excess_discount") * coefficients.get("excess_discount", 0.0)
    working["interaction_component"] = component_series(working, "excess_inter") * coefficients.get("excess_inter", 0.0)
    working["explained_component"] = (
        working["exposure_component"] + working["discount_component"] + working["interaction_component"]
    )
    working["residual_component"] = working["local_gap"] - working["explained_component"]
    if "month" not in working.columns:
        working["month"] = working["date"].dt.to_period("M").astype(str)

    overall = pd.DataFrame(
        [
            {
                "local_gap": float(working["local_gap"].sum()),
                "exposure_component": float(working["exposure_component"].sum()),
                "discount_component": float(working["discount_component"].sum()),
                "interaction_component": float(working["interaction_component"].sum()),
                "residual_component": float(working["residual_component"].sum()),
            }
        ]
    )
    monthly = (
        working.groupby("month", as_index=False)[
            ["local_gap", "exposure_component", "discount_component", "interaction_component", "residual_component"]
        ]
        .sum()
        .sort_values("month")
    )
    category = (
        working.groupby("category_name_cn", as_index=False)[
            ["local_gap", "exposure_component", "discount_component", "interaction_component", "residual_component"]
        ]
        .sum()
    )
    category["classification"] = category.apply(classify_category, axis=1)
    category = category.sort_values("local_gap", ascending=False)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_table(overall, output_dir / "overall.csv")
    write_table(monthly, output_dir / "monthly.csv")
    write_table(category, output_dir / "category.csv")
    write_json(
        {
            "category_count": int(len(category)),
            "classifications": category["classification"].value_counts().to_dict(),
            "local_gap_total": float(overall.loc[0, "local_gap"]) if not overall.empty else 0.0,
        },
        output_dir / "summary.json",
    )


if __name__ == "__main__":
    main()
