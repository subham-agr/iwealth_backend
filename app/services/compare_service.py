from datetime import date

from app.services.fund_analytics import build_fund_analytics
from app.services.fund_service import get_scheme_by_code
from app.services.nav_service import get_nav_history
from app.analytics.returns import normalized_monthly_series


def build_fund_comparison(
    scheme_codes: list[str],
    benchmark_name: str,
    start_date: date,
    end_date: date,
):
    funds = []

    for scheme_code in scheme_codes:
        scheme = get_scheme_by_code(scheme_code)
        analytics = build_fund_analytics(
            scheme_code=scheme_code,
            benchmark_name=benchmark_name,
            start_date=start_date,
            end_date=end_date,
        )

        if analytics.get("error"):
            funds.append(
                {
                    "scheme_code": scheme_code,
                    "scheme_name": scheme["scheme_name"]
                    if scheme
                    else scheme_code,
                    "error": analytics["error"],
                }
            )
            continue

        nav_df = get_nav_history(
            scheme_code,
            start_date,
            end_date,
        )
        nav_series = normalized_monthly_series(nav_df, "nav")

        funds.append(
            {
                "scheme_code": scheme_code,
                "scheme_name": scheme["scheme_name"]
                if scheme
                else analytics.get("fund_name", scheme_code),
                "returns": analytics["returns"],
                "benchmark_returns": analytics["benchmark_returns"],
                "max_drawdown": analytics.get("max_drawdown"),
                "ter": analytics["ter"],
                "nav_series": nav_series,
            }
        )

    nav_chart = _merge_nav_series(funds)

    return {
        "benchmark_name": benchmark_name,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "funds": funds,
        "nav_chart": nav_chart,
    }


def _merge_nav_series(funds: list[dict]):
    chart: dict[str, dict] = {}

    for index, fund in enumerate(funds):
        if fund.get("error"):
            continue

        key = f"fund_{index}"
        for point in fund.get("nav_series", []):
            date_key = point["date"]
            if date_key not in chart:
                chart[date_key] = {"date": date_key}
            chart[date_key][key] = point["value"]

    return sorted(chart.values(), key=lambda row: row["date"])
