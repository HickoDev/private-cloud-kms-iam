from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.audit.router import router as audit_router
from app.auth.router import router as auth_router
from app.core.config import get_settings
from app.iam.router import router as iam_router
from app.kms.router import router as kms_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Academic KMS integrated with a mini-IAM for a private cloud.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(iam_router, prefix="/api", tags=["IAM"])
app.include_router(kms_router, prefix="/api/keys", tags=["KMS"])
app.include_router(audit_router, prefix="/api/audit-logs", tags=["Audit Logs"])

