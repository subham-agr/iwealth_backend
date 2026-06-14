def parse_mcwb_csv(path):
    df = pd.read_csv(path)

    industry_col = (
        "Basic Industry"
        if "Basic Industry" in df.columns
        else "Industry"
    )

    market_cap_col = next(
        col
        for col in df.columns
        if "Market Capitalisation" in col
    )

    df = df[
        df["Security Symbol"] != "DUMMY"
    ]

    return pd.DataFrame(
        {
            "symbol": df["Security Symbol"],
            "name": df["Security Name"],
            "industry": df[industry_col],
            "market_cap": df[market_cap_col],
            "weight": df["Weightage (%)"],
        }
    )