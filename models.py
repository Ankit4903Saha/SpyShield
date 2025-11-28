# models.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple


@dataclass
class AppInfo:
    package_name: str
    app_name: str
    permissions: List[str] = field(default_factory=list)
    is_system_app: bool = False
    has_launcher_icon: bool = True
    installed_from_play_store: bool = True
    uses_accessibility_service: bool = False
    uses_media_projection: bool = False
    has_overlay_permission: bool = False
    foreground_service_usage_score: float = 0.0  # 0.0 - 1.0
    background_network_usage_score: float = 0.0  # 0.0 - 1.0

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AppInfo":
        return AppInfo(
            package_name=data.get("package_name", ""),
            app_name=data.get("app_name", ""),
            permissions=data.get("permissions", []),
            is_system_app=data.get("is_system_app", False),
            has_launcher_icon=data.get("has_launcher_icon", True),
            installed_from_play_store=data.get("installed_from_play_store", True),
            uses_accessibility_service=data.get("uses_accessibility_service", False),
            uses_media_projection=data.get("uses_media_projection", False),
            has_overlay_permission=data.get("has_overlay_permission", False),
            foreground_service_usage_score=float(
                data.get("foreground_service_usage_score", 0.0)
            ),
            background_network_usage_score=float(
                data.get("background_network_usage_score", 0.0)
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "package_name": self.package_name,
            "app_name": self.app_name,
            "permissions": self.permissions,
            "is_system_app": self.is_system_app,
            "has_launcher_icon": self.has_launcher_icon,
            "installed_from_play_store": self.installed_from_play_store,
            "uses_accessibility_service": self.uses_accessibility_service,
            "uses_media_projection": self.uses_media_projection,
            "has_overlay_permission": self.has_overlay_permission,
            "foreground_service_usage_score": self.foreground_service_usage_score,
            "background_network_usage_score": self.background_network_usage_score,
        }


def compute_risk(app: AppInfo) -> Tuple[float, str, List[str]]:
    """
    Compute a 0-100 risk score for the app, along with a risk level
    (Low/Medium/High) and a list of textual reasons.

    This is rule-based and explainable.
    """

    score = 0.0
    reasons: List[str] = []

    # 1. Core dangerous behaviors
    if app.uses_media_projection:
        score += 30
        reasons.append("Uses MediaProjection / screen capture capability.")

    if app.uses_accessibility_service:
        score += 25
        reasons.append("Runs an Accessibility Service (can read screen content).")

    if app.has_overlay_permission:
        score += 15
        reasons.append("Has overlay (draw over other apps) permission.")

    # 2. Permissions-based signals (simplified example set)
    permission_weights = {
        "android.permission.READ_SMS": 10,
        "android.permission.RECEIVE_SMS": 8,
        "android.permission.READ_CALL_LOG": 8,
        "android.permission.CALL_PHONE": 4,
        "android.permission.RECORD_AUDIO": 8,
        "android.permission.CAMERA": 5,
        "android.permission.READ_CONTACTS": 5,
        "android.permission.ACCESS_FINE_LOCATION": 3,
        "android.permission.ACCESS_COARSE_LOCATION": 2,
        "android.permission.SYSTEM_ALERT_WINDOW": 10,
        "android.permission.READ_PHONE_STATE": 5,
    }

    for perm in app.permissions:
        if perm in permission_weights:
            w = permission_weights[perm]
            score += w
            reasons.append(f"Uses sensitive permission: {perm} (+{w}).")

    # 3. Behavioral scores
    if app.foreground_service_usage_score > 0.7:
        score += 10
        reasons.append(
            "Runs long-lived foreground services frequently (possible background spying)."
        )
    elif app.foreground_service_usage_score > 0.4:
        score += 5
        reasons.append(
            "Moderate use of foreground services (needs review)."
        )

    if app.background_network_usage_score > 0.7:
        score += 10
        reasons.append("High background network usage (sending data while not in active use).")
    elif app.background_network_usage_score > 0.4:
        score += 5
        reasons.append("Moderate background network usage (monitor if unexpected).")

    # 4. Trust modifiers
    if app.is_system_app:
        score -= 10
        reasons.append("System app: slightly reduced risk (still monitor for abuse).")

    if app.installed_from_play_store:
        score -= 5
        reasons.append("Installed from official store: slightly reduced risk.")

    if not app.has_launcher_icon:
        score += 10
        reasons.append("No launcher icon: app may be trying to hide from the user.")

    # Clamp score between 0 and 100
    score = max(0.0, min(100.0, score))

    # Risk level based on score
    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"

    return score, level, reasons
