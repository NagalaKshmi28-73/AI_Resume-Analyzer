"""
Generates a downloadable PDF report summarizing the resume analysis.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
)


def generate_pdf_report(filename: str, job_role: str, ats_result: dict,
                         match_result: dict, ai_feedback: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], textColor=colors.HexColor("#1a1a2e"))
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], textColor=colors.HexColor("#16213e"), spaceBefore=12)
    body_style = styles["BodyText"]

    story = []
    story.append(Paragraph("AI Resume Analysis Report", title_style))
    story.append(Paragraph(f"File: {filename} &nbsp;&nbsp;|&nbsp;&nbsp; Target Role: {job_role}", body_style))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", body_style))
    story.append(Spacer(1, 12))

    # Scores table
    score_data = [
        ["Metric", "Score"],
        ["ATS Compatibility Score", f"{ats_result['total_score']} / 100"],
        ["Job Role Match Score", f"{match_result['match_score']} / 100"],
    ]
    score_table = Table(score_data, colWidths=[9 * cm, 6 * cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Matched Required Skills", heading_style))
    story.append(_bullet_list(match_result["matched_required"] or ["None found"]))

    story.append(Paragraph("Missing Required Skills", heading_style))
    story.append(_bullet_list(match_result["missing_required"] or ["None — great coverage!"]))

    story.append(Paragraph("Missing Preferred Skills", heading_style))
    story.append(_bullet_list(match_result["missing_preferred"] or ["None — great coverage!"]))

    story.append(Paragraph("AI Summary", heading_style))
    story.append(Paragraph(ai_feedback.get("summary", "N/A"), body_style))

    story.append(Paragraph("Strengths", heading_style))
    story.append(_bullet_list(ai_feedback.get("strengths", []) or ["N/A"]))

    story.append(Paragraph("Areas to Improve", heading_style))
    story.append(_bullet_list(ai_feedback.get("weaknesses", []) or ["N/A"]))

    story.append(Paragraph("Improvement Suggestions", heading_style))
    story.append(_bullet_list(ai_feedback.get("improvement_suggestions", []) or ["N/A"]))

    rewrites = ai_feedback.get("rewrite_examples", [])
    if rewrites:
        story.append(Paragraph("Suggested Rewrites", heading_style))
        for ex in rewrites:
            story.append(Paragraph(f"<b>Before:</b> {ex.get('original', '')}", body_style))
            story.append(Paragraph(f"<b>After:</b> {ex.get('improved', '')}", body_style))
            story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _bullet_list(items: list[str]) -> ListFlowable:
    style = getSampleStyleSheet()["BodyText"]
    return ListFlowable(
        [ListItem(Paragraph(item, style)) for item in items],
        bulletType="bullet",
    )
