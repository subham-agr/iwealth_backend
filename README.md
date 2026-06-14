# iWealth Backend - Fund Analytics API

FastAPI backend for mutual fund analytics using AMFI NAV, benchmark history, and TER data.

## Quick Start (< 5 minutes)

### Prerequisites
- Python 3.9+
- pip

### Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` for interactive API documentation.

### Test API

```bash
curl "http://localhost:8000/analytics/fund?scheme_code=122639&benchmark_name=NIFTY%20100&start_date=2023-01-01&end_date=2023-12-31"

curl "http://localhost:8000/analytics/compare?scheme_codes=122639,106956&benchmark_name=NIFTY%20100"
```

## Design documents

For architecture, frontend flow, and AI-layer design, see:
- `docs/Part4_Design_Document.md`
- `docs/Section3.md`

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI entry point
│   ├── analytics/                   # Metric computations
│   │   ├── capture.py              # Upside/downside capture ratio
│   │   ├── closet_indexer.py       # Closet indexer detection
│   │   ├── monthly_returns.py      # Rolling return analysis
│   │   └── returns.py              # CAGR & return metrics
│   ├── api/
│   │   └── routes/
│   │       ├── analytics.py        # /analytics/* endpoints
│   │       ├── benchmarks.py       # /benchmarks/* endpoints
│   │       └── funds.py            # /funds/* endpoints
│   ├── services/                    # Data fetching & processing
│   │   ├── amfi.py                 # AMFI NAV All parser
│   │   ├── benchmark.py            # Benchmark data (MCWB)
│   │   ├── fund_service.py         # Fund registry & lookup
│   │   ├── mcwb_service.py         # Stock price (bhavcopy)
│   │   ├── nav_service.py          # NAV history fetching
│   │   ├── ter.py                  # TER (expense ratio) data
│   │   └── portfolio_service.py    # Portfolio analytics
│   ├── models/
│   │   └── schemas.py              # Pydantic response schemas
│   ├── core/
│   │   ├── config.py               # Settings & constants
│   │   └── funds.py                # Fund registry
│   ├── utils/
│   │   ├── align_dates.py          # Date alignment utilities
│   │   ├── date_utils.py           # Date helper functions
│   │   └── parsers.py              # Data parser utilities
│   └── data/
│       ├── raw/                    # Original API responses
│       ├── processed/              # Cleaned & aligned data
│       └── cache/                  # Temporary aggregations
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## API Endpoints

### Fund Analytics

```
GET /analytics/fund
Parameters:
  - scheme_code: str      AMFI scheme code (e.g., "122639")
  - benchmark_name: str   Benchmark index (e.g., "NIFTY 100")
  - start_date: date      Start date (YYYY-MM-DD)
  - end_date: date        End date (YYYY-MM-DD)

Returns: Fund metrics (returns, capture ratio, TER, closet indexer flag)
```

### Fund Comparison

```
GET /analytics/compare
Parameters:
  - scheme_codes: str     Comma-separated codes (e.g., "122639,106956")
  - benchmark_name: str   Benchmark index
  - start_date: date      Start date
  - end_date: date        End date

Returns: Array of fund metrics + NAV chart data
```

### Portfolio Overview

```
GET /analytics/portfolio/demo
Parameters:
  - start_date: date      Start date
  - end_date: date        End date

Returns: Demo portfolio with allocation, holdings, and insights
```

---

## Metrics Explained

### Returns
- **1Y, 3Y, 5Y CAGR**: Annualized growth rates
- **Rolling Returns**: Best, worst, median returns over rolling 12-month windows

### Capture Ratios
- **Upside Capture**: How much of the market's gains the fund captured
- **Downside Capture**: How much of the market's losses the fund absorbed
- **Interpretation**: 90% upside / 70% downside = good (captures gains, limits losses)

### Closet Indexer Flag
- **Definition**: Fund's 3-year correlation with benchmark ≥ 0.90
- **Meaning**: Fund charges active management fees but just tracks the market
- **Action**: Consider low-cost index fund instead

### TER (Total Expense Ratio)
- **Direct Plan**: Fee if buying directly from AMC
- **Regular Plan**: Fee if buying through advisor/distributor
- **Example**: 0.25% = ₹25 annual charge per ₹10,000 invested

---

## Data Sources

All data from official regulatory sources:

1. **NAV History**: AMFI Portal
   - http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx
   - Daily NAV for all active funds

