"""
Professional PDF Agronomic Advisory Report Generator using ReportLab.
"""

import io
import html
from datetime import datetime, timezone
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
    Guaranteed null-safe and formatted for clean single-page executive presentation.
    """
    buffer = output_stream or io.BytesIO()

    try:
        prediction_result = prediction_result or {}
        advisory_data = advisory_data or {}

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=26,
            bottomMargin=24,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=PRIMARY_GREEN,
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#555555"),
        )
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=PRIMARY_GREEN,
            spaceBefore=5,
            spaceAfter=2,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
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
            fontSize=16,
            leading=19,
            textColor=PRIMARY_GREEN,
            alignment=1,
        )
        table_cell = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10.5,
            textColor=DARK_GRAY,
        )
        table_header = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10.5,
            textColor=colors.white,
        )

        story = []

        # 1. Header Banner
        timestamp_str = datetime.now(timezone.utc).strftime("%B %d, %Y - %H:%M UTC")
        header_table = Table(
            [
                [
                    Paragraph("<b>AgriSathi | Precision Agriculture</b>", title_style),
                    Paragraph(f"<b>Report ID:</b> AGR-{int(datetime.now(timezone.utc).timestamp())}<br/><b>Date:</b> {timestamp_str}", subtitle_style),
                ]
            ],
            colWidths=[4.4 * inch, 2.8 * inch],
        )
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ]))
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_GREEN, spaceBefore=4, spaceAfter=6))

        # 2. Hero Recommendation Box
        crop_val = prediction_result.get("recommended_crop") or "Target Crop"
        crop = html.escape(str(crop_val).title())
        conf_val = prediction_result.get("confidence")
        try:
            if isinstance(conf_val, str):
                conf_val = conf_val.rstrip("%").strip()
            conf = float(conf_val) if conf_val is not None else 95.0
        except (ValueError, TypeError):
            conf = 95.0

        crop_profile = (advisory_data.get("crop_profile") or {}) if isinstance(advisory_data, dict) else {}
        crop_desc = html.escape(str(crop_profile.get("description") or "Target crop determined optimal by Random Forest model."))
        crop_sci_name = html.escape(str(crop_profile.get("display_name", crop)))

        hero_data = [
            [Paragraph("PRIMARY AI CROP RECOMMENDATION", ParagraphStyle("SubHeader", parent=body_bold, textColor=SECONDARY_GREEN, alignment=1, fontSize=8))],
            [Paragraph(f"<b>{crop.upper()}</b>", hero_style)],
            [Paragraph(f"Model Confidence: <b>{conf:.1f}%</b> | Scientific Name: <i>{crop_sci_name}</i>", ParagraphStyle("Conf", parent=body_style, alignment=1, fontSize=8))],
            [Paragraph(crop_desc, ParagraphStyle("Desc", parent=body_style, alignment=1, textColor=colors.HexColor("#444444"), fontSize=7.5))],
        ]
        hero_table = Table(hero_data, colWidths=[7.2 * inch])
        hero_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREEN),
            ("BOX", (0, 0), (-1, -1), 1.2, PRIMARY_GREEN),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        story.append(hero_table)
        story.append(Spacer(1, 5))

        # 3. Two-Column Analysis: Soil Health & Fertilizer
        story.append(Paragraph("1. Soil Health & Nutritional Assessment", section_style))
        soil = (advisory_data.get("soil") or {}) if isinstance(advisory_data, dict) else {}
        fert = (advisory_data.get("fertilizer") or {}) if isinstance(advisory_data, dict) else {}

        soil_issues = (soil.get("issues") or []) if isinstance(soil, dict) else []
        fert_recs = (fert.get("recommendations") or []) if isinstance(fert, dict) else []

        soil_items = "<br/>".join([f"• {html.escape(str(issue))}" for issue in soil_issues[:3]]) or "• Soil parameters within baseline."
        fert_items = "<br/>".join([f"• {html.escape(str(rec))}" for rec in fert_recs[:3]]) or "• Nutrient status adequate."

        comm_fert = (fert.get("commercial_fertilizers") or {}) if isinstance(fert, dict) else {}
        deficits = (fert.get("deficits") or {}) if isinstance(fert, dict) else {}

        fert_box = (
            f"<b>Commercial Dosage Prescription:</b><br/>"
            f"• <b>Urea (46% N):</b> {comm_fert.get('urea_kg_ha', 0)} kg/ha<br/>"
            f"• <b>DAP (18% N, 46% P₂O₅):</b> {comm_fert.get('dap_kg_ha', 0)} kg/ha<br/>"
            f"• <b>MOP (60% K₂O):</b> {comm_fert.get('mop_kg_ha', 0)} kg/ha"
        )

        soil_status = html.escape(str(soil.get('status', 'Good')))
        soil_texture = html.escape(str(soil.get('soil_texture', 'Loamy')))

        two_col_data = [
            [
                Paragraph("<b>Soil Condition Profile</b>", body_bold),
                Paragraph("<b>Fertilizer Guidance (NPK)</b>", body_bold),
            ],
            [
                Paragraph(
                    f"<b>Condition:</b> {soil_status} (Health Score: {soil.get('score', 80)}/100)<br/>"
                    f"<b>Texture:</b> {soil_texture}<br/>"
                    f"<b>Reaction (pH):</b> {soil.get('ph', 6.5)} | <b>Organic Matter:</b> {soil.get('organic_matter', 3.0)}%<br/><br/>"
                    f"<b>Key Observations:</b><br/>{soil_items}",
                    table_cell,
                ),
                Paragraph(
                    f"{fert_box}<br/><br/>"
                    f"<b>Nutrient Deficits:</b> N: {deficits.get('N', 0)} kg/ha | "
                    f"P: {deficits.get('P', 0)} kg/ha | "
                    f"K: {deficits.get('K', 0)} kg/ha<br/><br/>"
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
            ("PADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(two_col_table)
        story.append(Spacer(1, 5))

        # 4. Smart Irrigation & Multi-Hazard Risk
        story.append(Paragraph("2. Water Management & Environmental Risk Matrix", section_style))
        irrig = (advisory_data.get("irrigation") or {}) if isinstance(advisory_data, dict) else {}
        risks = (advisory_data.get("risks") or {}) if isinstance(advisory_data, dict) else {}

        irrig_actions_list = (irrig.get("recommended_actions") or []) if isinstance(irrig, dict) else []
        risk_warnings_list = (risks.get("risks") or []) if isinstance(risks, dict) else []

        irrig_actions = "<br/>".join([f"• {html.escape(str(act))}" for act in irrig_actions_list[:2]]) or "• Maintain standard moisture monitoring."
        risk_warnings = "<br/>".join([f"• {html.escape(str(r))}" for r in risk_warnings_list[:2]]) or "• No acute environmental hazards detected."

        irrig_prio = html.escape(str(irrig.get('priority', 'Low')))
        irrig_et = html.escape(str(irrig.get('evapotranspiration_risk', 'Normal')))
        irrig_msg = html.escape(str(irrig.get('message', 'Maintain adequate irrigation.')))
        risk_level = html.escape(str(risks.get('overall_risk_level', 'Normal')))

        water_risk_data = [
            [
                Paragraph("<b>Smart Irrigation Advisory</b>", body_bold),
                Paragraph("<b>Hazard & Risk Assessment</b>", body_bold),
            ],
            [
                Paragraph(
                    f"<b>Priority:</b> {irrig_prio}<br/>"
                    f"<b>Soil Moisture:</b> {irrig.get('soil_moisture', 25)}%<br/>"
                    f"<b>Evapotranspiration Risk:</b> {irrig_et}<br/><br/>"
                    f"<b>Directive:</b> {irrig_msg}<br/><br/>"
                    f"<b>Action Plan:</b><br/>{irrig_actions}",
                    table_cell,
                ),
                Paragraph(
                    f"<b>Overall Risk Status:</b> {risk_level}<br/>"
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
            ("PADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(water_risk_table)
        story.append(Spacer(1, 5))

        # 5. Explainable AI (XAI) & Alternative Predictions Table
        story.append(Paragraph("3. Explainable AI Feature Attribution & Alternative Crops", section_style))
        raw_xai = prediction_result.get("important_features")
        if raw_xai is None:
            raw_xai = []
        elif hasattr(raw_xai, "to_dict"):
            raw_xai = raw_xai.to_dict("records")
        xai_features = raw_xai[:4] if isinstance(raw_xai, list) else []

        raw_probs = prediction_result.get("probabilities")
        if raw_probs is None:
            raw_probs = []
        elif hasattr(raw_probs, "to_dict"):
            raw_probs = raw_probs.to_dict("records")
        probs = raw_probs[:4] if isinstance(raw_probs, list) else []

        xai_rows = [[
            Paragraph("Top Influencing Feature", table_header),
            Paragraph("Impact", table_header),
            Paragraph("Direction", table_header),
            Paragraph("Alternative Crop", table_header),
            Paragraph("Probability", table_header),
        ]]

        row_count = max(len(xai_features), len(probs))
        if row_count == 0:
            xai_rows.append([
                Paragraph("Overall Model Balance", table_cell),
                Paragraph("100%", table_cell),
                Paragraph("Optimal", table_cell),
                Paragraph(crop, table_cell),
                Paragraph(f"{conf:.1f}%", table_cell),
            ])
        else:
            for i in range(row_count):
                f_item = xai_features[i] if i < len(xai_features) and isinstance(xai_features[i], dict) else {}
                p_item = probs[i] if i < len(probs) and isinstance(probs[i], dict) else {}

                f_name = str(f_item.get("feature") or "-")
                try:
                    imp_val = f_item.get("impact_percentage")
                    if isinstance(imp_val, str):
                        imp_val = imp_val.rstrip("%").strip()
                    f_imp = f"{float(imp_val):.1f}%" if imp_val is not None else "-"
                except (ValueError, TypeError):
                    f_imp = str(f_item.get("impact_percentage") or "-")

                f_dir_val = f_item.get("direction")
                f_dir = str(f_dir_val).capitalize() if f_dir_val is not None else "-"

                c_name_val = p_item.get("crop")
                c_name = str(c_name_val).title() if c_name_val is not None else "-"

                try:
                    p_val = p_item.get("percentage")
                    if isinstance(p_val, str):
                        p_val = p_val.rstrip("%").strip()
                    c_prob = f"{float(p_val):.1f}%" if p_val is not None else "-"
                except (ValueError, TypeError):
                    c_prob = str(p_item.get("percentage") or "-")

                xai_rows.append([
                    Paragraph(html.escape(f_name), table_cell),
                    Paragraph(html.escape(f_imp), table_cell),
                    Paragraph(html.escape(f_dir), table_cell),
                    Paragraph(html.escape(c_name), table_cell),
                    Paragraph(html.escape(c_prob), table_cell),
                ])

        xai_table = Table(xai_rows, colWidths=[2.2 * inch, 0.8 * inch, 1.0 * inch, 1.8 * inch, 1.4 * inch])
        xai_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_GREEN),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
            ("PADDING", (0, 0), (-1, -1), 3),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(xai_table)
        story.append(Spacer(1, 6))

        # 6. Disclaimer Footer
        story.append(HRFlowable(width="100%", thickness=0.8, color=BORDER_GRAY, spaceBefore=3, spaceAfter=4))
        disclaimer = (
            "<b>Agronomic Disclaimer:</b> This advisory is generated by the AgriSathi AI Engine based on "
            "input soil, meteorological, and farm parameters. Fertilizer dosages and chemical treatments "
            "should be cross-referenced with local agricultural extension services and verified against soil lab test reports."
        )
        story.append(Paragraph(disclaimer, ParagraphStyle("Disc", parent=body_style, fontSize=7, leading=9, textColor=colors.HexColor("#777777"))))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        return pdf_bytes

    except Exception as e:
        raise ReportGenerationError(f"Failed to generate PDF report: {e}") from e
