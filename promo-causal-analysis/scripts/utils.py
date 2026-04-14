from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


COLUMN_ALIASES = {
    "date": ["date", "dt", "biz_date", "stat_date"],
    "category_name_cn": ["category_name_cn", "category_name", "cate_name", "category", "class_name"],
    "category_id": ["category_id", "cate_id", "category_code", "class_id"],
    "is_activity": ["is_activity", "activity_flag", "is_promo", "promo_flag"],
    "gmv": ["gmv", "sku_sale_amt", "sale_amt", "sales", "revenue"],
    "sale_num": ["sale_num", "sales_qty", "qty", "volume"],
    "order_cnt": ["order_cnt", "order_num", "orders"],
    "discount_rate": ["discount_rate", "discount", "discount_pct"],
    "view_uv": ["view_uv", "exposure_uv", "impression_uv", "browse_uv"],
    "buy_uv": ["buy_uv", "purchase_uv", "order_uv"],
    "sku_id": ["sku_id", "sku", "item_id", "goods_id", "product_id"],
}


def load_pandas():
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit(
            "pandas is required to run this script. Install pandas before execution."
        ) from exc
    return pd


def load_statsmodels_formula_api():
    try:
        import statsmodels.formula.api as smf
    except ImportError as exc:
        raise SystemExit(
            "statsmodels is required to run this script. Install statsmodels before execution."
        ) from exc
    return smf


def load_statsmodels_api():
    try:
        import statsmodels.api as sm
    except ImportError as exc:
        raise SystemExit(
            "statsmodels is required to run this script. Install statsmodels before execution."
        ) from exc
    return sm


def load_scipy_stats():
    try:
        from scipy import stats
    except ImportError:
        return None
    return stats


def parse_csv_list(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def read_table(path: str | Path):
    pd = load_pandas()
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if suffix == ".json":
        return pd.read_json(path)
    raise SystemExit(f"Unsupported input format: {path}")


def write_table(df, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df.to_csv(path, index=False)
        return
    if suffix in {".parquet", ".pq"}:
        df.to_parquet(path, index=False)
        return
    raise SystemExit(f"Unsupported output format: {path}")


def write_json(payload: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def standardize_columns(df, required: Iterable[str] | None = None):
    pd = load_pandas()
    columns_lower = {str(col).strip().lower(): col for col in df.columns}
    rename_map: dict[Any, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            source = columns_lower.get(alias.lower())
            if source is not None:
                rename_map[source] = canonical
                break
    df = df.rename(columns=rename_map).copy()

    if "category_name_cn" not in df.columns and "category_id" in df.columns:
        df["category_name_cn"] = df["category_id"].astype(str)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.normalize()

    if "category_name_cn" in df.columns:
        df["category_name_cn"] = df["category_name_cn"].astype(str).str.strip()

    if "is_activity" in df.columns:
        df["is_activity"] = df["is_activity"].fillna(0).astype(int)

    if required:
        ensure_columns(df, required)
    return df


def ensure_columns(df, required: Iterable[str]) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise SystemExit(f"Missing required columns: {', '.join(missing)}")


def add_calendar_helpers(df, payday_anchor: int = 27):
    pd = load_pandas()
    ensure_columns(df, ["date"])
    df = df.copy()
    df["weekday"] = df["date"].dt.day_name()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["day_of_month"] = df["date"].dt.day
    df["dist2pay"] = df["day_of_month"] - payday_anchor
    month_end = df["date"] + pd.offsets.MonthEnd(0)
    df["is_month_end"] = (df["date"] == month_end).astype(int)
    return df


def safe_ratio(numerator, denominator):
    pd = load_pandas()
    denominator = denominator.replace({0: pd.NA})
    return numerator.divide(denominator)


def winsorize_series(series, pct: float):
    if pct <= 0:
        return series
    lower = series.quantile(pct)
    upper = series.quantile(1 - pct)
    return series.clip(lower=lower, upper=upper)


def summarize_panel(df) -> dict[str, Any]:
    payload = {
        "row_count": int(len(df)),
        "category_count": int(df["category_name_cn"].nunique()) if "category_name_cn" in df.columns else 0,
        "activity_rows": int(df["is_activity"].sum()) if "is_activity" in df.columns else 0,
        "non_activity_rows": int((1 - df["is_activity"]).sum()) if "is_activity" in df.columns else 0,
    }
    if "date" in df.columns and not df.empty:
        payload["date_min"] = str(df["date"].min().date())
        payload["date_max"] = str(df["date"].max().date())
    return payload


def normalize_numeric_columns(df, columns: Iterable[str]):
    pd = load_pandas()
    df = df.copy()
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def choose_available_columns(df, candidates: Iterable[str]) -> list[str]:
    return [column for column in candidates if column in df.columns]


def build_time_folds(df, time_column: str = "month", min_folds: int = 3):
    pd = load_pandas()
    if time_column in df.columns:
        periods = [value for value in sorted(df[time_column].dropna().unique())]
    else:
        periods = [value for value in sorted(df["date"].dt.to_period("M").astype(str).dropna().unique())]
        df = df.copy()
        df[time_column] = df["date"].dt.to_period("M").astype(str)

    if len(periods) < min_folds:
        cutoff_index = max(int(len(df) * 0.7), 1)
        ordered = df.sort_values("date")
        return [(ordered.index[:cutoff_index], ordered.index[cutoff_index:])]

    folds = []
    for index in range(1, len(periods)):
        train_periods = periods[:index]
        test_period = periods[index]
        train_index = df.index[df[time_column].isin(train_periods)]
        test_index = df.index[df[time_column] == test_period]
        if len(train_index) > 0 and len(test_index) > 0:
            folds.append((train_index, test_index))
    return folds
