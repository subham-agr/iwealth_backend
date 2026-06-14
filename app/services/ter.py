import pandas as pd
import requests

from io import BytesIO
from functools import lru_cache

from app.services.fund_service import get_scheme_by_code

headers = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7)"
        " AppleWebKit/537.36"
    )
}

TER_CACHE = {}

@lru_cache(maxsize=24)
def fetch_ter_data(month: str):
    """Fetch TER data for a specific month. Month format: MM-YYYY (e.g., 06-2026)"""
    url = "https://www.amfiindia.com/api/populate-te-rdata-revised"
    
    try:
        response = requests.get(
            url,
            params={
                "MF_ID": "All",
                "Month": month,
                "strCat": "-1",
                "strType": "-1",
                "excel": "true",
            },
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()
        
        df = pd.read_excel(BytesIO(response.content))
        # Remove rows where Scheme Name is NaN or contains metadata
        df = df.dropna(subset=["Scheme Name"])
        df = df[df["Scheme Name"].apply(lambda x: isinstance(x, str))]
        
        return df
    except Exception as e:
        print(f"Error fetching TER for {month}: {e}")
        return pd.DataFrame()

def get_ter_dataset(months):
    """Get TER dataset for multiple months"""
    key = tuple(sorted(months))
    
    if key in TER_CACHE:
        return TER_CACHE[key]
    
    dfs = [fetch_ter_data(m) for m in months if fetch_ter_data(m) is not None]
    dfs = [df for df in dfs if not df.empty]
    
    if not dfs:
        return pd.DataFrame()
    
    df = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["NSDL Scheme Code", "TER Date"])
    df["TER Date"] = pd.to_datetime(df["TER Date"])
    
    TER_CACHE[key] = df
    return df

def normalize_scheme_name(scheme_name: str):
    """Normalize scheme name by removing suffixes"""
    return scheme_name.split(" - ")[0].strip()

def get_fund_ter(scheme_code: str, start_date, end_date):
    """Get TER data for a fund based on end_date"""
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Fetch TER data for end month and previous month
    end_month = end_date.strftime("%m-%Y")
    prev_month = (end_date - pd.DateOffset(months=1)).strftime("%m-%Y")
    
    df = get_ter_dataset([end_month, prev_month])
    if df.empty:
        return None

    # Get scheme info
    scheme = get_scheme_by_code(scheme_code)
    if not scheme:
        return None

    base_name = normalize_scheme_name(scheme["scheme_name"])

    # Search for scheme in TER data
    mask = df["Scheme Name"].str.lower().str.contains(base_name.lower(), case=False, na=False, regex=False)
    matches = df.loc[mask]
    
    if matches.empty:
        return None

    # Get latest TER record
    latest = matches.sort_values("TER Date").iloc[-1]

    return {
        "scheme_name": latest["Scheme Name"],
        "regular_ter": float(latest.get("Regular Plan - Total TER (%)", None)),
        "direct_ter": float(latest.get("Direct Plan - Total TER (%)", None)),
        "ter_date": str(latest["TER Date"]),
    }