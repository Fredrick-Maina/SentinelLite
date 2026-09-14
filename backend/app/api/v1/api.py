from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.organizations import router as org_router
from app.api.v1.devices import router as device_router
from app.api.v1.ingest import router as ingest_router
from app.api.v1.alerts import router as alert_router
from app.api.v1.ai import router as ai_router
from app.api.v1.reports import router as report_router
from app.api.v1.audit import router as audit_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(org_router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(device_router, tags=["Devices"])
api_router.include_router(ingest_router, prefix="/ingest", tags=["Ingestion"])
api_router.include_router(alert_router, tags=["Alerts"])
api_router.include_router(ai_router, tags=["AI Security Analyst"])
api_router.include_router(report_router, tags=["Reports"])
api_router.include_router(audit_router, tags=["Audit Logs"])
