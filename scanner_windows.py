# scanner_windows.py
#
# Enumerate installed applications on Windows using the Registry,
# and map them into a dict format compatible with AppInfo.

import winreg
from typing import List, Dict, Tuple

# Registry locations where installed apps are registered
UNINSTALL_KEYS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
]

# Publishers we treat as "trusted" (mapped to installed_from_play_store = True)
TRUSTED_PUBLISHERS = [
    "Microsoft Corporation",
    "Google LLC",
    "Google Inc.",
    "Adobe",
    "Intel Corporation",
    "NVIDIA Corporation",
    "Oracle Corporation",
]

# Very simple heuristic keywords to mark suspicious remote/screen-related tools
SUSPICIOUS_KEYWORDS = [
    "remote",
    "viewer",
    "anydesk",
    "teamviewer",
    "monitor",
    "spy",
    "tracker",
    "keylogger",
    "assistant",
    "control",
    "screen",
]


def _get_reg_value(key, value_name: str):
    """Safely read a string value from a registry key."""
    try:
        value, _ = winreg.QueryValueEx(key, value_name)
        return str(value)
    except OSError:
        return None


def _enum_installed_apps_from_key(root, path: str) -> List[Dict[str, str]]:
    apps: List[Dict[str, str]] = []
    try:
        with winreg.OpenKey(root, path) as key:
            subkey_count = winreg.QueryInfoKey(key)[0]
            for i in range(subkey_count):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        display_name = _get_reg_value(subkey, "DisplayName")
                        if not display_name:
                            continue  # skip entries without a visible name

                        publisher = _get_reg_value(subkey, "Publisher") or ""
                        install_location = _get_reg_value(subkey, "InstallLocation") or ""

                        apps.append(
                            {
                                "registry_key": subkey_name,
                                "app_name": display_name,
                                "publisher": publisher,
                                "install_location": install_location,
                            }
                        )
                except OSError:
                    continue
    except OSError:
        # key might not exist on some systems
        pass

    return apps


def _to_appinfo_dict(app: Dict[str, str]) -> Dict[str, object]:
    """
    Map raw registry app info to the AppInfo-compatible dict.
    We don't have Android-style permissions here, so those stay empty/default.
    We use some basic heuristics for risk.
    """
    name = app["app_name"]
    publisher = app.get("publisher", "")
    install_location = app.get("install_location", "")
    registry_key = app.get("registry_key", "")

    # Use registry key as a stable "package_name" fallback
    pkg_name = registry_key or name.replace(" ", "_").lower()

    lower_publisher = publisher.lower()
    lower_name = name.lower()
    lower_location = install_location.lower()

    # Heuristic: treat Microsoft / Windows directory apps as system-ish
    is_system_app = (
        "microsoft" in lower_publisher
        or lower_location.startswith(r"c:\windows")
    )

    # Heuristic: treat known big vendors as "trusted source"
    installed_from_store = any(
        trusted.lower() in lower_publisher for trusted in TRUSTED_PUBLISHERS
    )

    # Basic suspicion heuristic based on name
    suspicious = any(keyword in lower_name for keyword in SUSPICIOUS_KEYWORDS)

    foreground_score = 0.0
    background_score = 0.0
    uses_media_projection = False
    uses_accessibility_service = False

    if suspicious:
        foreground_score = 0.8
        background_score = 0.6
        uses_media_projection = any(
            word in lower_name for word in ("screen", "remote", "viewer")
        )

    return {
        "package_name": pkg_name,
        "app_name": name,
        "permissions": [],  # no direct permissions info on Windows
        "is_system_app": is_system_app,
        "has_launcher_icon": True,
        "installed_from_play_store": installed_from_store,
        "uses_accessibility_service": uses_accessibility_service,
        "uses_media_projection": uses_media_projection,
        "has_overlay_permission": False,
        "foreground_service_usage_score": foreground_score,
        "background_network_usage_score": background_score,
        # extra metadata (used only for display / future work)
        "publisher": publisher,
        "install_location": install_location,
    }


def get_installed_apps_windows() -> List[Dict[str, object]]:
    """
    Public function: returns a list of dicts representing installed apps
    in a format that AppInfo.from_dict() understands.
    """
    seen: set[tuple] = set()
    result: List[Dict[str, object]] = []

    for root, path in UNINSTALL_KEYS:
        for raw_app in _enum_installed_apps_from_key(root, path):
            key = (raw_app["app_name"], raw_app["publisher"])
            if key in seen:
                continue  # de-duplicate entries
            seen.add(key)

            mapped = _to_appinfo_dict(raw_app)
            result.append(mapped)

    return result
