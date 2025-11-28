# streamlit_app.py
#
# SpyShield – Streamlit version
# This file is the main entrypoint for Streamlit Cloud.

import pandas as pd
import streamlit as st

from storage import load_apps

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="SpyShield - Dashboard",
    page_icon="🛡️",
    layout="wide",
)

# ---------- CUSTOM CSS FOR DARK AESTHETIC UI ----------
CUSTOM_CSS = """
<style>
/* Remove Streamlit default padding and make dark background */
.stApp {
    background: radial-gradient(circle at top left, #1d4ed8 0, transparent 55%),
                radial-gradient(circle at top right, #0f766e 0, transparent 55%),
                radial-gradient(circle at bottom, #7c3aed 0, transparent 55%),
                #020617;
    color: #f9fafb;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
}

/* Main container card */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3.5rem;
}

/* Header title styling */
.spyshield-header {
    padding: 1rem 1.25rem 1.1rem 1.25rem;
    border-radius: 1.2rem;
    background: radial-gradient(circle at top left, rgba(148,163,184,0.12), transparent 45%),
                radial-gradient(circle at bottom right, rgba(59,130,246,0.16), transparent 55%),
                rgba(15,23,42,0.92);
    border: 1px solid rgba(148,163,184,0.4);
    box-shadow: 0 18px 45px rgba(15,23,42,0.85);
    margin-bottom: 1.2rem;
}

/* Stats cards */
.stats-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin-top: 0.6rem;
}

.stat-card {
    padding: 0.5rem 0.9rem;
    border-radius: 999px;
    border: 1px solid rgba(148,163,184,0.6);
    background: rgba(15,23,42,0.9);
    display: flex;
    flex-direction: column;
}
.stat-label {
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9ca3af;
}
.stat-value {
    font-size: 1rem;
    font-weight: 600;
    color: #e5e7eb;
}

/* Risk levels */
.stat-card-high {
    border-color: rgba(248,113,113,0.8);
    background: radial-gradient(circle at top left, rgba(248,113,113,0.35), rgba(15,23,42,0.9));
}
.stat-card-medium {
    border-color: rgba(251,191,36,0.8);
    background: radial-gradient(circle at top left, rgba(251,191,36,0.35), rgba(15,23,42,0.9));
}
.stat-card-low {
    border-color: rgba(34,197,94,0.8);
    background: radial-gradient(circle at top left, rgba(34,197,94,0.35), rgba(15,23,42,0.9));
}

/* Table styling – use darker background & rounded corners */
.spyshield-table-container {
    margin-top: 0.8rem;
    padding: 0.4rem 0.4rem 0.2rem 0.4rem;
    border-radius: 1.1rem;
    background: radial-gradient(circle at top, rgba(15,23,42,0.95), rgba(15,23,42,0.98));
    border: 1px solid rgba(30,64,175,0.9);
}

/* Make dataframes darker */
.dataframe tbody tr:nth-child(odd) {
    background-color: rgba(15,23,42,0.9);
}
.dataframe tbody tr:nth-child(even) {
    background-color: rgba(15,23,42,0.98);
}
.dataframe thead {
    background: radial-gradient(circle at top, rgba(30,64,175,0.7), rgba(15,23,42,0.95));
    color: #e5e7eb;
}

/* Selected app detail card */
.detail-card {
    padding: 1rem 1.1rem 1.1rem 1.1rem;
    border-radius: 1.1rem;
    background: radial-gradient(circle at top left, rgba(30,64,175,0.35), rgba(15,23,42,0.98));
    border: 1px solid rgba(30,64,175,0.7);
}

/* Footer */
.spyshield-footer {
    text-align: center;
    font-size: 0.8rem;
    color: #e5e7eb;
    margin-top: 1.5rem;
    padding-top: 0.6rem;
    border-top: 1px solid rgba(51,65,85,0.9);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- LOAD DATA ----------
apps_dict = load_apps()
apps_list = list(apps_dict.values())
apps_list.sort(key=lambda x: x.get("risk_score", 0), reverse=True)

total_apps = len(apps_list)
high_count = sum(1 for a in apps_list if a.get("risk_level") == "High")
med_count = sum(1 for a in apps_list if a.get("risk_level") == "Medium")
low_count = sum(1 for a in apps_list if a.get("risk_level") == "Low")

# ---------- HEADER ----------
st.markdown(
    """
<div class="spyshield-header">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:1rem;">
    <div>
      <h1 style="margin-bottom:0.15rem;">Installed Apps Risk Overview</h1>
      <p style="font-size:0.9rem; color:#9ca3af; max-width:640px;">
        Simulated analysis of installed applications on a device, highlighting potential
        spyware or risky screen-mirroring behavior.
      </p>
    </div>
    <div class="stats-row">
      <div class="stat-card">
        <span class="stat-label">Total Apps</span>
        <span class="stat-value">{total}</span>
      </div>
      <div class="stat-card stat-card-high">
        <span class="stat-label">High Risk</span>
        <span class="stat-value">{high}</span>
      </div>
      <div class="stat-card stat-card-medium">
        <span class="stat-label">Medium Risk</span>
        <span class="stat-value">{med}</span>
      </div>
      <div class="stat-card stat-card-low">
        <span class="stat-label">Low Risk</span>
        <span class="stat-value">{low}</span>
      </div>
    </div>
  </div>