2. **Benchmarks**: Nifty Indices (MCWB reports)
   - niftyindices.com
   - Monthly constituent weights

3. **Stock Prices**: NSE Bhavcopy
   - https://nsearchives.nseindia.com/
   - Daily OHLCV data

4. **Fund Registry**: AMFI NAVAll
   - https://www.amfiindia.com/spages/NAVAll.txt
   - Scheme codes, names, categories

5. **TER Data**: AMFI TER API
   - https://www.amfiindia.com/api/populate-te-rdata-revised
   - Monthly expense ratio updates

---

## Configuration

Edit `app/core/config.py` to customize:

```python
# Data cache TTL (seconds)
CACHE_TTL = 86400  # 24 hours

# API timeout (seconds)
REQUEST_TIMEOUT = 60

# Supported benchmarks
SUPPORTED_BENCHMARKS = ["NIFTY 50", "NIFTY 100", "NIFTY 200", "NIFTY 500"]

# Default date range
DEFAULT_START_DATE = "2021-01-01"
DEFAULT_END_DATE = "2024-12-31"
```

---

## Supported Funds

### Large Cap
- ICICI Prudential Nifty 50 Index Fund (122639)
- SBI Bluechip Fund

### Midcap
- Axis Mid-Cap Fund (106956)
- ICICI Prudential Multicap Growth Fund

### Debt/Hybrid
- Aditya Birla Sun Life Banking & PSU Debt Fund (119551)
- HDFC Corporate Bond Fund

Add more funds by updating `app/core/funds.py`

---

## Error Handling

### Common Errors

```
"error": "Fund not found"
→ Scheme code doesn't exist in AMFI registry
→ Check code format (numeric string)

"error": "No data available for given inputs"
→ Date range outside available history (back to 2006)
→ Fund inactive during requested period

"error": "Benchmark not available"
→ Use supported benchmarks: NIFTY 50, NIFTY 100, etc.
```

### Graceful Degradation

- **TER unavailable**: Endpoint returns `ter: { ..., direct_ter: null, regular_ter: null }`
- **Benchmark missing**: Returns `alpha: null` instead of crashing
- **Partial data**: Uses available data and logs warnings

---

## Development

### Running Tests

```bash
pytest tests/
pytest tests/test_analytics.py -v
pytest tests/test_ter.py -v
```

### Debug Mode

```bash
# Run with debug logs
DEBUG=true python -m uvicorn app.main:app --reload --log-level debug
```

### Code Quality

```bash
# Format code
black app/

# Lint
pylint app/

# Type checking
mypy app/
```

---

## Performance Notes

### Caching
- NAV data cached for 24 hours (after first fetch)
- TER data cached by month to avoid duplicate API calls
- Benchmark indices cached per date

### Optimization Tips
- Use date ranges ≤ 1 year for faster response
- Reuse cached data (don't refetch same dates)
- Batch fund comparisons rather than individual queries

### Load Testing
```bash
# Test with 100 concurrent requests
apache2-bench -n 100 -c 10 http://localhost:8000/analytics/fund?scheme_code=122639&benchmark_name=NIFTY%20100&start_date=2023-01-01&end_date=2023-12-31
```

---

## Troubleshooting

### ImportError: No module named 'pandas'
```bash
pip install -r requirements.txt
```

### Connection refused (127.0.0.1:8000)
- Check if server is running: `ps aux | grep uvicorn`
- Restart: `Ctrl+C` and run `python -m uvicorn app.main:app --reload`

### "Module 'app' not found"
```bash
# Run from backend directory
cd backend
python -m uvicorn app.main:app --reload
```

### TER returns null
- AMFI API may not have data for requested month
- Falls back to previous month automatically
- Frontend displays "—" if unavailable

---

## Additional Resources

- **API Docs**: http://localhost:8000/docs (Swagger/OpenAPI)
- **Design Document**: See `DESIGN_DOCUMENT.md`
- **Frontend Integration**: See `../frontend/`
- **AMFI Official**: https://www.amfiindia.com

---

## License

Internal - iWealth Platform

---

## Support

For issues or questions:
1. Check `DESIGN_DOCUMENT.md` for detailed specs
2. Review inline code comments in `app/analytics/`
3. Check API response format in `app/models/schemas.py`
4. Review test cases in `tests/`

## AI Usage
- The helper functions and all logical functions is built using ChatGPT step by step to verify and create the data flow logic
- Cursor is used to add additional error handling and simplification changes