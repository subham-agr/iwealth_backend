# app/services/fund_service.py

from app.services.amfi import fetch_nav_all
from app.utils.parsers import parse_nav_all
from functools import lru_cache

@lru_cache(maxsize=1)
def get_all_funds():

    raw_data = fetch_nav_all()

    return parse_nav_all(raw_data)

def get_scheme_by_code(
    scheme_code: str,
):
    schemes = get_all_funds()

    for scheme in schemes:
        if str(scheme["scheme_code"]) == str(scheme_code):
            print(f"Found scheme for code {scheme_code}: {scheme['scheme_name']}")
            return {
                "scheme_code": scheme["scheme_code"],
                "scheme_name": scheme["scheme_name"],
                "category": scheme.get("category"),
                "nav": scheme.get("nav"),
            }

    return None

def get_scheme_by_name(
    scheme_name: str,
):
    schemes = get_all_funds()

    for scheme in schemes:
        if (
            scheme["scheme_name"].lower()
            == scheme_name.lower()
        ):
            return scheme

    return None

def search_funds(keyword: str):

    keyword = keyword.lower()

    funds = get_all_funds()

    return [
        fund
        for fund in funds
        if keyword in fund["scheme_name"].lower()
    ]
