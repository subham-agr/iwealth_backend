from app.services.nav_service import get_nav_history
from app.services.benchmark import get_benchmark_history
from app.services.fund_service import get_scheme_by_code
from app.analytics.monthly_returns import calculate_monthly_returns
from app.analytics.capture import calculate_capture_ratios
from app.analytics.returns import (
    calculate_returns_metrics,
    normalized_monthly_series,
)
from app.services.ter import get_fund_ter
from app.analytics.closet_indexer import calculate_closet_indexer_flag


def build_fund_analytics(
    scheme_code: str,
    benchmark_name: str,
    start_date,
    end_date,
):
    fund_df = get_nav_history(
        scheme_code,
        start_date,
        end_date,
    )

    benchmark_df = get_benchmark_history(
        benchmark_name,
        start_date,
        end_date,
    )

    if fund_df.empty or benchmark_df.empty:
        return {
            "error": "No data available for given inputs",
        }

    scheme = get_scheme_by_code(scheme_code)

    fund_metrics = calculate_returns_metrics(
        fund_df.rename(columns={"nav": "nav", "date": "date"})
    )

    benchmark_metrics = calculate_returns_metrics(
        benchmark_df.rename(columns={"value": "nav", "date": "date"}),
        value_col="nav",
    )

    fund_monthly = calculate_monthly_returns(
        fund_df,
        value_col="nav",
    )

    benchmark_monthly = calculate_monthly_returns(
        benchmark_df,
        value_col="value",
    )

    capture = calculate_capture_ratios(
        fund_monthly,
        benchmark_monthly,
    )

    closet_indexer = bool(calculate_closet_indexer_flag(
        fund_monthly,
        benchmark_monthly,
    ))

    ter = get_fund_ter(
        scheme_code,
        start_date,
        end_date,
    )
    
    # Handle case where TER data is not available
    if ter is None:
        ter = {
            "scheme_name": scheme["scheme_name"] if scheme else None,
            "regular_ter": None,
            "direct_ter": None,
            "ter_date": None,
        }

    nav_series = normalized_monthly_series(fund_df, "nav")
    benchmark_series = normalized_monthly_series(
        benchmark_df.rename(columns={"value": "nav"}),
        "nav",
    )

    return {
        "scheme_code": scheme_code,
        "fund_name": scheme["scheme_name"] if scheme else None,
        "benchmark_name": benchmark_name,
        "returns": {
            "1y": fund_metrics["return_1y"],
            "3y": fund_metrics["return_3y"],
            "5y": fund_metrics["return_5y"],
        },
        "rolling_returns": {
            "best": fund_metrics["best"],
            "worst": fund_metrics["worst"],
            "median": fund_metrics["median"],
        },
        "benchmark_returns": {
            "1y": benchmark_metrics["return_1y"],
            "3y": benchmark_metrics["return_3y"],
            "5y": benchmark_metrics["return_5y"],
        },
        "max_drawdown": fund_metrics["max_drawdown"],
        "capture_ratio": capture,
        "closest_indexer": closet_indexer,
        "closet_indexer_details": closet_indexer,
        "ter": ter,
        "nav_series": nav_series,
        "benchmark_series": benchmark_series,
    }
