# app/utils/parsers.py

from typing import List, Dict
import pandas as pd


def parse_nav_all(raw_text: str) -> List[Dict]:
    """
    Parse NAVAll.txt into a list of schemes.
    """

    schemes = []

    current_category = None

    for line in raw_text.splitlines():

        line = line.strip()

        if line.startswith("Scheme Code"):
            continue

        if not line:
            continue

        if ";" not in line:
            current_category = line
            continue

        parts = line.split(";")

        if len(parts) < 5:
            continue

        schemes.append(
            {
                "scheme_code": parts[0].strip(),
                "scheme_name": parts[3].strip(),
                "nav": parts[4].strip(),
                "category": current_category,
            }
        )

    return schemes

def parse_nav_history(
    raw_text: str,
):
    records = []

    for line in raw_text.splitlines():

        parts = line.split(";")

        if len(parts) != 5:
            continue

        try:

            records.append(
                {
                    "scheme_code": parts[0].strip(),
                    "scheme_name": parts[1].strip(),
                    "isin": parts[2].strip(),
                    "nav": float(parts[3]),
                    "date": pd.to_datetime(parts[4]),
                }
            )

        except:
            continue

    return pd.DataFrame(records)