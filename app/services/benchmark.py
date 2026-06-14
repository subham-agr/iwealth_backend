# app/services/benchmark_service.py

import requests
import pandas as pd
from datetime import datetime, timedelta

BASE_URL = (
    "https://www.nseindia.com/api/"
    "historicalOR/indicesHistory"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
}

def create_nse_session():

    session = requests.Session()

    session.get(
        "https://www.nseindia.com",
        headers=HEADERS,
        timeout=30,
    )

    return session

def fetch_benchmark_payload(
    benchmark_name: str,
    start_date: datetime,
    end_date: datetime,
):
    session = create_nse_session()

    params = {
        "indexType": benchmark_name,
        "from": start_date.strftime("%d-%m-%Y"),
        "to": end_date.strftime("%d-%m-%Y"),
    }

    try:
        response = session.get(
            BASE_URL,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise ValueError(
            f"Unable to fetch benchmark history: {exc}"
        ) from exc

def normalize_benchmark_history(
    payload: dict
) -> pd.DataFrame:

    rows = []

    if "data" not in payload or not isinstance(payload["data"], list):
        raise ValueError(
            f"Unexpected NSE response: {payload}"
        )

    for item in payload["data"]:

        rows.append(
            {
                "date": pd.to_datetime(
                    item["EOD_TIMESTAMP"],
                    format="%d-%b-%Y",
                ),
                "value": float(
                    item["EOD_CLOSE_INDEX_VAL"]
                ),
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values("date")
        .reset_index(drop=True)
    )

def split_date_range(
    start_date,
    end_date,
    chunk_days=365,
):
    ranges = []

    current_start = start_date

    while current_start <= end_date:

        current_end = min(
            current_start + timedelta(days=chunk_days - 1),
            end_date,
        )

        ranges.append(
            (
                current_start,
                current_end,
            )
        )

        current_start = (
            current_end
            + timedelta(days=1)
        )

    return ranges

def get_benchmark_history(
    benchmark_name: str,
    start_date: datetime,
    end_date: datetime,
):
    all_rows = []

    date_ranges = split_date_range(
        start_date,
        end_date,
    )

    for chunk_start, chunk_end in date_ranges:

        payload = fetch_benchmark_payload(
            benchmark_name,
            chunk_start,
            chunk_end,
        )

        if payload.get("error"):
            raise ValueError(
                payload.get(
                    "showMessage",
                    "Benchmark API Error",
                )
            )

        chunk_df = normalize_benchmark_history(
            payload
        )

        all_rows.append(chunk_df)

    if not all_rows:
        return pd.DataFrame(
            columns=[
                "date",
                "value",
            ]
        )

    df = pd.concat(
        all_rows,
        ignore_index=True,
    )

    df = (
        df
        .drop_duplicates(
            subset=["date"]
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    return df