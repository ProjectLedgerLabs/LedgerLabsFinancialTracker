from typing import List, Dict, Any
from fastapi import Request

def flash(request: Request, message: str, category: str = "success") -> None:
    """Store a flash message in the session"""
    if not hasattr(request, "session"):
        return
    
    flashes = request.session.get("_flashes", [])
    flashes.append({"message": message, "type": category})
    request.session["_flashes"] = flashes

def get_flashed_messages(request: Request) -> List[Dict[str, Any]]:
    """Retrieve and clear flash messages from the session"""
    if not hasattr(request, "session"):
        return []
    
    flashes = request.session.pop("_flashes", [])
    return flashes