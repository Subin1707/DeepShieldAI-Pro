import hashlib
import hmac
import secrets


def generate_secure_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def hash_value(value: str, salt: str | None = None) -> str:
    salt_value = salt or secrets.token_hex(16)
    digest = hashlib.sha256(f"{salt_value}:{value}".encode("utf-8")).hexdigest()
    return f"{salt_value}${digest}"


def verify_hash(value: str, hashed_value: str) -> bool:
    try:
        salt, expected_digest = hashed_value.split("$", 1)
    except ValueError:
        return False

    actual_digest = hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()
    return hmac.compare_digest(actual_digest, expected_digest)


def mask_secret(secret: str | None, visible_chars: int = 4) -> str:
    if not secret:
        return ""

    if len(secret) <= visible_chars * 2:
        return "*" * len(secret)

    return f"{secret[:visible_chars]}{'*' * 8}{secret[-visible_chars:]}"


def is_placeholder_secret(secret: str | None) -> bool:
    if not secret:
        return True

    lowered = secret.lower()
    return "your_" in lowered or "placeholder" in lowered or "api_key_here" in lowered
