# ==========================================================
# normalizers.py — ATILA Golden Standard Normalization Layer
# ==========================================================
import yaml
import json
from datetime import datetime
from typing import Dict, Any

# Load platform field mappings
def load_platform_map(path: str = "config/platform_map.yaml") -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)

# Resolve nested key paths like fields.status.name or fields["System.Title"]
def resolve_path(data: Dict[str, Any], path: str):
    try:
        if not path or path.lower() == "null":
            return None
        value = data
        for part in path.replace("[", ".[").split("."):
            if part.startswith("["):
                key = part.strip("[]\"'")
                value = value.get(key) if isinstance(value, dict) else value
            elif isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value
    except Exception:
        return None

# Normalize ticket into ATILA Smart Ticket
def normalize_ticket(source: str, raw_ticket: Dict[str, Any], platform_map: Dict[str, Any]) -> Dict[str, Any]:
    platform_rules = platform_map.get(source.lower())
    if not platform_rules:
        raise ValueError(f"No mapping found for platform: {source}")

    normalized = {}
    for target_field, source_path in platform_rules.items():
        normalized[target_field] = resolve_path(raw_ticket, source_path)

    # Default handling
    normalized["source"] = source
    normalized["created_at"] = _safe_date(normalized.get("created_at"))
    normalized["updated_at"] = _safe_date(normalized.get("updated_at"))
    return normalized

def _safe_date(val):
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00")) if val else datetime.utcnow()
    except Exception:
        return datetime.utcnow()

# Example usage
if __name__ == "__main__":
    # Load mapping and demo with fake GitHub issue
    mapping = load_platform_map()
    example_github = {
        "id": 1001,
        "title": "Bug: login error",
        "body": "Users cannot log in after update.",
        "state": "open",
        "assignee": {"login": "david"},
        "labels": [{"name": "bug"}, {"name": "auth"}],
        "created_at": "2025-11-09T14:30:00Z",
        "updated_at": "2025-11-09T15:00:00Z",
        "repository": {"name": "ai-pipeline"}
    }

    norm = normalize_ticket("github", example_github, mapping)
    print(json.dumps(norm, indent=2, default=str))
