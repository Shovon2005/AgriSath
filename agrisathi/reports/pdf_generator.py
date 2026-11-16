"""
Professional PDF Agronomic Advisory Report Generator using ReportLab.
"""

import io
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from agrisathi.core.exceptions import ReportGenerationError


PRIMARY_GREEN = colors.HexColor("#1b5e20")
SECONDARY_GREEN = colors.HexColor("#2e7d32")
LIGHT_GREEN = colors.HexColor("#e8f5e9")
DARK_GRAY = colors.HexColor("#212121")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
BORDER_GRAY = colors.HexColor("#e0e0e0")
AMBER_WARN = colors.HexColor("#e65100")


def generate_pdf_advisory_report(
    prediction_result: Dict[str, Any],
    advisory_data: Dict[str, Any],
    output_stream: io.BytesIO = None,
) -> bytes:
    """
    Generate an agronomic PDF advisory document.
    Returns bytes content of the generated PDF.
    """
    buffer = output_stream or io.BytesIO()

    try:
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=PRIMARY_GREEN,
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#555555"),
        )
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=PRIMARY_GREEN,
            spaceBefore=10,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=DARK_GRAY,
        )
        body_bold = ParagraphStyle(
            "BodyBold",
            parent=body_style,
            fontName="Helvetica-Bold",
        )
        hero_style = ParagraphStyle(
            "HeroCrop",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=PRIMARY_GREEN,
            alignment=1,
        )
        table_cell = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=DARK_GRAY,
        )
        table_header = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.white,
        )

        story = []

        # 1. Header Banner
        timestamp_str = datetime.now().strftime("%B %d, %Y - %H:%M UTC")
        header_table = Table(
            [
                [
                    Paragraph("<b>AgriSathi | Precision Agriculture</b>", title_style),
                    Paragraph(f"<b>Report ID:</b> AGR-{int(datetime.now().timestamp())}<br/><b>Date:</b> {timestamp_str}", subtitle_style),
                ]
            ],
            colWidths=[4.2 * inch, 3.0 * inch],
        )
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ]))
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_GREEN, spaceBefore=6, spaceAfter=10))

        # 2. Hero Recommendation Box
        crop = prediction_result.get("recommended_crop", "").title()
        conf = float(prediction_result.get("confidence", 95.0))
        crop_profile = advisory_data.get("crop_profile", {})
        crop_desc = crop_profile.get("description", "Target crop determined optimal by Random Forest model.")

        hero_data = [
            [Paragraph("PRIMARY AI CROP RECOMMENDATION", ParagraphStyle("SubHeader", parent=body_bold, textColor=SECONDARY_GREEN, alignment=1))],
            [Paragraph(f"<b>{crop.upper()}</b>", hero_style)],
            [Paragraph(f"Model Confidence: <b>{conf:.1f}%</b> | Scientific Name: <i>{crop_profile.get('display_name', crop)}</i>", ParagraphStyle("Conf", parent=body_style, alignment=1))],
            [Paragraph(crop_desc, ParagraphStyle("Desc", parent=body_style, alignment=1, textColor=colors.HexColor("#444444")))],
        ]
        hero_table = Table(hero_data, colWidths=[7.2 * inch])
        hero_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREEN),
            ("BOX", (0, 0), (-1, -1), 1.5, PRIMARY_GREEN),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        story.append(hero_table)
        story.append(Spacer(1, 10))

        # 3. Two-Column Analysis: Soil Health & Fertilizer
        story.append(Paragraph("1. Soil Health & Nutritional Assessment", section_style))
        soil = advisory_data.get("soil", {})
        fert = advisory_data.get("fertilizer", {})

        soil_items = "<br/>".join([f"• {issue}" for issue in soil.get("issues", [])[:4]])
        fert_items = "<br/>".join([f"• {rec}" for rec in fert.get("recommendations", [])[:4]])

        comm_fert = fert.get("commercial_fertilizers", {})
        fert_box = (
            f"<b>Commercial Dosage Prescription:</b><br/>"
            f"• <b>Urea (46% N):</b> {comm_fert.get('urea_kg_ha', 0)} kg/ha<br/>"
            f"• <b>DAP (18% N, 46% P₂O₅):</b> {comm_fert.get('dap_kg_ha', 0)} kg/ha<br/>"
            f"• <b>MOP (60% K₂O):</b> {comm_fert.get('mop_kg_ha', 0)} kg/ha"
        )

        two_col_data = [
            [
                Paragraph("<b>Soil Condition Profile</b>", body_bold),
                Paragraph("<b>Fertilizer Guidance (NPK)</b>", body_bold),
            ],
            [
                Paragraph(
                    f"<b>Condition:</b> {soil.get('status', 'Good')} (Health Score: {soil.get('score', 80)}/100)<br/>"
                    f"<b>Texture:</b> {soil.get('soil_texture', 'Loamy')}<br/>"
                    f"<b>Reaction (pH):</b> {soil.get('ph', 6.5)} | <b>Organic Matter:</b> {soil.get('organic_matter', 3.0)}%<br/><br/>"
                    f"<b>Key Observations:</b><br/>{soil_items}",
                    table_cell,
                ),
                Paragraph(
                    f"{fert_box}<br/><br/>"
                    f"<b>Nutrient Deficits:</b> N: {fert.get('deficits', {}).get('N', 0)} kg/ha | "
                    f"P: {fert.get('deficits', {}).get('P', 0)} kg/ha | "
                    f"K: {fert.get('deficits', {}).get('K', 0)} kg/ha<br/><br/>"
                    f"<b>Advisory Notes:</b><br/>{fert_items}",
                    table_cell,
                ),
            ]
        ]
        two_col_table = Table(two_col_data, colWidths=[3.5 * inch, 3.7 * inch])
        two_col_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRAY),
            ("BACKGROUND", (0, 1), (-1, 1), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(two_col_table)
        story.append(Spacer(1, 10))

        # 4. Smart Irrigation & Multi-Hazard Risk
        story.append(Paragraph("2. Water Management & Environmental Risk Matrix", section_style))
        irrig = advisory_data.get("irrigation", {})
        risks = advisory_data.get("risks", {})

        irrig_actions = "<br/>".join([f"• {act}" for act in irrig.get("recommended_actions", [])[:3]])
        risk_warnings = "<br/>".join([f"• {r}" for r in risks.get("risks", [])[:3]])

        water_risk_data = [
            [
                Paragraph("<b>Smart Irrigation Advisory</b>", body_bold),
                Paragraph("<b>Hazard & Risk Assessment</b>", body_bold),
            ],
            [
                Paragraph(
                    f"<b>Priority:</b> {irrig.get('priority', 'Low')}<br/>"
                    f"<b>Soil Moisture:</b> {irrig.get('soil_moisture', 25)}%<br/>"
                    f"<b>Evapotranspiration Risk:</b> {irrig.get('evapotranspiration_risk', 'Normal')}<br/><br/>"
                    f"<b>Directive:</b> {irrig.get('message', 'Maintain adequate irrigation.')}<br/><br/>"
                    f"<b>Action Plan:</b><br/>{irrig_actions}",
                    table_cell,
                ),
                Paragraph(
                    f"<b>Overall Risk Status:</b> {risks.get('overall_risk_level', 'Normal')}<br/>"
                    f"<b>Active Warnings Count:</b> {risks.get('high_risk_count', 0)} High Severity<br/><br/>"
                    f"<b>Identified Environmental Factors:</b><br/>{risk_warnings}",
                    table_cell,
                ),
            ]
        ]
        water_risk_table = Table(water_risk_data, colWidths=[3.5 * inch, 3.7 * inch])
        water_risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRAY),
            ("BACKGROUND", (0, 1), (-1, 1), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(water_risk_table)
        story.append(Spacer(1, 10))

        # 5. Explainable AI (XAI) & Alternative Predictions Table
        story.append(Paragraph("3. Explainable AI Feature Attribution & Alternative Crops", section_style))
        raw_xai = prediction_result.get("important_features", [])
        if hasattr(raw_xai, "to_dict"):
            raw_xai = raw_xai.to_dict("records")
        xai_features = raw_xai[:4] if isinstance(raw_xai, list) else []

        raw_probs = prediction_result.get("probabilities", [])
        if hasattr(raw_probs, "to_dict"):
            raw_probs = raw_probs.to_dict("records")
        probs = raw_probs[:4] if isinstance(raw_probs, list) else []

        xai_rows = [[
            Paragraph("Top Influencing Feature", table_header),
            Paragraph("Impact", table_header),
            Paragraph("Direction", table_header),
            Paragraph("Alternative Crop", table_header),
            Paragraph("Probability", table_header),
        ]]

        for i in range(max(len(xai_features), len(probs))):
            f_item = xai_features[i] if i < len(xai_features) else {}
            p_item = probs[i] if i < len(probs) else {}

            f_name = f_item.get("feature", "-")
            try:
                f_imp = f"{float(f_item.get('impact_percentage', 0)):.1f}%" if f_item else "-"
            except (ValueError, TypeError):
                f_imp = str(f_item.get("impact_percentage", "-"))
            f_dir = f_item.get("direction", "-").capitalize() if f_item else "-"
            c_name = p_item.get("crop", "-").title() if p_item else "-"
            try:
                c_prob = f"{float(p_item.get('percentage', 0)):.1f}%" if p_item else "-"
            except (ValueError, TypeError):
                c_prob = str(p_item.get("percentage", "-"))

            xai_rows.append([
                Paragraph(f_name, table_cell),
                Paragraph(f_imp, table_cell),
                Paragraph(f_dir, table_cell),
                Paragraph(c_name, table_cell),
                Paragraph(c_prob, table_cell),
            ])

        xai_table = Table(xai_rows, colWidths=[2.2 * inch, 0.8 * inch, 1.0 * inch, 1.8 * inch, 1.4 * inch])
        xai_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_GREEN),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(xai_table)
        story.append(Spacer(1, 12))

        # 6. Disclaimer Footer
        story.append(HRFlowable(width="100%", thickness=1, color=BORDER_GRAY, spaceBefore=4, spaceAfter=6))
        disclaimer = (
            "<b>Agronomic Disclaimer:</b> This advisory is generated by the AgriSathi AI Engine based on "
            "input soil, meteorological, and farm parameters. Fertilizer dosages and chemical treatments "
            "should be cross-referenced with local agricultural extension services and verified against soil lab test reports."
        )
        story.append(Paragraph(disclaimer, ParagraphStyle("Disc", parent=body_style, fontSize=7.5, leading=10, textColor=colors.HexColor("#777777"))))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        return pdf_bytes

    except Exception as e:
        raise ReportGenerationError(f"Failed to generate PDF report: {e}") from e
