import pandas as pd
import numpy as np


def calculate_closet_indexer_flag(
    fund_monthly: pd.DataFrame,
    benchmark_monthly: pd.DataFrame,
):
    merged = fund_monthly.merge(
        benchmark_monthly,
        on="date",
        suffixes=("_fund", "_benchmark"),
    ).dropna()

    if merged.empty:
        return {
            "is_closet_indexer": None,
            "correlation": None,
            "tracking_error": None,
            "active_return": None,
        }

    # Excess return
    merged["active"] = (
        merged["return_fund"]
        - merged["return_benchmark"]
    )

    # Correlation
    correlation = merged["return_fund"].corr(
        merged["return_benchmark"]
    )

    # Tracking error (annualized-ish approximation)
    tracking_error = merged["active"].std()

    # Active return
    active_return = merged["active"].mean()

    # Decision rules (tunable thresholds)
    is_closet_indexer = (
        correlation is not None
        and correlation > 0.95
        and abs(active_return) < 0.002
        and tracking_error < 0.01
    )

    return {
        "is_closet_indexer": is_closet_indexer,
        "correlation": (
            round(float(correlation), 4)
            if correlation is not None
            else None
        ),
        "tracking_error": round(
            float(tracking_error), 6
        ),
        "active_return": round(
            float(active_return), 6
        ),
    }