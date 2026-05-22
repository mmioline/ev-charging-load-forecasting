import json
from datetime import datetime
from typing import Optional

from redis import Redis
from redis.exceptions import RedisError

from .config import settings

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)


def _status_key(station_id: int) -> str:
    return f"station:status:{station_id}"


def cache_station_status(
    station_id: int,
    status: str,
    last_updated_at: datetime,
) -> bool:
    payload = {
        "station_id": station_id,
        "status": status,
        "last_updated_at": last_updated_at.isoformat(),
    }
    try:
        redis_client.set(_status_key(station_id), json.dumps(payload, ensure_ascii=False))
        return True
    except RedisError:
        return False


def get_cached_station_status(station_id: int) -> Optional[dict]:
    try:
        raw_data = redis_client.get(_status_key(station_id))
    except RedisError:
        return None

    if not raw_data:
        return None

    try:
        return json.loads(raw_data)
    except json.JSONDecodeError:
        return None
