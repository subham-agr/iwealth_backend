# app/services/amfi.py

import requests
from datetime import datetime

NAV_HISTORY_URL = (
    "http://portal.amfiindia.com/"
    "DownloadNAVHistoryReport_Po.aspx"
)

AMFI_NAV_ALL_URL = "https://www.amfiindia.com/spages/NAVAll.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def fetch_nav_all() -> str:
    """
    Returns raw NAVAll.txt content.
    """

    response = requests.get(
        AMFI_NAV_ALL_URL,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return response.text
    
def fetch_nav_history_chunk(
    start_date: datetime,
    end_date: datetime,
) -> str:

    params = {
        "frmdt": start_date.strftime("%d-%b-%Y"),
        "todt": end_date.strftime("%d-%b-%Y"),
    }

    response = requests.get(
        NAV_HISTORY_URL,
        params=params,
        headers=HEADERS,
        timeout=60,
    )

    response.raise_for_status()

    return response.text

def fetch_test_history():
    params = {
        "frmdate": "01-Apr-2025",
        "rpt": "0"
    }

    response = requests.get(
        NAV_HISTORY_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text