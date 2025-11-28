# storage.py

import json
from pathlib import Path
from typing import Dict, List

from models import AppInfo, compute_risk


DATA_FILE = Path("data") / "sample_apps.json"


def load_apps() -> Dict[str, dict]:
    """
    Load apps from JSON file and compute risk info for each.
    Returns a dict keyed by package_name with full app info + risk.
    """
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw_list: List[dict] = json.load(f)

    apps: Dict[str, dict] = {}
    for raw in raw_list:
        app = AppInfo.from_dict(raw)
        score, level, reasons = compute_risk(app)
        info = app.to_dict()
        info["risk_score"] = score
        info["risk_level"] = level
        info["risk_reasons"] = reasons
        apps[app.package_name] = info

    return apps


def save_apps(apps: Dict[str, dict]) -> None:
    """
    Save current apps (without risk fields) back to JSON if needed.
    Not strictly required for a read-only demo.
    """
    cleaned = []
    for pkg, info in apps.items():
        # Remove risk fields if present
        d = dict(info)
        d.pop("risk_score", None)
        d.pop("risk_level", None)
        d.pop("risk_reasons", None)
        cleaned.append(d)

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=4, ensure_ascii=False)
