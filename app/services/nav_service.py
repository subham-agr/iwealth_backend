# app/services/nav_service.py

import requests
import pandas as pd


MFAPI_BASE_URL = "https://api.mfapi.in/mf"

def fetch_nav_payload(
    scheme_code: str
) -> dict:
    try:
        response = requests.get(
            f"{MFAPI_BASE_URL}/{scheme_code}",
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise ValueError(
            f"Unable to fetch NAV history: {exc}"
        ) from exc

def normalize_nav_history(
    payload: dict
) -> pd.DataFrame:

    try:
        df = pd.DataFrame(
            payload["data"]
        )
    except Exception as exc:
        raise ValueError(
            "Unexpected NAV payload format"
        ) from exc

    df["date"] = pd.to_datetime(
        df["date"],
        dayfirst=True,
    )

    df["nav"] = pd.to_numeric(
        df["nav"],
        errors="coerce",
    )

    return (
        df[["date", "nav"]]
        .dropna()
        .sort_values("date")
        .reset_index(drop=True)
    )

def validate_nav_history(
    df: pd.DataFrame
):

    if df.empty:
        raise ValueError(
            "No NAV history found"
        )

    if df["date"].duplicated().any():
        raise ValueError(
            "Duplicate NAV dates detected"
        )

    if not df["date"].is_monotonic_increasing:
        raise ValueError(
            "Dates not sorted"
        )

    return True

def get_nav_history(
    scheme_code: str,
    start_date=None,
    end_date=None,
):
    payload = fetch_nav_payload(
        scheme_code
    )

    if payload.get("status") != "SUCCESS":
        raise ValueError(
            "Unable to fetch NAV history"
        )

    df = normalize_nav_history(
        payload
    )

    if start_date:
        df = df[
            df["date"] >= pd.Timestamp(
                start_date
            )
        ]

    if end_date:
        df = df[
            df["date"] <= pd.Timestamp(
                end_date
            )
        ]

    validate_nav_history(df)
    
    return df