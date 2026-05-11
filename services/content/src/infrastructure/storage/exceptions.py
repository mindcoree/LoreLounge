class MinioCleanupError(Exception):
    """Raised when user media cleanup in MinIO fails for non-idempotent reasons."""
