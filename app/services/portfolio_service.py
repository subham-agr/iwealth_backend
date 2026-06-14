from datetime import date

from app.services.fund_analytics import build_fund_analytics
from app.services.fund_service import get_scheme_by_code

DEMO_PORTFOLIO = [
    {
        "scheme_code": "122639",
        "weight": 0.40,
        "benchmark_name": "NIFTY 500",
        "asset_class": "Equity",
    },
    {
        "scheme_code": "120503",
        "weight": 0.30,
        "benchmark_name": "NIFTY 100",
        "asset_class": "Equity",
    },
    {
        "scheme_code": "119551",
        "weight": 0.20,
        "benchmark_name": "NIFTY 100",
        "asset_class": "Debt",
    },
    {
        "scheme_code": "cash",
        "weight": 0.10,
        "benchmark_name": "NIFTY 100",
        "asset_class": "Cash",
    },
]

DEMO_TOTAL_VALUE = 1_245_000


def _risk_label(max_drawdown: float | None) -> str:
    if max_drawdown is None:
        return "Unknown"

    if max_drawdown > -10:
        return "Low"
    if max_drawdown > -20:
        return "Medium"
    return "High"


def build_portfolio_overview(
    start_date: date,
    end_date: date,
):
    holdings = []
    allocation_map: dict[str, float] = {}
    weighted_return_1y = 0.0
    weighted_benchmark_1y = 0.0
    valid_weights = 0.0
    insights: list[str] = []

    for item in DEMO_PORTFOLIO:
        weight = item["weight"]
        asset_class = item["asset_class"]
        allocation_map[asset_class] = (
            allocation_map.get(asset_class, 0) + weight * 100
        )

        if item["scheme_code"] == "cash":
            holdings.append(
                {
                    "scheme_code": "cash",
                    "scheme_name": "Cash / Liquid",
                    "allocation_pct": round(weight * 100, 1),
                    "return_1y": 5.0,
                    "contribution_pct": round(5.0 * weight, 2),
                    "risk": "Low",
                    "asset_class": asset_class,
                }
            )
            weighted_return_1y += 5.0 * weight
            weighted_benchmark_1y += 5.0 * weight
            valid_weights += weight
            continue

        scheme = get_scheme_by_code(item["scheme_code"])
        analytics = build_fund_analytics(
            scheme_code=item["scheme_code"],
            benchmark_name=item["benchmark_name"],
            start_date=start_date,
            end_date=end_date,
        )

        if analytics.get("error"):
            continue

        return_1y = analytics["returns"].get("1y") or 0
        benchmark_1y = analytics["benchmark_returns"].get("1y") or 0
        max_dd = analytics.get("max_drawdown")

        holdings.append(
            {
                "scheme_code": item["scheme_code"],
                "scheme_name": scheme["scheme_name"]
                if scheme
                else analytics.get("fund_name", "Unknown Fund"),
                "allocation_pct": round(weight * 100, 1),
                "return_1y": return_1y,
                "contribution_pct": round(return_1y * weight, 2),
                "risk": _risk_label(max_dd),
                "asset_class": asset_class,
                "max_drawdown": max_dd,
            }
        )

        weighted_return_1y += return_1y * weight
        weighted_benchmark_1y += benchmark_1y * weight
        valid_weights += weight

    if valid_weights == 0:
        return {"error": "Unable to build portfolio overview"}

    portfolio_return_1y = round(weighted_return_1y / valid_weights, 2)
    portfolio_benchmark_1y = round(
        weighted_benchmark_1y / valid_weights,
        2,
    )
    alpha = round(portfolio_return_1y - portfolio_benchmark_1y, 2)

    equity_pct = allocation_map.get("Equity", 0)
    if equity_pct >= 70:
        insights.append(
            "Your portfolio is mostly in equity funds, which can grow faster but may swing more in the short term."
        )
    elif equity_pct >= 40:
        insights.append(
            "Your portfolio has a balanced mix of equity and safer assets."
        )
    else:
        insights.append(
            "Your portfolio leans toward safer assets, which may grow slower but feel steadier."
        )

    if alpha > 0:
        insights.append(
            f"Over the past year, your portfolio beat its benchmark by about {alpha}% — a positive sign."
        )
    elif alpha < 0:
        insights.append(
            f"Over the past year, your portfolio trailed its benchmark by about {abs(alpha)}%."
        )
    else:
        insights.append(
            "Your portfolio matched its benchmark over the past year."
        )

    high_risk = [h for h in holdings if h["risk"] == "High"]
    if high_risk:
        insights.append(
            f"{high_risk[0]['scheme_name']} has seen larger drops — it contributes most to portfolio ups and downs."
        )

    allocation = [
        {"name": name, "value": round(value, 1)}
        for name, value in allocation_map.items()
    ]

    overall_risk = _risk_label(
        min(
            [
                h.get("max_drawdown", 0)
                for h in holdings
                if h["scheme_code"] != "cash"
            ],
            default=-15,
        )
        if any(h["scheme_code"] != "cash" for h in holdings)
        else -5
    )

    return {
        "total_value": DEMO_TOTAL_VALUE,
        "return_1y": portfolio_return_1y,
        "benchmark_return_1y": portfolio_benchmark_1y,
        "alpha": alpha,
        "risk_level": overall_risk,
        "allocation": allocation,
        "holdings": holdings,
        "insights": insights,
    }
