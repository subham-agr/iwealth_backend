import pandas as pd
import numpy as np


def _compound_return(series):
    return (np.prod(1 + series) - 1)


def calculate_capture_ratios(
    fund_monthly: pd.DataFrame,
    benchmark_monthly: pd.DataFrame,
):
    merged = fund_monthly.merge(
        benchmark_monthly,
        on="date",
        suffixes=("_fund", "_benchmark"),
    )

    if merged.empty:
        return {
            "upside_capture": None,
            "downside_capture": None,
        }

    upside = merged[
        merged["return_benchmark"] > 0
    ]

    downside = merged[
        merged["return_benchmark"] < 0
    ]

    def ratio(fund, bench):
        if len(bench) == 0:
            return None

        bench_ret = _compound_return(
            bench
        )
        fund_ret = _compound_return(
            fund
        )

        if bench_ret == 0:
            return None

        return fund_ret / bench_ret

    upside_capture = ratio(
        upside["return_fund"],
        upside["return_benchmark"],
    )

    downside_capture = ratio(
        downside["return_fund"],
        downside["return_benchmark"],
    )

    return {
        "upside_capture": (
            round(float(upside_capture), 4)
            if upside_capture is not None
            else None
        ),
        "downside_capture": (
            round(float(downside_capture), 4)
            if downside_capture is not None
            else None
        ),
    }