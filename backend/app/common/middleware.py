from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        csp = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; font-src 'self'; connect-src 'self' https://api.openai.com; "
            "object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains"
        )
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        return response


class TenantScopeMiddleware(BaseHTTPMiddleware):
    """Extracts tenant_id from JWT into request.state (H-3). Enforcement happens in deps."""

    async def dispatch(self, request: Request, call_next):
        request.state.tenant_id = None
        request.state.user = None
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()
            try:
                from app.auth.jwt import decode_access_token

                payload = decode_access_token(token)
                request.state.tenant_id = payload.get("tenant_id")
                request.state.user_id = payload.get("sub")
                request.state.user_role = payload.get("role")
            except Exception:
                pass
        return await call_next(request)
