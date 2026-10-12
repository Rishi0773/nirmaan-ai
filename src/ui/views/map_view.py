"""
NIRMAAN AI - Interactive Garbage Map View
Visualizes reports and geospatial hotspot clusters across Bengaluru wards
using Folium and MarkerClusters (PPT Slide 3 & 6).
"""

import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

from src.config import BENGALURU_BOUNDS
from src.database.repository import Repository
from src.ui.components import render_header


def render(repo: Repository):
    render_header(
        title="Interactive Garbage Map & Geospatial Triage",
        subtitle="Geographic visualization of reported blackspots, severity markers, and hotspot cluster buffers.",
        active_tab="Garbage Map"
    )

    # Filter Controls
    f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 2])
    with f_col1:
        status_filter = st.selectbox("Filter Status", ["All", "Pending", "Under Cleanup", "Cleared"])
    with f_col2:
        reports = repo.get_all_reports()
        wards = sorted(list(set([r["ward_name"] for r in reports if r["ward_name"]])))
        ward_filter = st.selectbox("Filter Ward", ["All"] + wards)
    with f_col3:
        show_hotspots = st.checkbox("Overlay Hotspot Cluster Buffer Zones", value=True)

    filtered_reports = repo.get_all_reports(status=status_filter, ward=ward_filter)
    hotspots = repo.get_all_hotspots()

    # Create Folium Map
    center_lat = BENGALURU_BOUNDS["center_lat"]
    center_lon = BENGALURU_BOUNDS["center_lon"]
    if filtered_reports:
        center_lat = filtered_reports[0]["latitude"]
        center_lon = filtered_reports[0]["longitude"]

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="CartoDB positron"
    )

    # 1. Overlay Hotspot Buffer Circles
    if show_hotspots:
        for hs in hotspots:
            folium.Circle(
                location=[hs["centroid_lat"], hs["centroid_lon"]],
                radius=hs["radius_meters"],
                color="#DC2626",
                weight=2,
                fill=True,
                fill_color="#F87171",
                fill_opacity=0.25,
                tooltip=f"Hotspot {hs['hotspot_code']} ({hs['ward_name']}): {hs['incident_count']} repeat incidents | Recurrence: {hs['recurrence_score']}"
            ).add_to(m)

    # 2. Add Report Markers
    marker_cluster = MarkerCluster(name="Reported Incidents").add_to(m)

    for r in filtered_reports:
        sev = r.get("severity_level") or "Medium"
        status = r["status"]

        # Color coding
        if status == "Cleared":
            color = "green"
            icon = "check"
        elif sev == "High":
            color = "red"
            icon = "exclamation-triangle"
        elif sev == "Low":
            color = "blue"
            icon = "info-circle"
        else:
            color = "orange"
            icon = "trash"

        popup_html = f"""
        <div style="font-family: sans-serif; font-size: 12px; width: 220px;">
            <div style="font-weight: bold; color: #0F172A; font-size: 13px;">{r['report_uid']}</div>
            <div style="color: #64748B; margin-bottom: 4px;">{r['ward_name']}</div>
            <div style="margin-bottom: 4px;"><b>Status:</b> {status}</div>
            <div style="margin-bottom: 4px;"><b>Severity:</b> {sev} ({r.get('severity_score', 0):.1f})</div>
            <div style="margin-bottom: 4px;"><b>Priority Score:</b> {r.get('priority_score', 0):.1f}/100</div>
            <div style="font-size: 11px; color: #334155;">{r.get('address', '')[:60]}</div>
        </div>
        """

        folium.Marker(
            location=[r["latitude"], r["longitude"]],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{r['report_uid']} - {sev} Severity ({status})",
            icon=folium.Icon(color=color, icon=icon, prefix="fa")
        ).add_to(marker_cluster)

    # Render Map in Streamlit
    st_folium(m, width=None, height=520, use_container_width=True)

    # Map Legend
    st.markdown(
        """
        <div style="background: #FFFFFF; padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid #E2E8F0; margin-top: 0.5rem; font-size: 0.8rem; display: flex; gap: 1.5rem; align-items: center;">
            <strong>Map Legend:</strong>
            <span><span style="color: #DC2626; font-weight: bold;">●</span> Red: High Severity</span>
            <span><span style="color: #D97706; font-weight: bold;">●</span> Orange: Medium Severity</span>
            <span><span style="color: #0284C7; font-weight: bold;">●</span> Blue: Low Severity</span>
            <span><span style="color: #16A34A; font-weight: bold;">●</span> Green: Cleared Site</span>
            <span><span style="color: #F87171; font-weight: bold;">◯</span> Red Shaded Circle: Hotspot Cluster Buffer</span>
        </div>
        """,
        unsafe_allow_html=True
    )
