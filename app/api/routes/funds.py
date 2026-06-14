from datetime import date

from fastapi import APIRouter, HTTPException, Query
from app.services.nav_service import get_nav_history
from app.services.fund_service import get_all_funds, search_funds

router = APIRouter(prefix="/funds", tags=["funds"])


@router.get("/")
def list_funds():
    return get_all_funds()


@router.get("/search")
def search(keyword: str):
    return search_funds(keyword)


@router.get("/{scheme_code}/history")
def fund_history(
    scheme_code: str,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be on or before end_date",
        )

    try:
        df = get_nav_history(
            scheme_code,
            start_date,
            end_date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="No NAV history found for the given scheme and date range",
        )

    return {
        "rows": len(df),
        "start_date": str(df["date"].min().date()),
        "end_date": str(df["date"].max().date()),
        "latest_nav": float(df.iloc[-1]["nav"]),
        "history": df.to_dict(orient="records"),
    }
