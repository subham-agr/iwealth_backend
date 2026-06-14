# app/api/benchmarks.py

from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.services.benchmark import get_benchmark_history

router = APIRouter(
    prefix="/benchmarks",
    tags=["benchmarks"],
)


@router.get("/history")
def benchmark_history(
    benchmark_name: str = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be on or before end_date",
        )

    try:
        df = get_benchmark_history(
            benchmark_name=benchmark_name,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="No benchmark history available for the given input",
        )

    return {
        "benchmark": benchmark_name,
        "rows": len(df),
        "start_date": str(df["date"].min().date()),
        "end_date": str(df["date"].max().date()),
        "latest_value": float(df.iloc[-1]["value"]),
        "history": df.to_dict(orient="records"),
    }
