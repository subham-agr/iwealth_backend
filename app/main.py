from fastapi import FastAPI
from app.api.routes import health, funds, benchmarks, analytics
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="iWealth Fund Analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React dev server
        "https://iwealthfund.netlify.app",  # Deployed frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(funds.router)
app.include_router(benchmarks.router)
app.include_router(analytics.router)