from __future__ import annotations

import argparse

from utils import (
    add_calendar_helpers,
    ensure_columns,
    normalize_numeric_columns,
    read_table,
    standardize_columns,
    summarize_panel,
    write_json,
    write_table,
)


NUMERIC_ORDER_COLUMNS = ["gmv", "sale_num", "order_cnt", "discount_rate", "buy_uv", "is_activity"]
NUMERIC_EXPOSURE_COLUMNS = ["view_uv"]


def validate_inputs(orders, exposure, activity_calendar) -> None:
    ensure_columns(orders, ["date", "category_name_cn", "gmv"])
    if exposure is not None:
        ensure_columns(exposure, ["date", "category_name_cn", "view_uv"])
    if activity_calendar is not None:
        ensure_columns(activity_calendar, ["date", "is_activity"])


def aggregate_orders(orders):
    orders = normalize_numeric_columns(orders, NUMERIC_ORDER_COLUMNS)
    aggregations = {"gmv": "sum"}
    for column in ["sale_num", "order_cnt", "buy_uv"]:
        if column in orders.columns:
            aggregations[column] = "sum"
    if "discount_rate" in orders.columns:
        aggregations["discount_rate"] = "mean"
    if "is_activity" in orders.columns:
        aggregations["is_activity"] = "max"
    grouped = orders.groupby(["date", "category_name_cn"], as_index=False).agg(aggregations)
    return grouped


def aggregate_exposure(exposure):
    exposure = normalize_numeric_columns(exposure, NUMERIC_EXPOSURE_COLUMNS)
    grouped = (
        exposure.groupby(["date", "category_name_cn"], as_index=False)
        .agg({"view_uv": "sum"})
    )
    return grouped


def merge_activity_calendar(panel, activity_calendar):
    if activity_calendar is None:
        if "is_activity" not in panel.columns:
            panel["is_activity"] = 0
        return panel

    activity_daily = activity_calendar.groupby("date", as_index=False).agg({"is_activity": "max"})
    merged = panel.merge(activity_daily, on="date", how="left", suffixes=("", "_calendar"))
    if "is_activity_calendar" in merged.columns:
        merged["is_activity"] = merged["is_activity_calendar"].fillna(merged.get("is_activity", 0)).fillna(0)
        merged = merged.drop(columns=["is_activity_calendar"])
    merged["is_activity"] = merged["is_activity"].fillna(0).astype(int)
    return merged


def build_panel(orders, exposure=None, activity_calendar=None, payday_anchor: int = 27):
    order_panel = aggregate_orders(orders)
    if exposure is not None:
        exposure_panel = aggregate_exposure(exposure)
        panel = order_panel.merge(exposure_panel, on=["date", "category_name_cn"], how="outer")
    else:
        panel = order_panel.copy()

    panel["gmv"] = panel["gmv"].fillna(0)
    for column in ["sale_num", "order_cnt", "discount_rate", "view_uv", "buy_uv"]:
        if column in panel.columns:
            panel[column] = panel[column].fillna(0)

    panel = merge_activity_calendar(panel, activity_calendar)
    panel = add_calendar_helpers(panel, payday_anchor=payday_anchor)
    if "view_uv" in panel.columns and "buy_uv" in panel.columns:
        panel["conversion_rate"] = panel["buy_uv"].where(panel["view_uv"] != 0, 0) / panel["view_uv"].where(panel["view_uv"] != 0, 1)
    panel = panel.sort_values(["date", "category_name_cn"]).reset_index(drop=True)
    return panel


def parse_args():
    parser = argparse.ArgumentParser(description="Build a category-day panel for promotion analysis.")
    parser.add_argument("--orders", required=True, help="Path to the raw orders table.")
    parser.add_argument("--exposure", help="Path to the raw exposure table.")
    parser.add_argument("--activity-calendar", help="Path to the activity calendar table.")
    parser.add_argument("--output", required=True, help="Output path for the category-day panel.")
    parser.add_argument("--metadata-output", required=True, help="Output path for panel metadata JSON.")
    parser.add_argument("--payday-anchor", type=int, default=27, help="Anchor day used for dist2pay.")
    return parser.parse_args()


def main():
    args = parse_args()
    orders = standardize_columns(read_table(args.orders), required=["date", "category_name_cn", "gmv"])
    exposure = standardize_columns(read_table(args.exposure), required=["date", "category_name_cn", "view_uv"]) if args.exposure else None
    activity_calendar = standardize_columns(read_table(args.activity_calendar), required=["date", "is_activity"]) if args.activity_calendar else None

    validate_inputs(orders, exposure, activity_calendar)
    panel = build_panel(orders, exposure=exposure, activity_calendar=activity_calendar, payday_anchor=args.payday_anchor)
    write_table(panel, args.output)
    metadata = summarize_panel(panel)
    metadata["columns"] = list(panel.columns)
    metadata["downgrades"] = {
        "missing_exposure": exposure is None,
        "missing_activity_calendar": activity_calendar is None and "is_activity" not in orders.columns,
        "missing_buy_uv": "buy_uv" not in panel.columns,
        "missing_discount_rate": "discount_rate" not in panel.columns,
    }
    write_json(metadata, args.metadata_output)


if __name__ == "__main__":
    main()
