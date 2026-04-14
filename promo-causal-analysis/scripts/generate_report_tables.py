from __future__ import annotations

import argparse
import json
from pathlib import Path

from utils import load_pandas


def markdown_table(df, max_rows: int = 10) -> str:
    if df.empty:
        return "_No rows available._"
    df = df.head(max_rows)
    columns = list(df.columns)
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = [
        "| " + " | ".join(str(row[column]) for column in columns) + " |"
        for _, row in df.iterrows()
    ]
    return "\n".join([header, divider, *rows])


def load_json(path: str | None):
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_args():
    parser = argparse.ArgumentParser(description="Generate report-ready markdown tables and narrative.")
    parser.add_argument("--descriptive-csv", help="CSV output from run_descriptive_stats.py.")
    parser.add_argument("--did-json", help="Legacy DID JSON output.")
    parser.add_argument("--psm-did-json", help="JSON output from run_psm_did_event_study.py.")
    parser.add_argument("--localgap-json", help="JSON output from run_localgap_model.py.")
    parser.add_argument("--category-csv", help="Category-level decomposition CSV.")
    parser.add_argument("--gps-json", help="JSON output from run_gps_response.py.")
    parser.add_argument("--gps-curve-csv", help="CSV dose-response curve from run_gps_response.py.")
    parser.add_argument("--uplift-csv", help="CSV output from run_uplift_prioritization.py.")
    parser.add_argument("--output", required=True, help="Output markdown path.")
    return parser.parse_args()


def main():
    args = parse_args()
    pd = load_pandas()

    sections: list[str] = ["# Promo Causal Analysis Report"]

    if args.descriptive_csv:
        descriptive = pd.read_csv(args.descriptive_csv)
        sections.extend(
            [
                "## Descriptive Statistics",
                "Raw activity vs non-activity differences are descriptive only and can still reflect cyclical demand timing.",
                markdown_table(descriptive),
            ]
        )

    did_summary = load_json(args.psm_did_json or args.did_json)
    if did_summary:
        rows = []
        for comparison_name, payload in did_summary.get("comparisons", {}).items():
            rows.append(
                {
                    "comparison": comparison_name,
                    "status": payload.get("status"),
                    "did_coefficient": payload.get("did_coefficient"),
                    "did_pvalue": payload.get("did_pvalue"),
                    "pretrend_status": payload.get("pretrend", {}).get("status"),
                    "pretrend_pvalue": payload.get("pretrend", {}).get("pvalue"),
                }
            )
        sections.extend(
            [
                "## PSM Plus DID or Event-Study Diagnostics",
                "Treat this section as directional support rather than as the final increment estimate.",
                markdown_table(pd.DataFrame(rows)),
            ]
        )

    localgap_summary = load_json(args.localgap_json)
    if localgap_summary:
        coeff_rows = [
            {"term": term, "coefficient": value}
            for term, value in localgap_summary.get("coefficients", {}).items()
        ]
        sections.extend(
            [
                "## LocalGap Main Analysis",
                f"Estimable activity rows: {localgap_summary.get('estimable_rows')}, coverage rate: {localgap_summary.get('coverage_rate')}",
                markdown_table(pd.DataFrame(coeff_rows)),
            ]
        )

    if args.category_csv:
        category = pd.read_csv(args.category_csv)
        sections.extend(
            [
                "## Category Decomposition",
                "Category labels summarize attribution patterns under the current model and should not be treated as immutable business truths.",
                markdown_table(category),
            ]
        )

    gps_summary = load_json(args.gps_json)
    if gps_summary:
        curve = pd.read_csv(args.gps_curve_csv) if args.gps_curve_csv else pd.DataFrame()
        sections.extend(
            [
                "## GPS Dose-Response",
                "Use this layer to read scaling logic and diminishing returns only within the supported treatment range.",
                markdown_table(pd.DataFrame([gps_summary])),
                markdown_table(curve),
            ]
        )

    if args.uplift_csv:
        uplift = pd.read_csv(args.uplift_csv)
        sections.extend(
            [
                "## Uplift Prioritization",
                "Use uplift as an allocation ranking layer rather than as stand-alone causal proof.",
                markdown_table(uplift),
            ]
        )

        bucket_counts = uplift["action_bucket"].value_counts().to_dict() if "action_bucket" in uplift.columns else {}
        sections.extend(
            [
                "## Recommendation Summary",
                f"Current action-bucket counts: {bucket_counts}",
            ]
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n\n".join(sections) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
