"""
NIRMAAN AI - Interactive Garbage Map & Geospatial Triage View
Visualizes real SQLite report coordinates, severity markers, and DBSCAN hotspot cluster buffers
using Folium, OpenStreetMap tiles, and MarkerCluster with full attribution and filtering.
"""

from datetime import datetime
from pathlib import Path
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

from src.config import BENGALURU_BOUNDS
from src.database.repository import Repository
from src.ui.components import render_header


def render(repo: Repository):
    render_header(
        title="Interactive Municipal Garbage Map & Geospatial Triage",
        subtitle="Live geographic intelligence mapping active blackspots, DBSCAN spatial clusters, and field clearance status across Greater Bengaluru.",
        active_tab="Garbage Map"
    )

    all_reports = repo.get_all_reports()
    hotspots = repo.get_all_hotspots()
    wards = sorted(list(set([r["ward_name"] for r in all_reports if r.get("ward_name")])))
    categories = sorted(list(set([r["waste_category"] for r in all_reports if r.get("waste_category")])))

    # 1. Summary Header & Refresh Control
    sc1, sc2, sc3, sc4, sc5 = st.columns([1, 1, 1, 1, 0.8])
    total_reps = len(all_reports)
    high_prio = len([r for r in all_reports if (r.get("priority_score") or 0) >= 60 and r["status"] not in ["Cleared", "Verified Closed"]])
    under_clean = len([r for r in all_reports if r["status"] in ["Under Cleanup", "In Progress", "Awaiting Verification", "Assigned"]])
    cleared_cnt = len([r for r in all_reports if r["status"] in ["Cleared", "Verified Closed"]])

    with sc1:
        st.metric("Total Recorded", total_reps)
    with sc2:
        st.metric("High Priority Active", high_prio)
    with sc3:
        st.metric("Under Field Work", under_clean)
    with sc4:
        st.metric("Verified Cleared", cleared_cnt)
    with sc5:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    st.markdown("<hr style='margin: 0.75rem 0 1.25rem 0; border-color: rgba(255,255,255,0.15);'/>", unsafe_allow_html=True)

    # 2. Comprehensive Filter Controls
    f_c1, f_c2, f_c3, f_c4, f_c5, f_c6 = st.columns([1.1, 1.1, 1.1, 1.1, 1.1, 0.9])
    with f_c1:
        status_filter = st.selectbox(
            "Report Status",
            ["All", "Pending", "In Progress", "Under Cleanup", "Awaiting Verification", "Cleared", "Blocked", "Reopened"]
        )
    with f_c2:
        ward_filter = st.selectbox("Ward Jurisdiction", ["All"] + wards)
    with f_c3:
        sev_filter = st.selectbox("Severity Grade", ["All", "High", "Medium", "Low"])
    with f_c4:
        prio_filter = st.selectbox("Priority Tier", ["All", "Critical (≥80)", "High (≥60)", "Moderate (40–59)", "Low (<40)"])
    with f_c5:
        cat_filter = st.selectbox("Waste Category", ["All"] + categories)
    with f_c6:
        show_hotspots = st.checkbox("Show DBSCAN Buffers", value=True)

    # Apply Filters
    filtered_reports = all_reports
    if status_filter != "All":
        filtered_reports = [r for r in filtered_reports if r["status"] == status_filter]
    if ward_filter != "All":
        filtered_reports = [r for r in filtered_reports if r["ward_name"] == ward_filter]
    if sev_filter != "All":
        filtered_reports = [r for r in filtered_reports if r.get("severity_level") == sev_filter]
    if cat_filter != "All":
        filtered_reports = [r for r in filtered_reports if r.get("waste_category") == cat_filter]
    if prio_filter != "All":
        if prio_filter == "Critical (≥80)":
            filtered_reports = [r for r in filtered_reports if (r.get("priority_score") or 0) >= 80]
        elif prio_filter == "High (≥60)":
            filtered_reports = [r for r in filtered_reports if (r.get("priority_score") or 0) >= 60]
        elif prio_filter == "Moderate (40–59)":
            filtered_reports = [r for r in filtered_reports if 40 <= (r.get("priority_score") or 0) < 60]
        elif prio_filter == "Low (<40)":
            filtered_reports = [r for r in filtered_reports if (r.get("priority_score") or 0) < 40]

    # Validate coordinate bounds
    valid_reports = []
    unlocated_reports = []
    for r in filtered_reports:
        try:
            lat = float(r["latitude"])
            lon = float(r["longitude"])
            if BENGALURU_BOUNDS["lat_min"] <= lat <= BENGALURU_BOUNDS["lat_max"] and \
               BENGALURU_BOUNDS["lon_min"] <= lon <= BENGALURU_BOUNDS["lon_max"]:
                valid_reports.append(r)
            else:
                unlocated_reports.append(r)
        except (ValueError, TypeError):
            unlocated_reports.append(r)

    st.caption(
        f"Displaying **{len(valid_reports)}** mapped reports with verified GPS coordinates across Greater Bengaluru. "
        f"Tile Provider: **OpenStreetMap Public Tiles** (Standard Attribution)."
    )

    # Center coordinates
    center_lat = BENGALURU_BOUNDS["center_lat"]
    center_lon = BENGALURU_BOUNDS["center_lon"]
    if valid_reports:
        center_lat = sum(r["latitude"] for r in valid_reports) / len(valid_reports)
        center_lon = sum(r["longitude"] for r in valid_reports) / len(valid_reports)

    # 3. Initialize Folium Map with pure OpenStreetMap tiles
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="OpenStreetMap",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    )

    # 4. Overlay DBSCAN Hotspot Buffer Circles
    if show_hotspots:
        for hs in hotspots:
            if ward_filter != "All" and hs.get("ward_name") != ward_filter:
                continue
            folium.Circle(
                location=[hs["centroid_lat"], hs["centroid_lon"]],
                radius=hs["radius_meters"],
                color="#DC2626",
                weight=2,
                fill=True,
                fill_color="#EF4444",
                fill_opacity=0.20,
                tooltip=f"DBSCAN Hotspot {hs['hotspot_code']} ({hs['ward_name']}): {hs['incident_count']} repeat incidents | Recurrence Index: {hs['recurrence_score']:.1f}"
            ).add_to(m)

    # 5. Add Report Markers into MarkerCluster
    marker_cluster = MarkerCluster(name="Reported Waste Incidents").add_to(m)

    for r in valid_reports:
        sev = r.get("severity_level") or "Medium"
        st_val = r["status"]
        prio = r.get("priority_score") or 0.0

        # Colors adhering to prompt specification:
        # Green: verified-cleared reports
        # Red: high-priority active reports (Priority >= 60 or High Severity)
        # Orange: medium-priority active reports
        # Blue: low-priority active reports
        if st_val in ["Cleared", "Verified Closed"]:
            marker_color = "green"
            icon_name = "check"
        elif st_val == "Blocked":
            marker_color = "purple"
            icon_name = "ban"
        elif prio >= 60.0 or sev == "High":
            marker_color = "red"
            icon_name = "exclamation-triangle"
        elif prio >= 40.0 or sev == "Medium":
            marker_color = "orange"
            icon_name = "trash"
        else:
            marker_color = "blue"
            icon_name = "info-circle"

        sim_tag = "<span style='color:#B45309; font-weight:700;'>[DEMO SIMULATED]</span>" if r.get("is_simulated") else "<span style='color:#059669; font-weight:700;'>[FIELD OBSERVATION]</span>"
        created_time = str(r.get("created_at") or "Unknown")[:16]

        popup_html = f"""
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 12px; width: 250px; line-height: 1.45; color: #0F172A;">
            <div style="font-weight: 800; font-size: 13px; color: #1E3A8A; border-bottom: 2px solid #3B82F6; padding-bottom: 3px; margin-bottom: 5px;">
                {r['report_uid']}
            </div>
            <div><b>Ward:</b> {r['ward_name']} &bull; {sim_tag}</div>
            <div><b>Submitted:</b> {created_time}</div>
            <div style="margin-top: 3px;"><b>Operational Status:</b> <span style="font-weight: 700; color: #2563EB;">{st_val}</span></div>
            <div><b>Waste Category:</b> {r['waste_category'].replace('_', ' ').title()}</div>
            <div><b>Severity Grade:</b> <span style="font-weight: 700;">{sev}</span> ({r.get('severity_score', 0):.1f}/100)</div>
            <div><b>Priority Score (P):</b> <span style="font-weight: 800; color: #DC2626;">{prio:.1f}/100</span></div>
            <div style="font-size: 11px; color: #475569; margin-top: 6px; border-top: 1px solid #E2E8F0; padding-top: 4px;">
                <b>Address:</b> {r.get('address', 'N/A')[:65]}
            </div>
        </div>
        """

        folium.Marker(
            location=[r["latitude"], r["longitude"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{r['report_uid']} | Priority: {prio:.1f} | Severity: {sev} | Status: {st_val}",
            icon=folium.Icon(color=marker_color, icon=icon_name, prefix="fa")
        ).add_to(marker_cluster)

    # 6. Render Map
    if valid_reports or hotspots:
        st_folium(m, height=530, use_container_width=True)
    else:
        st.warning("No incidents match the selected filter combination.")

    # 7. Quick Inspection Bar below map
    if valid_reports:
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        c_insp1, c_insp2 = st.columns([3.5, 1])
        with c_insp1:
            insp_options = [
                f"{r['report_uid']} - {r['ward_name']} (Priority: {(r.get('priority_score') or 0):.1f} | {r['status']})"
                for r in valid_reports
            ]
            chosen_rep_str = st.selectbox("Inspect Full Dossier for Mapped Incident", insp_options)
        with c_insp2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Open Incident Dossier", type="primary", use_container_width=True):
                chosen_uid = chosen_rep_str.split(" - ")[0]
                st.session_state["nav_page"] = "Track Report"
                st.session_state["selected_report_uid"] = chosen_uid
                st.rerun()

    # 8. Legend adhering to prompt specification
    st.markdown(
        """
        <div style="background: rgba(255, 255, 255, 0.96); padding: 0.75rem 1.25rem; border-radius: 10px; border: 1px solid #CBD5E1; margin-top: 0.75rem; font-size: 0.82rem; color: #0F172A; display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <strong>Map Legend:</strong>
            <span><span style="color: #DC2626; font-weight: 900; font-size: 1.1rem;">●</span> Red: High Priority Active</span>
            <span><span style="color: #D97706; font-weight: 900; font-size: 1.1rem;">●</span> Orange: Medium Priority Active</span>
            <span><span style="color: #0284C7; font-weight: 900; font-size: 1.1rem;">●</span> Blue: Low Priority Active</span>
            <span><span style="color: #16A34A; font-weight: 900; font-size: 1.1rem;">●</span> Green: Verified Cleared</span>
            <span><span style="color: #9333EA; font-weight: 900; font-size: 1.1rem;">●</span> Purple: Blocked Site</span>
            <span><span style="color: #EF4444; font-weight: 900;">◯</span> Shaded Buffer: DBSCAN Spatial Cluster (200m)</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 9. Location Unavailable / Out of Bounds Section
    if unlocated_reports:
        with st.expander(f"📍 Location Unavailable or Out-of-Bounds ({len(unlocated_reports)} incidents)"):
            st.caption("The following reports do not have valid Bengaluru GPS coordinates and cannot be rendered on the geospatial canvas:")
            for ur in unlocated_reports:
                st.markdown(
                    f"- **{ur['report_uid']}** ({ur['ward_name']}): `{ur['status']}` | Category: {ur['waste_category']} | Coordinates: `{ur.get('latitude')}, {ur.get('longitude')}` | *{ur.get('address', 'No address')}*"
                )
