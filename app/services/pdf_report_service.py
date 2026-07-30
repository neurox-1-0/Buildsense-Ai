"""Generate presentation-ready approved business reports with ReportLab."""

from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    PageBreak,
    Spacer,
    Table,
    TableStyle,
)


NAVY = colors.HexColor("#17233C")
BLUE = colors.HexColor("#2563EB")
LIGHT_BLUE = colors.HexColor("#EAF1FF")
SLATE = colors.HexColor("#475569")
LIGHT = colors.HexColor("#F5F7FB")
GREEN = colors.HexColor("#15803D")


class PDFReportService:
    def __init__(self) -> None:
        self.font, self.bold_font = self._register_fonts()
        self.styles = self._styles()

    def build(self, data: dict) -> bytes:
        buffer = BytesIO()
        document = BaseDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=22 * mm,
            bottomMargin=18 * mm,
            title="BuildSense AI Approved Intelligence Report",
            author="BuildSense AI",
        )
        frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height)
        document.addPageTemplates([
            PageTemplate(id="report", frames=[frame], onPage=self._page_decoration)
        ])
        document.build(self._story(data))
        return buffer.getvalue()

    def _story(self, data: dict) -> list:
        objective = data.get("objective") or {}
        execution = data.get("execution") or {}
        intelligence = data.get("intelligence") or {}
        recommendation = data.get("recommendation") or {}
        final_report = recommendation.get("final_business_report") or {}
        strategy = recommendation.get("recommended_strategy") or {}
        alternatives = recommendation.get("alternatives") or []
        evidence = data.get("evidence") or []
        trail = data.get("trail") or []
        approvals = data.get("approvals") or []

        story = [
            Spacer(1, 12 * mm),
            Paragraph("BUILDSENSE AI", self.styles["brand"]),
            Paragraph("Approved Business Intelligence Report", self.styles["cover_title"]),
            Paragraph(self._p(objective.get("title", "Business objective")), self.styles["cover_subtitle"]),
            Spacer(1, 8 * mm),
            self._summary_table(execution, recommendation, evidence),
            Spacer(1, 10 * mm),
            Paragraph(
                "This report records the evidence, analysis, autonomous decisions, "
                "recommended strategy, and final human approval for this execution.",
                self.styles["lead"],
            ),
            Spacer(1, 26 * mm),
            Paragraph(
                f"Execution ID: {self._plain(execution.get('execution_id', ''))}<br/>"
                f"Generated: {self._plain(execution.get('updated_at') or execution.get('created_at', ''))}",
                self.styles["small"],
            ),
            PageBreak(),
            self._heading("1. Business objective"),
            self._label_value("Objective", objective.get("title")),
            self._label_value("Description", objective.get("description")),
            self._two_column_details([
                ("Industry", objective.get("industry")),
                ("Target market", objective.get("target_market")),
                ("Status", execution.get("status")),
                ("Human guidance", execution.get("human_guidance") or "None"),
            ]),
            Spacer(1, 5 * mm),
            self._heading("2. Executive recommendation"),
            Paragraph(self._p(recommendation.get("summary", "No summary available.")), self.styles["body"]),
            Spacer(1, 4 * mm),
            self._strategy_card(strategy, primary=True),
        ]

        if alternatives:
            story += [
                Spacer(1, 5 * mm),
                Paragraph("Alternative strategies", self.styles["subheading"]),
                self._strategy_comparison(alternatives),
            ]

        if final_report:
            story += [
                PageBreak(),
                self._heading("3. Final business launch blueprint"),
                *self._final_business_report(final_report),
            ]

        story += [
            Spacer(1, 6 * mm),
            self._heading("4. Market intelligence"),
            Paragraph(self._p(intelligence.get("summary", "No intelligence summary available.")), self.styles["body"]),
            Spacer(1, 3 * mm),
            self._two_column_details([
                ("Overall sentiment", intelligence.get("overall_sentiment")),
                ("Analysis confidence", self._percent(intelligence.get("confidence"))),
                ("Analysis engine", intelligence.get("analysis_engine")),
                ("Decision readiness", intelligence.get("decision_readiness") or "Not assessed"),
            ]),
            Spacer(1, 4 * mm),
            KeepTogether([
                Paragraph("Detected trends", self.styles["subheading"]),
                *self._bullets(intelligence.get("trends") or ["No strong trend was detected."]),
            ]),
        ]

        if intelligence.get("verified_signals"):
            story += [
                Spacer(1, 3 * mm),
                Paragraph("Verified evidence signals", self.styles["subheading"]),
                *self._bullets([
                    f"{item.get('signal', '')} — {item.get('interpretation', '')}"
                    for item in intelligence["verified_signals"][:6]
                ]),
            ]
        if intelligence.get("opportunity_insights"):
            story += [
                Spacer(1, 3 * mm),
                Paragraph("Opportunities to test", self.styles["subheading"]),
                *self._bullets([
                    f"{item.get('opportunity', '')}: {item.get('recommended_test', '')}"
                    for item in intelligence["opportunity_insights"][:5]
                ]),
            ]
        if intelligence.get("contradictions"):
            story += [
                Spacer(1, 3 * mm),
                Paragraph("Contradictions and cautions", self.styles["subheading"]),
                *self._bullets(intelligence["contradictions"][:6]),
            ]
        if intelligence.get("research_gaps"):
            story += [
                Spacer(1, 3 * mm),
                Paragraph("Evidence gaps and next research", self.styles["subheading"]),
                *self._bullets([
                    f"{item.get('missing_information', '')}: {item.get('next_research_action', '')}"
                    for item in intelligence["research_gaps"][:5]
                ]),
            ]
        story += [
            Spacer(1, 6 * mm),
            self._heading("5. Supporting evidence"),
        ]

        for index, item in enumerate(evidence[:30], 1):
            metadata = item.get("metadata") or {}
            story.append(KeepTogether([
                Paragraph(
                    f"{index}. {self._p(item.get('title') or 'Untitled evidence')}",
                    self.styles["evidence_title"],
                ),
                Paragraph(
                    f"Source: {self._p(item.get('source', 'unknown'))} | "
                    f"Evidence ID: {self._p(item.get('item_id', ''))} | "
                    f"Demo data: {'Yes' if metadata.get('is_demo') else 'No'}",
                    self.styles["meta"],
                ),
                Paragraph(self._p((item.get("content") or "")[:1200]), self.styles["evidence"]),
                Paragraph(self._p(item.get("url") or "No source URL"), self.styles["url"]),
                Spacer(1, 3 * mm),
            ]))

        story += [
            PageBreak(),
            self._heading("6. Autonomous decision trail"),
        ]
        for index, item in enumerate(trail, 1):
            story.append(KeepTogether([
                Paragraph(
                    f"{index}. {self._p((item.get('step') or 'step').replace('_', ' ').title())}",
                    self.styles["trail_title"],
                ),
                Paragraph(self._p(item.get("message", "")), self.styles["body"]),
                Paragraph(self._p(item.get("created_at", "")), self.styles["meta"]),
                Spacer(1, 3 * mm),
            ]))

        story += [
            Spacer(1, 4 * mm),
            self._heading("7. Human approval"),
        ]
        if approvals:
            for approval in approvals:
                story += [
                    self._two_column_details([
                        ("Decision", approval.get("action")),
                        ("Decision time", approval.get("created_at")),
                        ("Feedback", approval.get("feedback") or "None"),
                        ("Modified summary", approval.get("modified_summary") or "None"),
                    ]),
                    Spacer(1, 4 * mm),
                ]
        else:
            story.append(Paragraph("No approval record was available.", self.styles["body"]))

        story += [
            Spacer(1, 7 * mm),
            Paragraph(
                "Decision note",
                self.styles["subheading"],
            ),
            Paragraph(
                "Recommendations are evidence-informed management inputs, not guarantees. "
                "Validate financial, legal, operational, and market assumptions before implementation.",
                self.styles["note"],
            ),
        ]
        return story

    def _page_decoration(self, canvas, document) -> None:
        canvas.saveState()
        width, height = A4
        canvas.setFillColor(NAVY)
        canvas.rect(0, height - 13 * mm, width, 13 * mm, stroke=0, fill=1)
        canvas.setFont(self.bold_font, 9)
        canvas.setFillColor(colors.white)
        canvas.drawString(18 * mm, height - 8.5 * mm, "BuildSense AI")
        canvas.setFont(self.font, 8)
        canvas.setFillColor(SLATE)
        canvas.drawString(18 * mm, 9 * mm, "Approved business intelligence report")
        canvas.drawRightString(width - 18 * mm, 9 * mm, f"Page {document.page}")
        canvas.restoreState()

    def _summary_table(self, execution: dict, recommendation: dict, evidence: list) -> Table:
        values = [
            ("STATUS", str(execution.get("status", "")).replace("_", " ").title()),
            ("CONFIDENCE", self._percent(recommendation.get("confidence"))),
            ("EVIDENCE", str(len(evidence))),
            ("PRODUCTIVE TOOLS", str(execution.get("productive_tool_count", 0))),
        ]
        cells = []
        for label, value in values:
            cells.append(Paragraph(
                f"<font size='7' color='#64748B'>{escape(label)}</font><br/>"
                f"<font size='13' color='#17233C'><b>{escape(value)}</b></font>",
                self.styles["metric"],
            ))
        table = Table([cells], colWidths=[document_width() / 4] * 4)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E1EC")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E1EC")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        return table

    def _strategy_card(self, strategy: dict, primary: bool = False) -> Table:
        confidence = [
            ["Expected impact", strategy.get("expected_impact", "")],
            ["Implementation cost", strategy.get("implementation_cost", "")],
            ["Risk", strategy.get("risk", "")],
            ["Score", str(strategy.get("score", ""))],
        ]
        content = [
            Paragraph(self._p(strategy.get("title", "No strategy available")), self.styles["strategy_title"]),
            Paragraph(self._p(strategy.get("description", "")), self.styles["body"]),
            Table(confidence, colWidths=[42 * mm, 118 * mm], style=[
                ("FONTNAME", (0, 0), (-1, -1), self.font),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TEXTCOLOR", (0, 0), (0, -1), SLATE),
                ("TEXTCOLOR", (1, 0), (1, -1), NAVY),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]),
            Paragraph(f"<b>Why:</b> {self._p(strategy.get('justification', ''))}", self.styles["note"]),
            Paragraph(
                f"<b>Evidence IDs:</b> {self._p(', '.join(strategy.get('evidence_ids') or []) or 'None')}",
                self.styles["meta"],
            ),
        ]
        table = Table([[content]], colWidths=[document_width()])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE if primary else LIGHT),
            ("BOX", (0, 0), (-1, -1), 1, BLUE if primary else colors.HexColor("#CBD5E1")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ]))
        return table

    def _strategy_comparison(self, alternatives: list[dict]) -> Table:
        # Every cell is a Paragraph so long model-generated values wrap inside
        # their column instead of painting over the neighboring column.
        rows = [[
            Paragraph(label, self.styles["table_header"])
            for label in ["Strategy", "Impact", "Cost", "Risk", "Score"]
        ]]
        for item in alternatives:
            rows.append([
                Paragraph(self._p(item.get("title", "")), self.styles["table"]),
                Paragraph(self._p(item.get("expected_impact")), self.styles["table"]),
                Paragraph(self._p(item.get("implementation_cost")), self.styles["table"]),
                Paragraph(self._p(item.get("risk")), self.styles["table"]),
                Paragraph(self._p(item.get("score")), self.styles["table"]),
            ])
        table = Table(
            rows,
            colWidths=[55 * mm, 42 * mm, 28 * mm, 22 * mm, 17 * mm],
            repeatRows=1,
        )
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        return table

    def _final_business_report(self, report: dict) -> list:
        def cell(label: str, value: str) -> Paragraph:
            return Paragraph(
                f"<font color='#64748B' size='8'>{escape(label.upper())}</font><br/>"
                f"<font color='#17233C'>{value}</font>",
                self.styles["detail"],
            )

        def bullets(values: list) -> str:
            return "<br/>".join(f"- {self._p(item)}" for item in values) or "Not identified"

        rows = [
            [
                cell("Business goal", self._p(report.get("business_goal", ""))),
                "",
            ],
            [
                cell("Market opportunity score", f"{self._plain(report.get('opportunity_score', 0))}%"),
                cell("Confidence", f"{self._plain(report.get('confidence', 0))}%"),
            ],
            [
                cell("Data sources used", bullets(report.get("data_sources_used", []))),
                cell("Top customer complaints", bullets(report.get("top_customer_complaints", []))),
            ],
            [
                cell("Trending products", bullets(report.get("trending_products", []))),
                cell("High-demand categories", bullets(report.get("high_demand_categories", []))),
            ],
            [
                cell("Recommended business changes", bullets(report.get("recommended_business_changes", []))),
                cell("Marketing recommendations", bullets(report.get("marketing_recommendations", []))),
            ],
            [
                cell("Operational improvements", bullets(report.get("operational_improvements", []))),
                cell("Target market", bullets(report.get("target_markets", []))),
            ],
            [
                Paragraph(
                    f"<font color='#9FE3BF' size='8'>OVERALL RECOMMENDATION</font><br/>"
                    f"<font color='#FFFFFF'>{self._p(report.get('overall_recommendation', ''))}</font>",
                    self.styles["detail"],
                ),
                "",
            ],
        ]
        summary_table = Table(rows, colWidths=[document_width() / 2] * 2)
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
            ("BOX", (0, 0), (-1, -1), 0.8, BLUE),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFD0F7")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("SPAN", (0, 0), (1, 0)),
            ("SPAN", (0, -1), (1, -1)),
            ("BACKGROUND", (0, -1), (1, -1), NAVY),
            ("TEXTCOLOR", (0, -1), (1, -1), colors.white),
        ]))
        flowables = [summary_table, Spacer(1, 6 * mm)]
        requirement_answers = report.get("requirement_answers", [])
        if requirement_answers:
            flowables.append(self._heading("Your requirements answered"))
            for index, answer in enumerate(requirement_answers, 1):
                answer_content = [
                    Paragraph(
                        f"{index}. {self._p(answer.get('requirement', 'Requested decision'))}",
                        self.styles["subheading"],
                    ),
                    Paragraph(
                        f"<b>Recommendation:</b> {self._p(answer.get('recommendation', ''))}",
                        self.styles["body"],
                    ),
                    Paragraph(
                        f"<b>Why:</b> {self._p(answer.get('rationale', ''))}<br/>"
                        f"<b>Confidence:</b> {self._plain(round(float(answer.get('confidence', 0)) * 100))}%<br/>"
                        f"<b>Validate:</b> {self._p(answer.get('validation_needed', '') or 'No additional validation specified')}",
                        self.styles["note"],
                    ),
                    Spacer(1, 4 * mm),
                ]
                flowables.append(KeepTogether(answer_content))

        dynamic_sections = report.get("dynamic_sections", [])
        if dynamic_sections:
            flowables.append(self._heading("Tailored decision plan"))
            for section in dynamic_sections:
                values = section.get("recommendations", [])
                flowables.append(KeepTogether([
                    Paragraph(self._p(section.get("title", "Decision section")), self.styles["subheading"]),
                    Paragraph(self._p(section.get("purpose", "")), self.styles["small"]),
                    *self._bullets(values or ["Complete live validation before finalizing this section."]),
                    Paragraph(
                        f"<b>Success measure:</b> {self._p(section.get('success_measure', '') or 'Define a measurable validation threshold.')}",
                        self.styles["note"],
                    ),
                    Spacer(1, 4 * mm),
                ]))
        else:
            blueprint_sections = [
                ("Location strategy", report.get("location_recommendations", [])),
                ("Target audience profiles", report.get("audience_profiles", [])),
                ("Product and service portfolio", report.get("product_portfolio", [])),
                ("Pricing and unit economics", report.get("pricing_strategy", [])),
                ("Customer experience plan", report.get("customer_experience_plan", [])),
                ("Technology and measurement", report.get("technology_plan", [])),
                ("Financial assumptions to validate", report.get("financial_assumptions", [])),
                ("90-day launch roadmap", report.get("ninety_day_plan", [])),
                ("Success metrics", report.get("success_metrics", [])),
                ("Immediate next actions", report.get("immediate_next_actions", [])),
            ]
            for title, values in blueprint_sections:
                if values:
                    flowables.append(KeepTogether([
                        Paragraph(self._p(title), self.styles["subheading"]),
                        *self._bullets(values),
                        Spacer(1, 4 * mm),
                    ]))
        return flowables

    def _two_column_details(self, values: list[tuple[str, object]]) -> Table:
        rows = []
        for index in range(0, len(values), 2):
            pair = values[index:index + 2]
            row = []
            for label, value in pair:
                row.append(Paragraph(
                    f"<font color='#64748B' size='8'>{escape(str(label).upper())}</font><br/>"
                    f"<font color='#17233C'>{self._p(value or 'Not specified')}</font>",
                    self.styles["detail"],
                ))
            while len(row) < 2:
                row.append("")
            rows.append(row)
        table = Table(rows, colWidths=[document_width() / 2] * 2)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E1EC")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E1EC")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        return table

    def _label_value(self, label: str, value: object) -> KeepTogether:
        return KeepTogether([
            Paragraph(self._p(label), self.styles["label"]),
            Paragraph(self._p(value or "Not specified"), self.styles["body"]),
            Spacer(1, 3 * mm),
        ])

    def _heading(self, text: str) -> Paragraph:
        return Paragraph(self._p(text), self.styles["heading"])

    def _bullets(self, values: list[object]) -> list:
        return [
            Paragraph(f"- {self._p(value)}", self.styles["bullet"])
            for value in values
        ]

    def _styles(self) -> dict[str, ParagraphStyle]:
        base = getSampleStyleSheet()
        return {
            "brand": ParagraphStyle("brand", parent=base["Normal"], fontName=self.bold_font, fontSize=10, textColor=BLUE, spaceAfter=7),
            "cover_title": ParagraphStyle("cover_title", parent=base["Title"], fontName=self.bold_font, fontSize=27, leading=32, textColor=NAVY, alignment=TA_LEFT, spaceAfter=10),
            "cover_subtitle": ParagraphStyle("cover_subtitle", parent=base["Normal"], fontName=self.font, fontSize=14, leading=20, textColor=SLATE, spaceAfter=10),
            "lead": ParagraphStyle("lead", parent=base["Normal"], fontName=self.font, fontSize=11, leading=17, textColor=SLATE),
            "heading": ParagraphStyle("heading", parent=base["Heading1"], fontName=self.bold_font, fontSize=16, leading=20, textColor=NAVY, spaceBefore=3, spaceAfter=8, borderColor=BLUE, borderWidth=0, borderPadding=0),
            "subheading": ParagraphStyle("subheading", parent=base["Heading2"], fontName=self.bold_font, fontSize=11, leading=15, textColor=NAVY, spaceBefore=3, spaceAfter=5),
            "strategy_title": ParagraphStyle("strategy_title", parent=base["Heading2"], fontName=self.bold_font, fontSize=15, leading=19, textColor=NAVY, spaceAfter=6),
            "body": ParagraphStyle("body", parent=base["BodyText"], fontName=self.font, fontSize=9, leading=14, textColor=colors.HexColor("#25324A")),
            "small": ParagraphStyle("small", parent=base["BodyText"], fontName=self.font, fontSize=8, leading=12, textColor=SLATE),
            "meta": ParagraphStyle("meta", parent=base["BodyText"], fontName=self.font, fontSize=7.5, leading=11, textColor=SLATE),
            "url": ParagraphStyle("url", parent=base["BodyText"], fontName=self.font, fontSize=7, leading=10, textColor=BLUE),
            "note": ParagraphStyle("note", parent=base["BodyText"], fontName=self.font, fontSize=8.5, leading=13, textColor=SLATE, backColor=LIGHT, borderPadding=6),
            "label": ParagraphStyle("label", parent=base["Normal"], fontName=self.bold_font, fontSize=8, leading=10, textColor=SLATE, spaceAfter=2),
            "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontName=self.font, fontSize=9, leading=14, leftIndent=4 * mm, firstLineIndent=-3 * mm, textColor=colors.HexColor("#25324A")),
            "evidence_title": ParagraphStyle("evidence_title", parent=base["Heading3"], fontName=self.bold_font, fontSize=10, leading=14, textColor=NAVY, spaceAfter=2),
            "evidence": ParagraphStyle("evidence", parent=base["BodyText"], fontName=self.font, fontSize=8.2, leading=12, textColor=colors.HexColor("#334155"), leftIndent=4 * mm, borderColor=colors.HexColor("#CBD5E1"), borderWidth=0, borderPadding=5, backColor=LIGHT),
            "trail_title": ParagraphStyle("trail_title", parent=base["Heading3"], fontName=self.bold_font, fontSize=9.5, leading=13, textColor=BLUE, spaceAfter=2),
            "metric": ParagraphStyle("metric", parent=base["Normal"], fontName=self.font, alignment=TA_CENTER, leading=16),
            "detail": ParagraphStyle("detail", parent=base["Normal"], fontName=self.font, fontSize=9, leading=13),
            "table": ParagraphStyle("table", parent=base["Normal"], fontName=self.font, fontSize=8, leading=11),
            "table_header": ParagraphStyle(
                "table_header",
                parent=base["Normal"],
                fontName=self.bold_font,
                fontSize=8,
                leading=10,
                textColor=colors.white,
            ),
        }

    @staticmethod
    def _register_fonts() -> tuple[str, str]:
        candidates = [
            (
                Path("C:/Windows/Fonts/arial.ttf"),
                Path("C:/Windows/Fonts/arialbd.ttf"),
            ),
            (
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ),
        ]
        for regular, bold in candidates:
            if regular.exists() and bold.exists():
                pdfmetrics.registerFont(TTFont("BuildSenseSans", str(regular)))
                pdfmetrics.registerFont(TTFont("BuildSenseSansBold", str(bold)))
                return "BuildSenseSans", "BuildSenseSansBold"
        return "Helvetica", "Helvetica-Bold"

    @staticmethod
    def _plain(value: object) -> str:
        return str(value if value is not None else "")

    @staticmethod
    def _p(value: object) -> str:
        return escape(str(value if value is not None else "")).replace("\n", "<br/>")

    @staticmethod
    def _percent(value: object) -> str:
        try:
            return f"{float(value) * 100:.0f}%"
        except (TypeError, ValueError):
            return "N/A"


def document_width() -> float:
    return A4[0] - 36 * mm
