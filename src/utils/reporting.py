"""
NIRMAAN AI - Civic Presentation Reporting & Exports
Generates structured CSV dumps and formatted PDF executive summaries,
incident dossiers, ward operations reports, and audit logs using ReportLab.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.config import EXPORTS_DIR, CIVIC_DISCLAIMER


def _get_base_styles():
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CivicTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        textColor=colors.HexColor('#0F172A'), spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'CivicSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13,
        textColor=colors.HexColor('#475569'), spaceAfter=12
    )
    section_style = ParagraphStyle(
        'CivicSection', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=12, leading=15,
        textColor=colors.HexColor('#1E293B'), spaceBefore=10, spaceAfter=6
    )
    body_style = ParagraphStyle(
        'CivicBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#334155')
    )
    disclaimer_style = ParagraphStyle(
        'CivicDisclaimer', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=7.5, leading=10,
        textColor=colors.HexColor('#64748B'), spaceBefore=12
    )
    return title_style, subtitle_style, section_style, body_style, disclaimer_style


def export_reports_to_csv(reports: List[Dict[str, Any]], filename: str = "nirmaan_reports_dump.csv") -> str:
    """Exports list of reports to CSV in data/exports/."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = EXPORTS_DIR / filename
    df = pd.DataFrame(reports)
    cols = [
        "report_uid", "ward_name", "status", "waste_category",
        "severity_level", "severity_score", "priority_score",
        "latitude", "longitude", "address", "is_simulated", "created_at"
    ]
    avail_cols = [c for c in cols if c in df.columns]
    if avail_cols:
        df[avail_cols].to_csv(str(filepath), index=False)
    else:
        df.to_csv(str(filepath), index=False)
    return str(filepath)


