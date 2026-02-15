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


def valkey_exists(key: str) -> bool:
    """Check if a key exists."""
    return r.exists(key) == 1


def valkey_get(key: str) -> Any:
    """GET a key. Automatically JSON-deserializes when possible."""
    value = r.get(key)
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value  # fallback for old non-JSON data


def valkey_set(key: str, value: Any, expire: int | None = None) -> bool:
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


def valkey_delete(video_id: str) -> bool:
    """DELETE a key"""
    delete_list = [video_id + "_clean_transcript.json", video_id + "_segmented_summary.json",
                   video_id + "_fact_check.json", video_id + "_summary.json", video_id + ".en.vtt"]
    count = 0
    for key in delete_list:
        count += int(r.delete(key))
    return count


def vtt_file_to_string(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def vtt_string_to_file(content: str, file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