</div>
""".format(
        total=total_apps, high=high_count, med=med_count, low=low_count
    ),
    unsafe_allow_html=True,
)

# ---------- MAIN LAYOUT ----------
col_table, col_detail = st.columns([1.4, 1.1])

# ---------- TABLE (LEFT) ----------
with col_table:
    st.markdown("#### Apps & Risk Scores")

    if apps_list:
        # build a DataFrame for nice display
        df = pd.DataFrame(
            [
                {
                    "App": a.get("app_name"),
                    "Package / ID": a.get("package_name"),
                    "Risk Score": round(a.get("risk_score", 0), 1),
                    "Risk Level": a.get("risk_level"),
                    "Source": "Trusted / Store"
                    if a.get("installed_from_play_store")
                    else "Unknown / Sideloaded",
                }
                for a in apps_list
            ]
        )

        st.markdown('<div class="spyshield-table-container">', unsafe_allow_html=True)
        st.dataframe(
            df,
            use_container_width=True,
            height=480,
            hide_index=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        st.caption(
            "Tip: Use the scroll bars and column sort to explore installed applications."
        )
    else:
        st.info(
            "No apps found. On Streamlit Cloud or non-Windows OS, "
            "SpyShield uses the sample `data/sample_apps.json` file. "
            "Make sure that file exists in your repository for a richer demo."
        )

# ---------- DETAILS (RIGHT) ----------
with col_detail:
    st.markdown("#### Selected App Details")

    if apps_list:
        # Create a mapping of label -> app for the selector
        label_to_pkg = {
            f"{a.get('app_name')} ({a.get('package_name')})": a.get("package_name")
            for a in apps_list
        }
        labels_sorted = sorted(label_to_pkg.keys())
        default_label = labels_sorted[0]

        selected_label = st.selectbox(
            "Choose an app to inspect:", labels_sorted, index=labels_sorted.index(default_label)
        )
        selected_pkg = label_to_pkg[selected_label]
        app = apps_dict[selected_pkg]

        # Detail card
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)

        risk_level = app.get("risk_level", "Unknown")
        risk_score = round(app.get("risk_score", 0), 1)
        source_text = (
            "Trusted / Store" if app.get("installed_from_play_store") else "Unknown / Sideloaded"
        )
        publisher = app.get("publisher", "") or "Unknown"
        install_location = app.get("install_location", "") or "N/A"

        st.markdown(
            f"##### {app.get('app_name')}  \n"
            f"`{app.get('package_name')}`"
        )
        st.markdown(
            f"- **Risk Score:** **{risk_score}** ({risk_level})  \n"
            f"- **Source:** {source_text}  \n"
            f"- **Publisher:** {publisher}  \n"
            f"- **Install Location:** `{install_location}`"
        )

        st.markdown("---")
        st.markdown("**Flags & Behaviors**")

        col_basic1, col_basic2 = st.columns(2)
        with col_basic1:
            st.write(
                "- System app: **{}**".format("Yes" if app.get("is_system_app") else "No")
            )
            st.write(
                "- Launcher icon visible: **{}**".format(
                    "Yes" if app.get("has_launcher_icon") else "No"
                )
            )
            st.write(
                "- Accessibility service: **{}**".format(
                    "Yes" if app.get("uses_accessibility_service") else "No"
                )
            )
        with col_basic2:
            st.write(
                "- Screen capture / MediaProjection: **{}**".format(
                    "Yes" if app.get("uses_media_projection") else "No"
                )
            )
            st.write(
                "- Overlay permission: **{}**".format(
                    "Yes" if app.get("has_overlay_permission") else "No"
                )
            )
            st.write(
                "- Foreground service usage score: **{}**".format(
                    app.get("foreground_service_usage_score", 0.0)
                )
            )
            st.write(
                "- Background network usage score: **{}**".format(
                    app.get("background_network_usage_score", 0.0)
                )
            )

        # Permissions
        st.markdown("---")
        st.markdown("**Permissions**")
        perms = app.get("permissions") or []
        if perms:
            for p in perms:
                st.code(p, language="text")
        else:
            st.write("No explicit permissions recorded (or not available on this platform).")

        # Reasons
        st.markdown("---")
        st.markdown("**Why this risk score?**")
        reasons = app.get("risk_reasons") or []
        if reasons:
            for idx, r in enumerate(reasons, start=1):
                st.markdown(f"{idx}. {r}")
        else:
            st.write("No specific suspicious patterns detected for this application.")

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info(
            "Once applications are loaded, you can inspect individual app details here."
        )

# ---------- FOOTER ----------
st.markdown(
    """
<div class="spyshield-footer">
  SpyShield @ AnkitSaha4903
</div>
""",
    unsafe_allow_html=True,
)