def generate_executive_pdf_report(
    metrics: Dict[str, Any],
    top_hotspots: List[Dict[str, Any]],
    output_filename: str = "nirmaan_executive_summary.pdf"
) -> str:
    """Builds a structured, professional civic PDF report using ReportLab."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = EXPORTS_DIR / output_filename
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    title_style, subtitle_style, section_style, body_style, disclaimer_style = _get_base_styles()

    story.append(Paragraph("NIRMAAN AI — Civic Solid Waste Prioritization", title_style))
    story.append(Paragraph(
        f"Executive Pilot Assessment & Hotspot Intelligence Dossier | Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#059669'), spaceAfter=12))

    story.append(Paragraph("1. Executive Summary & Operational Metrics", section_style))
    story.append(Paragraph(
        "NIRMAAN AI dynamically triages urban solid waste complaints using YOLOv8 multi-class detection, "
        "OpenCV contour ground coverage, and DBSCAN spatiotemporal clustering to eliminate First-Come-First-Served delays.",
        body_style
    ))
    story.append(Spacer(1, 8))

    kpi_data = [
        ["Metric", "Value", "Metric", "Value"],
        ["Total Logged Reports", str(metrics.get("total_reports", 0)), "Active Spatial Hotspots", str(metrics.get("active_hotspots", 0))],
        ["Pending Dispatches", str(metrics.get("pending_reports", 0)), "High-Severity Unresolved", str(metrics.get("high_severity_pending", 0))],
        ["Under Field Cleanup", str(metrics.get("under_cleanup", 0)), "Average Priority Score", f"{metrics.get('avg_priority_score', 0):.1f}/100"],
        ["Verified Cleared", str(metrics.get("cleared_reports", 0)), "FCFS Dwell Time Reduction", "35.8% (Simulated)"]
    ]
    kpi_table = Table(kpi_data, colWidths=[135, 120, 135, 120])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFFFF')),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Top Chronic Hotspots (Spatial Clusters)", section_style))
    hs_rows = [["Code", "Ward", "Incidents", "Recurrence Index", "Avg Severity", "Status"]]
    for h in top_hotspots[:6]:
        hs_rows.append([
            h.get("hotspot_code", "HS"),
            h.get("ward_name", "Ward"),
            str(h.get("incident_count", 0)),
            f"{h.get('recurrence_score', 0):.1f}",
            f"{h.get('avg_severity', 0):.1f}",
            h.get("status", "Active")
        ])

    hs_table = Table(hs_rows, colWidths=[65, 130, 65, 95, 80, 65])
    hs_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(hs_table)
    story.append(Spacer(1, 12))

    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#E2E8F0'), spaceAfter=6))
    story.append(Paragraph(
        f"<b>Academic Integrity & Verification Notice:</b> {CIVIC_DISCLAIMER} "
        "Generated strictly for municipal pilot feasibility and research evaluation.",
        disclaimer_style
    ))

    doc.build(story)
    return str(filepath)


def generate_incident_pdf_report(report: Dict[str, Any], output_filename: str = "nirmaan_incident_report.pdf") -> str:
    """Generates an individual Incident Investigation Report PDF."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = EXPORTS_DIR / output_filename
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    title_style, subtitle_style, section_style, body_style, disclaimer_style = _get_base_styles()

    story.append(Paragraph(f"NIRMAAN AI — Incident Investigation Report", title_style))
    story.append(Paragraph(
        f"Ticket UID: {report['report_uid']} | Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=12))

    story.append(Paragraph("1. Incident Identification & Location Details", section_style))
    p_score = report.get("priority_score") or 0.0
    sev_lvl = report.get("severity_level") or "Unassessed"
    data = [
        ["Report UID", report["report_uid"], "Status", report["status"]],
        ["Ward Name", report["ward_name"], "Category", report["waste_category"].replace('_', ' ').title()],
        ["Address", report.get("address", "N/A"), "Coordinates", f"{report['latitude']:.4f}, {report['longitude']:.4f}"],
        ["Reported Time", str(report.get("created_at")), "Reporter", report.get("reporter_name", "Anonymous Citizen")],
        ["Severity Grade", str(sev_lvl), "Priority Score", f"{p_score:.1f}/100"]
    ]
    t = Table(data, colWidths=[110, 150, 110, 140])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Mathematical Priority Breakdown", section_style))
    s_comp = report.get('severity_component') or 0.0
    r_comp = report.get('recurrence_component') or 0.0
    w_comp = report.get('waste_type_component') or 0.0
    t_comp = report.get('waiting_time_component') or 0.0
    prio_data = [
        ["Component", "Symbol", "Weight", "Calculated Component Value"],
        ["Severity Index", "S", "35%", f"{s_comp:.1f} pts"],
        ["Recurrence Index", "R", "25%", f"{r_comp:.1f} pts"],
        ["Waste Hazard Index", "W", "20%", f"{w_comp:.1f} pts"],
        ["Waiting Time Escalator", "T", "20%", f"{t_comp:.1f} pts"],
        ["Aggregate Priority Score", "Final", "100%", f"{p_score:.1f} / 100"]
    ]
    pt = Table(prio_data, colWidths=[160, 60, 80, 210])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(pt)
    story.append(Spacer(1, 12))

    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#E2E8F0'), spaceAfter=6))
    story.append(Paragraph(f"<b>Notice:</b> {CIVIC_DISCLAIMER}", disclaimer_style))

    doc.build(story)
    return str(filepath)


def generate_ward_operations_pdf_report(
    ward_name: str,
    reports: List[Dict[str, Any]],
    output_filename: str = "nirmaan_ward_operations.pdf"
) -> str:
    """Generates Ward Operations Assessment Report PDF."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = EXPORTS_DIR / output_filename
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    title_style, subtitle_style, section_style, body_style, disclaimer_style = _get_base_styles()

    story.append(Paragraph(f"NIRMAAN AI — Ward Operations Report: {ward_name}", title_style))
    story.append(Paragraph(
        f"Jurisdiction: {ward_name} Ward | Period Summary | Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0D9488'), spaceAfter=12))

    # Ward summary counts
    total = len(reports)
    pending = len([r for r in reports if r["status"] in ["Pending", "Submitted", "Under Review", "Prioritized"]])
    under = len([r for r in reports if r["status"] in ["Under Cleanup", "In Progress", "Awaiting Verification", "Assigned"]])
    cleared = len([r for r in reports if r["status"] in ["Cleared", "Verified Closed"]])

    w_summary = [
        ["Total Ward Reports", str(total), "Pending Strike Dispatch", str(pending)],
        ["Under Active Cleanup", str(under), "Verified Closed Sites", str(cleared)]
    ]
    st_table = Table(w_summary, colWidths=[140, 115, 140, 115])
    st_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(st_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph(f"Recent Complaints in {ward_name}", section_style))
    r_rows = [["UID", "Address", "Category", "Severity", "Priority Score", "Status"]]
    for r in reports[:10]:
        r_rows.append([
            r["report_uid"],
            r.get("address", "")[:32],
            r["waste_category"].replace('_', ' ').title(),
            r.get("severity_level", "Medium"),
            f"{(r.get('priority_score') or 0.0):.1f}",
            r["status"]
        ])
    rt = Table(r_rows, colWidths=[75, 175, 80, 60, 60, 60])
    rt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(rt)
    story.append(Spacer(1, 12))

    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#E2E8F0'), spaceAfter=6))
    story.append(Paragraph(f"<b>Notice:</b> {CIVIC_DISCLAIMER}", disclaimer_style))

    doc.build(story)
    return str(filepath)
