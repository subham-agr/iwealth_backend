import pandas as pd


def prepare_timeseries(df, date_col, value_col):
    df = df[[date_col, value_col]].copy()

    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)

    df = df.dropna()

    return df


def align_on_benchmark_dates(
    fund_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    fund_date_col="date",
    benchmark_date_col="date",
    fund_value_col="value",
    benchmark_value_col="value",
):
    """
    Align fund NAV to benchmark dates using as-of merge.
    """

    fund_df = prepare_timeseries(
        fund_df,
        fund_date_col,
        fund_value_col,
    )

    benchmark_df = prepare_timeseries(
        benchmark_df,
        benchmark_date_col,
        benchmark_value_col,
    )

    fund_df = fund_df.rename(
        columns={
            fund_date_col: "date",
            fund_value_col: "fund_value",
        }
    )

    benchmark_df = benchmark_df.rename(
        columns={
            benchmark_date_col: "date",
            benchmark_value_col: "benchmark_value",
        }
    )

    merged = pd.merge_asof(
        benchmark_df,
        fund_df,
        on="date",
        direction="backward",  # KEY: use last available NAV
    )

    merged = merged.dropna()

    return merged