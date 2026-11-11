import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.common.errors import DomainError
from app.common.middleware import SecurityHeadersMiddleware, TenantScopeMiddleware

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

app = FastAPI(
    title="MediClaim AI",
    version="0.1.0",
    docs_url="/docs" if settings.DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.DOCS_ENABLED else None,
    openapi_url="/openapi.json" if settings.DOCS_ENABLED else None,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TenantScopeMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status,
        content={
            "type": f"https://mediclaim.ai/errors/{exc.code}",
            "title": exc.title,
            "status": exc.status,
            "detail": exc.detail,
            "instance": str(request.url.path),
        },
    )


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/readyz")
async def readyz():
    # minimal; detailed checks added per module
    return {"status": "ready"}


from contextlib import asynccontextmanager

from app.db import SessionLocal

# Routers
from app.auth.router import router as auth_router
from app.claims.router import router as claims_router
from app.audit.router import router as audit_router, admin_router as audit_admin_router
from app.reporting.router import router as reporting_router
from app.admin.router import router as admin_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(claims_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(audit_admin_router, prefix="/api/v1")
app.include_router(reporting_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


@asynccontextmanager
async def lifespan(app):
    async with SessionLocal() as session:
        from app.auth.bootstrap import bootstrap

        await bootstrap(session)
    yield


app.router.lifespan_context = lifespan
