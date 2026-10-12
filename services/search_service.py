"""
NIRMAAN AI - Search Service
Enables multi-field search across incident report UIDs, Bengaluru wards,
landmarks, addresses, and waste categories.
"""

from typing import List, Dict, Any
from src.database.repository import Repository


def search_reports(query: str, repo: Repository) -> List[Dict[str, Any]]:
    """
    Searches incident reports matching the query string.
    Matches across report_uid, ward_name, address, landmark, and waste_category.
    """
    if not query or not query.strip():
        return []

    q = query.strip().lower()
    all_reports = repo.get_all_reports()
    results = []

    for r in all_reports:
        uid = (r.get("report_uid") or "").lower()
        ward = (r.get("ward_name") or "").lower()
        address = (r.get("address") or "").lower()
        landmark = (r.get("landmark") or "").lower()
        category = (r.get("waste_category") or "").lower()
        status = (r.get("status") or "").lower()

        # Score relevance
        if q in uid or q in ward or q in address or q in landmark or q in category or q in status:
            results.append(r)

    return results
