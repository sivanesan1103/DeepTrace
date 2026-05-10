from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import report

app = FastAPI(
    title="DeepTrace Report Service",
    description="Report generation service with PDF export",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(report.router, prefix="/report", tags=["report"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "report"}