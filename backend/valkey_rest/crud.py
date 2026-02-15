import os
import json
from typing import Any

import redis
from dotenv import load_dotenv

load_dotenv()

# Single connection object
r = redis.Redis(
    host=os.getenv("VALKEY_HOST"),
    port=int(os.getenv("VALKEY_PORT")),
    password=os.getenv("VALKEY_PASSWORD"),
    ssl=True,
    decode_responses=True,
)


def ping() -> bool:
    """Test connection"""
    return r.ping()


def get(key: str) -> Any:
    """GET a key. Automatically JSON-deserializes when possible."""
    value = r.get(key)
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value  # fallback for old non-JSON data


def set(key: str, value: Any, expire: int | None = None) -> bool:
    """SET (or UPDATE) a key.
    - dict, list, int, float, bool → automatically JSON serialized
    - str → stored as-is (no extra quotes)
    """
    # Always serialize to JSON so we get proper types back on GET
    if value is None:
        json_value = "null"
    else:
        json_value = json.dumps(value)

    r.set(key, json_value)

    if expire is not None:
        r.expire(key, expire)

    return True


def delete(key: str) -> bool:
    """DELETE a key"""
    return bool(r.delete(key))
