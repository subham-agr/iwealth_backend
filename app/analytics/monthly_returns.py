# app/analytics/monthly_returns.py

import pandas as pd


def calculate_monthly_returns(
    df: pd.DataFrame,
    value_col: str = "nav",
):
    """
    Input:
        date | nav

    Output:
        date | return

    Uses month-end values.
    """

    if df.empty:
        return pd.DataFrame(columns=["date", "return"])

    data = df.copy()

    data["date"] = pd.to_datetime(data["date"])

    data = data.sort_values("date")

    monthly_prices = (
        data.set_index("date")[value_col]
        .resample("ME")
        .last()
    )

    monthly_returns = (
        monthly_prices
        .pct_change()
        .dropna()
    )

    return (
        monthly_returns
        .reset_index(name="return")
    )