class DomainError(Exception):
    code: str = "domain_error"
    status: int = 400
    title: str = "Domain error"

    def __init__(self, detail: str = ""):
        super().__init__(detail or self.title)
        self.detail = detail or self.title


class ClaimNotFound(DomainError):
    code = "not_found"
    status = 404
    title = "Claim not found"


class FileNotFound(DomainError):
    code = "not_found"
    status = 404
    title = "File not found"


class UserNotFound(DomainError):
    code = "not_found"
    status = 404
    title = "User not found"


class ProviderNotFound(DomainError):
    code = "not_found"
    status = 404
    title = "Provider not found"


class DuplicateClaimNumber(DomainError):
    code = "conflict"
    status = 409
    title = "Duplicate claim number"


class InvalidStatusTransition(DomainError):
    code = "conflict"
    status = 409
    title = "Invalid status transition"


class ExtractionMissing(DomainError):
    code = "conflict"
    status = 409
    title = "Extraction missing"


class OverrideReasonRequired(DomainError):
    code = "validation"
    status = 422
    title = "Override reason required"


class AuditChainBroken(DomainError):
    code = "internal"
    status = 500
    title = "Audit chain broken"


class TenantMismatch(DomainError):
    code = "forbidden"
    status = 403
    title = "Tenant mismatch"


class Unauthorized(DomainError):
    code = "unauthorized"
    status = 401
    title = "Unauthorized"


class Forbidden(DomainError):
    code = "forbidden"
    status = 403
    title = "Forbidden"


class RateLimited(DomainError):
    code = "rate_limited"
    status = 429
    title = "Rate limited"


class PayloadTooLarge(DomainError):
    code = "payload_too_large"
    status = 413
    title = "Payload too large"


class UnsupportedMediaType(DomainError):
    code = "unsupported_media_type"
    status = 415
    title = "Unsupported media type"


class ValidationFailed(DomainError):
    code = "validation"
    status = 422
    title = "Validation failed"


class UpstreamUnavailable(DomainError):
    code = "upstream_unavailable"
    status = 502
    title = "Upstream unavailable"


class ServiceUnavailable(DomainError):
    code = "service_unavailable"
    status = 503
    title = "Service unavailable"
