from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime


def generate_analysis_pdf(analysis: dict, user_name: str = "Candidate") -> bytes:
    """Generate a professional PDF report from analysis data."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=22, textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=6, alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading', parent=styles['Heading2'],
        fontSize=13, textColor=colors.HexColor('#16213e'),
        spaceBefore=14, spaceAfter=6,
        borderPad=4,
    )
    body_style = ParagraphStyle(
        'CustomBody', parent=styles['Normal'],
        fontSize=10, leading=16, textColor=colors.HexColor('#333333')
    )
    score_style = ParagraphStyle(
        'ScoreStyle', parent=styles['Normal'],
        fontSize=28, textColor=colors.HexColor('#0f3460'),
        alignment=TA_CENTER, fontName='Helvetica-Bold'
    )

    # Header
    story.append(Paragraph("AI Resume Analysis Report", title_style))
    story.append(Paragraph(
        f"Generated for: <b>{user_name}</b> | {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        ParagraphStyle('Sub', parent=styles['Normal'], fontSize=10,
                       textColor=colors.gray, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 0.3*inch))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0f3460')))
    story.append(Spacer(1, 0.2*inch))

    # Score summary table
    ats = analysis.get("ats_score", 0)
    skill_match = analysis.get("skill_match_percentage", 0)
    tfidf = analysis.get("tfidf_similarity", 0)
    cosine = analysis.get("cosine_similarity", 0)

    score_color = colors.HexColor('#27ae60') if ats >= 70 else \
                  colors.HexColor('#f39c12') if ats >= 50 else colors.HexColor('#e74c3c')

    score_data = [
        ['ATS Score', 'Skill Match', 'TF-IDF Sim.', 'Cosine Sim.'],
        [f"{ats:.1f}%", f"{skill_match:.1f}%", f"{tfidf:.1f}%", f"{cosine:.1f}%"],
    ]
    score_table = Table(score_data, colWidths=[4*cm]*4)
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f0f4f8')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 18),
        ('TEXTCOLOR', (0, 1), (0, 1), score_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, 1), [colors.HexColor('#f0f4f8')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.25*inch))

    # Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dee2e6')))
    story.append(Spacer(1, 0.1*inch))
    summary = analysis.get("summary", "No summary available.")
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 0.2*inch))

    # Matched skills
    matched = analysis.get("matched_skills", [])
    if matched:
        story.append(Paragraph("✓ Matched Skills", heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dee2e6')))
        story.append(Spacer(1, 0.1*inch))
        skill_text = "  •  ".join(matched)
        story.append(Paragraph(skill_text, ParagraphStyle(
            'Skills', parent=body_style, textColor=colors.HexColor('#27ae60')
        )))
        story.append(Spacer(1, 0.2*inch))

    # Missing skills
    missing = analysis.get("missing_skills", [])
    if missing:
        story.append(Paragraph("✗ Missing Skills", heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dee2e6')))
        story.append(Spacer(1, 0.1*inch))
        miss_text = "  •  ".join(missing)
        story.append(Paragraph(miss_text, ParagraphStyle(
            'Missing', parent=body_style, textColor=colors.HexColor('#e74c3c')
        )))
        story.append(Spacer(1, 0.2*inch))

    # Suggestions
    suggestions = analysis.get("suggestions", [])
    if suggestions:
        story.append(Paragraph("Improvement Suggestions", heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dee2e6')))
        story.append(Spacer(1, 0.1*inch))
        for i, sug in enumerate(suggestions, 1):
            story.append(Paragraph(f"{i}. {sug}", body_style))
            story.append(Spacer(1, 0.05*inch))

    # Footer
    story.append(Spacer(1, 0.3*inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dee2e6')))
    story.append(Paragraph(
        "Generated by AI Resume Analyzer | Powered by NLP & Machine Learning",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8,
                       textColor=colors.gray, alignment=TA_CENTER)
    ))

    doc.build(story)
    return buffer.getvalue()
