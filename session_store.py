from datetime import datetime
from typing import Optional

_sessions: dict = {}


def log_request(username: str, sector: str, success: bool) -> None:
    """Log a request for a user session."""
    if username not in _sessions:
        _sessions[username] = {
            "username": username,
            "first_request": datetime.utcnow().isoformat(),
            "requests": [],
            "total_count": 0,
        }

    _sessions[username]["requests"].append({
        "sector": sector,
        "timestamp": datetime.utcnow().isoformat(),
        "success": success,
    })
    _sessions[username]["total_count"] += 1

  
    if len(_sessions[username]["requests"]) > 50:
        _sessions[username]["requests"] = _sessions[username]["requests"][-50:]


def get_session(username: str) -> Optional[dict]:
    """Get session info for a user."""
    return _sessions.get(username)


def get_all_sessions() -> dict:
    """Get all sessions (admin only)."""
    return {
        "total_users": len(_sessions),
        "sessions": _sessions,
    }