from datetime import timedelta
import pandas as pd
import numpy as np


def absolute_return(
    start_value: float,
    end_value: float,
) -> float:
    return (
        (end_value - start_value)
        / start_value
    ) * 100


def cagr(
    start_value: float,
    end_value: float,
    years: float,
) -> float:
    return (
        (
            end_value / start_value
        ) ** (1 / years)
        - 1
    ) * 100


def trailing_return(
    df: pd.DataFrame,
    years: int,
    value_col: str = "nav",
):
    latest_date = df["date"].max()

    target_date = (
        latest_date
        - pd.DateOffset(years=years)
    )

    historical = df[
        df["date"] <= target_date
    ]

    if historical.empty:
        return None

    start_value = historical.iloc[-1][value_col]

    end_value = df.iloc[-1][value_col]

    if years == 1:
        return round(
            absolute_return(
                start_value,
                end_value,
            ),
            2,
        )

    return round(
        cagr(
            start_value,
            end_value,
            years,
        ),
        2,
    )


def rolling_12m_returns(
    df: pd.DataFrame,
    value_col: str = "nav",
):
    returns = []

    for idx in range(len(df)):
        start_date = df.iloc[idx]["date"]

        target_date = (
            start_date
            + pd.DateOffset(years=1)
        )

        future = df[
            df["date"] >= target_date
        ]

        if future.empty:
            continue

        start_value = df.iloc[idx][value_col]

        end_value = future.iloc[0][value_col]

        ret = (
            (end_value - start_value)
            / start_value
        ) * 100

        returns.append(ret)

    return returns


def rolling_summary(
    df: pd.DataFrame,
    value_col: str = "nav",
):
    returns = rolling_12m_returns(
        df,
        value_col=value_col,
    )

    if not returns:
        return {
            "best": None,
            "worst": None,
            "median": None,
        }

    return {
        "best": round(max(returns), 2),
        "worst": round(min(returns), 2),
        "median": round(
            float(np.median(returns)),
            2,
        ),
    }


def max_drawdown(
    df: pd.DataFrame,
    value_col: str = "nav",
) -> float | None:
    prices = df.sort_values("date")[value_col]
    if prices.empty:
        return None

    rolling_max = prices.cummax()
    drawdowns = (prices - rolling_max) / rolling_max * 100

    return round(float(drawdowns.min()), 2)


def normalized_monthly_series(
    df: pd.DataFrame,
    value_col: str = "nav",
):
    if df.empty:
        return []

    monthly = (
        df.set_index("date")[value_col]
        .resample("ME")
        .last()
        .dropna()
    )

    if monthly.empty:
        return []

    base = monthly.iloc[0]

    return [
        {
            "date": date.strftime("%Y-%m"),
            "value": round(float(value / base * 100), 2),
        }
        for date, value in monthly.items()
    ]


def calculate_returns_metrics(
    df: pd.DataFrame,
    value_col: str = "nav",
):
    df = df.sort_values("date").reset_index(drop=True)
    return {
        "return_1y": trailing_return(
            df,
            1,
            value_col,
        ),
        "return_3y": trailing_return(
            df,
            3,
            value_col,
        ),
        "return_5y": trailing_return(
            df,
            5,
            value_col,
        ),
        "max_drawdown": max_drawdown(
            df,
            value_col,
        ),
        **rolling_summary(
            df,
            value_col,
        ),
    }