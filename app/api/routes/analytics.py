from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.services.fund_analytics import build_fund_analytics
from app.services.compare_service import build_fund_comparison
from app.services.portfolio_service import build_portfolio_overview

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


def _validate_date_range(start_date: date, end_date: date):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be on or before end_date",
        )


@router.get("/fund")
def fund_analytics(
    scheme_code: str,
    benchmark_name: str,
    start_date: date,
    end_date: date,
):
    _validate_date_range(start_date, end_date)

    result = build_fund_analytics(
        scheme_code=scheme_code,
        benchmark_name=benchmark_name,
        start_date=start_date,
        end_date=end_date,
    )

    if result.get("error"):
        raise HTTPException(
            status_code=404,
            detail=result["error"],
        )

    return result


@router.get("/compare")
def compare_funds(
    scheme_codes: str = Query(
        ...,
        description="Comma-separated scheme codes, e.g. 122639,120503",
    ),
    benchmark_name: str = "NIFTY 100",
    start_date: date = date(2021, 1, 1),
    end_date: date = date(2025, 6, 1),
):
    _validate_date_range(start_date, end_date)

    codes = [code.strip() for code in scheme_codes.split(",") if code.strip()]

    if not codes:
        raise HTTPException(
            status_code=400,
            detail="At least one scheme_code is required",
        )

    return build_fund_comparison(
        scheme_codes=codes,
        benchmark_name=benchmark_name,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/portfolio/demo")
def demo_portfolio(
    start_date: date = date(2021, 1, 1),
    end_date: date = date(2025, 6, 1),
):
    _validate_date_range(start_date, end_date)

    result = build_portfolio_overview(
        start_date=start_date,
        end_date=end_date,
    )

    if result.get("error"):
        raise HTTPException(
            status_code=400,
            detail=result["error"],
        )

    return result
