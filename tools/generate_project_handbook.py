"""Generate the beginner-friendly BuildSense AI project handbook PDF."""

from __future__ import annotations

import ast
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "buildsense-ai-complete-project-handbook.pdf"

NAVY = colors.HexColor("#10243B")
GREEN = colors.HexColor("#14885D")
MINT = colors.HexColor("#E9F7F0")
PALE = colors.HexColor("#F4F7FA")
BLUE = colors.HexColor("#3478B8")
AMBER = colors.HexColor("#D79323")
TEXT = colors.HexColor("#26384A")
MUTED = colors.HexColor("#647488")
BORDER = colors.HexColor("#D9E2E8")


def styles():
    """Create the document typography used throughout the handbook."""
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "CoverTitle", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=28, leading=33, textColor=colors.white, alignment=TA_LEFT,
            spaceAfter=10,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle", parent=base["BodyText"], fontName="Helvetica",
            fontSize=12, leading=18, textColor=colors.HexColor("#CDE8DB"),
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=20, leading=25, textColor=NAVY, spaceBefore=8,
            spaceAfter=12, keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=14, leading=18, textColor=GREEN, spaceBefore=10,
            spaceAfter=7, keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=11, leading=14, textColor=NAVY, spaceBefore=7,
            spaceAfter=4, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.2, leading=14, textColor=TEXT, spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "Small", parent=base["BodyText"], fontName="Helvetica",
            fontSize=7.8, leading=11, textColor=TEXT,
        ),
        "muted": ParagraphStyle(
            "Muted", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8.2, leading=12, textColor=MUTED, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9, leading=13.5, textColor=TEXT, leftIndent=14,
            firstLineIndent=-8, bulletIndent=3, spaceAfter=4,
        ),
        "step": ParagraphStyle(
            "Step", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8.5, leading=12.5, textColor=TEXT,
        ),
        "callout": ParagraphStyle(
            "Callout", parent=base["BodyText"], fontName="Helvetica-Bold",
            fontSize=9.2, leading=14, textColor=NAVY,
        ),
        "code": ParagraphStyle(
            "Code", parent=base["Code"], fontName="Courier",
            fontSize=7.7, leading=11, textColor=colors.HexColor("#E9F5EF"),
            backColor=NAVY, borderPadding=8, spaceAfter=8,
        ),
        "table_head": ParagraphStyle(
            "TableHead", parent=base["BodyText"], fontName="Helvetica-Bold",
            fontSize=7.5, leading=10, textColor=colors.white,
        ),
        "table": ParagraphStyle(
            "Table", parent=base["BodyText"], fontName="Helvetica",
            fontSize=7.2, leading=10, textColor=TEXT,
        ),
        "toc": ParagraphStyle(
            "TOC", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10, leading=16, textColor=TEXT, leftIndent=8,
        ),
    }


S = styles()


def P(text: str, style: str = "body") -> Paragraph:
    """Create an escaped ReportLab paragraph with basic bold-tag support."""
    safe = (
        escape(str(text))
        .replace("&lt;b&gt;", "<b>")
        .replace("&lt;/b&gt;", "</b>")
        .replace("&lt;br/&gt;", "<br/>")
    )
    return Paragraph(safe, S[style])


def heading(number: str, title: str) -> list:
    return [P(f"{number}. {title}", "h1")]


def bullets(items: list[str]) -> list:
    return [Paragraph(f"- {escape(item)}", S["bullet"]) for item in items]


def callout(title: str, text: str, color=MINT) -> Table:
    table = Table([[P(title, "callout"), P(text, "body")]], colWidths=[43 * mm, 125 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("BOX", (0, 0), (-1, -1), 0.6, GREEN),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def flow_row(items: list[tuple[str, str]]) -> Table:
    cells = []
    for index, (title, detail) in enumerate(items, 1):
        cells.append(P(f"<b>{index:02d} {title}</b><br/>{detail}", "step"))
    table = Table([cells], colWidths=[168 * mm / len(cells)] * len(cells))
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def data_table(headers: list[str], rows: list[list[str]], widths: list[float]) -> Table:
    data = [[P(item, "table_head") for item in headers]]
    data.extend([[P(item, "table") for item in row] for row in rows])
    table = Table(data, colWidths=[width * mm for width in widths], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def describe_file(path: str) -> str:
    """Return a beginner-friendly purpose for every project file."""
    exact = {
        "run.py": "Application entry point. Creates Flask and starts the local web server.",
        "requirements.txt": "List of Python libraries required to run and test the project.",
        ".env.example": "Safe template showing configuration names without real secrets.",
        "README.md": "Quick-start instructions, main features, APIs, and production notes.",
        "app/__init__.py": "Flask application factory. Registers routes and CSRF protection.",
        "app/routes/dashboard_routes.py": "HTML page routes, objective creation/deletion, and report downloads.",
        "app/routes/api_routes.py": "JSON API for health, readiness, objectives, executions, and approvals.",
        "app/routes/approval_routes.py": "Receives manager decisions from the review form.",
        "app/services/objective_service.py": "Validates objectives and performs safe cascade deletion.",
        "app/services/execution_service.py": "Starts background workflows and stores their final state.",
        "app/services/dashboard_service.py": "Combines database records for the dashboard templates.",
        "app/services/approval_service.py": "Validates and persists approve, modify, reject, and retry actions.",
        "app/services/pdf_report_service.py": "Turns an approved result into a branded PDF report.",
        "app/services/readiness_service.py": "Tests whether external services are configured and working.",
        "app/templates/base.html": "Shared HTML shell: navigation, alerts, delete dialog, footer, CSS, and JS.",
        "app/templates/dashboard.html": "New-objective form, scenario presets, statistics, filters, and history.",
        "app/templates/objective_detail.html": "Objective summary, workflow progress, and execution history.",
        "app/templates/recommendation_review.html": "Strategy, intelligence, final report, downloads, and approval controls.",
        "app/templates/decision_trail.html": "Human-readable audit trail of controller and agent decisions.",
        "app/static/css/style.css": "Complete responsive visual system for every web page.",
        "app/static/js/app.js": "Client interactions: presets, filters, dialogs, refresh, forms, and shortcuts.",
        "orchestration/graph_builder.py": "Compiles the LangGraph StateGraph and its conditional reason-act-observe routing.",
        "orchestration/nodes.py": "Controller and worker nodes for collect, retry, analyze, strategy, and cancel.",
        "orchestration/state.py": "Typed shared state passed between controller cycles.",
        "orchestration/retry_policies.py": "Rules limiting how many times evidence collection may retry.",
        "orchestration/hitl_node.py": "Final node that pauses execution for human review.",
        "core/execution_planner.py": "Builds adaptive research queries, tool priorities, and constraints.",
        "core/decision_trail_logger.py": "Writes controller decisions and evidence events to the audit trail.",
        "core/url_safety.py": "Rejects private, local, or unsafe URLs before scraping.",
        "core/utils.py": "Shared ID, time, text-cleaning, and number helper functions.",
        "core/exceptions.py": "Project-specific exception types.",
        "config/settings.py": "Loads `.env` values into one cached settings object.",
        "config/logging_config.py": "Defines application logging format and level.",
        "agents/data_collection_agent/agent.py": "Runs selected evidence tools and stores validated unique results.",
        "agents/data_collection_agent/validator.py": "Rejects incomplete or unusable evidence records.",
        "agents/data_collection_agent/deduplication.py": "Removes repeated evidence using normalized content.",
        "agents/data_collection_agent/retry_handler.py": "Retries temporary source failures within a fixed limit.",
        "agents/intelligence_analysis_agent/agent.py": "Creates the structured market intelligence report.",
        "agents/intelligence_analysis_agent/sentiment_analysis.py": "Estimates positive, negative, and neutral customer sentiment.",
        "agents/intelligence_analysis_agent/pain_point_extractor.py": "Finds recurring customer complaints and unmet needs.",
        "agents/intelligence_analysis_agent/trend_detector.py": "Finds repeated product and market themes.",
        "agents/intelligence_analysis_agent/purchase_intent_detector.py": "Detects language suggesting willingness to buy.",
        "agents/intelligence_analysis_agent/confidence_scorer.py": "Calculates evidence confidence from volume and quality.",
        "agents/intelligence_analysis_agent/spam_filter.py": "Removes low-quality or spam-like evidence.",
        "agents/intelligence_analysis_agent/language_detector.py": "Identifies the likely language of collected text.",
        "agents/business_strategy_agent/agent.py": "Creates recommendations and verifies every cited evidence ID.",
        "agents/business_strategy_agent/recommendation_builder.py": "Builds the standard final business report fields.",
        "agents/business_strategy_agent/strategy_generator.py": "Generates deterministic strategy alternatives.",
        "agents/business_strategy_agent/strategy_comparator.py": "Ranks candidate strategies by their scores.",
        "agents/business_strategy_agent/impact_estimator.py": "Normalizes impact values for comparison.",
        "schemas/objective_schema.py": "Validates business goals, markets, keywords, and public URLs.",
        "schemas/collection_schema.py": "Defines the normalized evidence record structure.",
        "schemas/intelligence_schema.py": "Defines the intelligence report contract.",
        "schemas/strategy_schema.py": "Defines strategies and the complete final-report contract.",
        "schemas/controller_schema.py": "Restricts AI controller output to legal structured actions.",
        "schemas/approval_schema.py": "Validates human decisions and required feedback.",
        "tools/tool_registry.py": "Lists enabled tools and explains when the planner should use them.",
        "tools/openai_client.py": "Calls OpenAI and requires structured JSON output.",
        "tools/google_places_client.py": "Retrieves public place and review information.",
        "tools/youtube_client.py": "Retrieves public YouTube discussion signals.",
        "tools/firecrawl_client.py": "Extracts content through the Firecrawl service.",
        "tools/scraper_client.py": "Scrapes safe public pages using direct HTTP and BeautifulSoup.",
        "tools/demo_preflight.py": "Runs presentation readiness checks before a live demo.",
        "tools/render_pdf_sample.py": "Builds a repeatable sample approved report for visual testing.",
        "prompts/planner_prompts.py": "Instructions used for research planning.",
        "prompts/intelligence_prompts.py": "Instructions for structured market intelligence generation.",
        "prompts/strategy_prompts.py": "Instructions for evidence-grounded strategy generation.",
        "prompts/recommendation_prompts.py": "Reusable recommendation wording and constraints.",
        "database/connection.py": "Connects to MongoDB or supplies the in-memory test database.",
    }
    if path in exact:
        return exact[path]
    if path.startswith("database/models/"):
        return "Creates a consistent MongoDB document for this record type."
    if path.startswith("database/repositories/"):
        return "Provides database queries for this record type using the shared repository."
    if path.startswith("agents/data_collection_agent/sources/"):
        return "Adapts this external source to the normalized evidence format."
    if path.startswith("tests/"):
        return "Automated verification for the behavior named by this test file."
    if path.startswith("docs/"):
        return "Project documentation or repeatable demonstration material."
    if path.endswith("__init__.py"):
        return "Marks this directory as an importable Python package."
    return "Supporting project file used by the surrounding module."


def project_files() -> list[str]:
    """List readable project files while excluding generated and secret content."""
    allowed = {".py", ".html", ".css", ".js", ".md", ".json", ".txt", ".example"}
    skipped_parts = {".venv", "__pycache__", "output", "tmp", ".git"}
    result = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in skipped_parts for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() in allowed or relative in {"requirements.txt", ".env.example"}:
            result.append(relative)
    return sorted(result)


def explain_symbol(name: str, kind: str, docstring: str | None) -> str:
    """Explain a class or function in simple language."""
    if docstring:
        return docstring.splitlines()[0].strip()
    known = {
        "__init__": "Creates the object and prepares the dependencies it will use.",
        "create_app": "Creates the Flask application and connects configuration, routes, and safeguards.",
        "csrf_context": "Creates or reuses the security token inserted into browser forms.",
        "protect_html_forms": "Checks the submitted security token before accepting an HTML form.",
        "index": "Loads the dashboard data and renders the main page.",
        "create_objective": "Reads new goal data, validates it, stores it, and starts an execution.",
        "objective_detail": "Loads one objective and its execution history.",
        "delete_objective": "Deletes a safe past objective and redirects to the dashboard.",
        "decision_trail": "Loads and renders the audit trail for one execution.",
        "recommendation_review": "Loads the evidence, analysis, strategy, and approval interface.",
        "approved_report": "Returns the approved execution data as a JSON download.",
        "approved_pdf_report": "Builds and returns the approved PDF download.",
        "health": "Reports whether the application is running and which integrations are configured.",
        "integration_readiness": "Runs live checks and reports which evidence services produce usable data.",
        "execution_status": "Returns the current status of one workflow execution.",
        "execution_details": "Returns the complete stored data bundle for one execution.",
        "approval": "Validates and applies a human decision through the JSON API.",
        "decide": "Processes the manager's decision submitted from the browser.",
        "start": "Creates an execution record and starts the workflow.",
        "_run": "Runs the controller graph and persists its outputs and final status.",
        "_run_with_context": "Runs background work inside the Flask application context.",
        "request_cancel": "Marks a running execution so the controller stops at its next decision.",
        "apply": "Validates, stores, and applies an approval or follow-up action.",
        "overview": "Builds portfolio records and dashboard status totals.",
        "build": "Creates the complete PDF in memory and returns its bytes.",
        "_story": "Builds the ordered PDF sections from the execution data.",
        "_page_decoration": "Draws the PDF header, footer, and page number.",
        "_strategy_comparison": "Creates the wrapping strategy comparison table.",
        "_final_business_report": "Creates the standard management-report table.",
        "check": "Tests database and external-tool readiness.",
        "run": "Performs this agent's main task and returns structured output.",
        "_local_analysis": "Creates deterministic market intelligence when AI output is unavailable.",
        "_validate_grounding": "Rejects strategy evidence IDs that were not present in the analysis.",
        "build_recommendation": "Creates all standard final-report sections from the objective and intelligence.",
        "generate_local_strategies": "Builds deterministic strategy alternatives for offline operation.",
        "rank_strategies": "Sorts candidate strategies from highest to lowest score.",
        "normalize_impact": "Converts an impact value into a consistent comparison form.",
        "deduplicate": "Removes repeated evidence records.",
        "with_retry": "Retries a temporary source failure within the configured limit.",
        "valid_item": "Checks whether one evidence record contains usable required data.",
        "validate_items": "Keeps only valid evidence records.",
        "collect": "Calls this source and converts its response into normalized evidence.",
        "analyze_sentiment": "Estimates customer sentiment from evidence text.",
        "extract_pain_points": "Finds common complaints and customer problems.",
        "detect_purchase_intent": "Finds language showing that customers may buy.",
        "detect_trends": "Finds repeated themes across evidence.",
        "score_confidence": "Calculates evidence confidence using quality and volume.",
        "filter_spam": "Removes weak, repeated, or spam-like text.",
        "detect_language": "Estimates the language used in a text item.",
        "controller_node": "Observes workflow state and selects exactly one legal next action.",
        "collect_node": "Runs one selected collection tool and merges its evidence.",
        "retry_collection_node": "Changes the collection approach for a broader retry.",
        "analyze_node": "Runs the intelligence agent on all collected evidence.",
        "strategy_node": "Runs the strategy agent and records the ranked comparison.",
        "cancel_node": "Ends an execution after a user cancellation request.",
        "human_review_node": "Pauses the workflow and marks it ready for management review.",
        "build_graph": "Returns the reusable controller runtime.",
        "invoke": "Repeats controller and worker actions until review or cancellation.",
        "build_execution_plan": "Creates adaptive queries, tool priorities, and constraints.",
        "validate_public_url": "Rejects private, local, malformed, and unsafe source URLs.",
        "new_id": "Creates a readable unique identifier with the requested prefix.",
        "utc_now": "Returns the current UTC timestamp.",
        "clean_text": "Normalizes whitespace and text for comparison or storage.",
        "clamp": "Keeps a number inside a minimum and maximum range.",
        "log": "Stores one transparent event in the decision trail.",
        "get_database": "Returns MongoDB or the in-memory database selected by settings.",
        "reset_memory_database": "Clears the in-memory database between automated tests.",
        "create": "Inserts one clean document into this repository.",
        "get": "Finds one record by its public identifier.",
        "get_one": "Returns the first database document matching a query.",
        "list": "Returns matching records ordered by creation time.",
        "update": "Updates matching fields and refreshes the modification timestamp.",
        "delete": "Deletes all records matching a query and returns the removed count.",
        "for_execution": "Returns records linked to one execution identifier.",
        "available": "Reports whether this integration has the configuration it needs.",
        "json_response": "Requests structured JSON from OpenAI and parses the response.",
        "search_reviews": "Searches Google Places for public business review evidence.",
        "search_comments": "Searches YouTube for public discussion evidence.",
        "scrape": "Extracts readable content from a safe public webpage.",
        "enabled_tools": "Builds the list of currently configured evidence tools.",
        "main": "Runs this module as a command-line utility.",
    }
    if name in known:
        return known[name]
    readable = name.strip("_").replace("_", " ")
    if kind == "Class":
        return f"Groups the data and behavior for {readable}."
    if name.startswith("_"):
        return f"Internal helper used to {readable}."
    return f"Performs the {readable} operation for this module."


def code_walkthrough() -> list[tuple[str, list[list[str]]]]:
    """Inspect production Python files and list their code units in source order."""
    sections = []
    roots = ["app", "agents", "orchestration", "core", "database", "schemas", "tools", "config"]
    paths = []
    for folder in roots:
        paths.extend((ROOT / folder).rglob("*.py"))
    paths.append(ROOT / "run.py")
    for path in sorted(paths):
        if "__pycache__" in path.parts or path.name == "__init__.py":
            continue
        relative = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        rows = []
        order = 1
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                rows.append([
                    str(order), f"class {node.name}", "Class",
                    explain_symbol(node.name, "Class", ast.get_docstring(node)),
                ])
                order += 1
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        rows.append([
                            str(order), f"{node.name}.{member.name}()", "Method",
                            explain_symbol(member.name, "Method", ast.get_docstring(member)),
                        ])
                        order += 1
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                rows.append([
                    str(order), f"{node.name}()", "Function",
                    explain_symbol(node.name, "Function", ast.get_docstring(node)),
                ])
                order += 1
        if not rows:
            rows = [["1", "Module declarations", "Constants/data", describe_file(relative)]]
        sections.append((relative, rows))
    return sections


def page_decoration(canvas, doc):
    """Draw the consistent header, footer, and page number."""
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 15 * mm, width, 15 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(18 * mm, height - 9.5 * mm, "BuildSense AI")
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#C8D6E1"))
    canvas.drawRightString(width - 18 * mm, height - 9.5 * mm, "Complete Project Handbook")
    canvas.setStrokeColor(BORDER)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(18 * mm, 9 * mm, "Beginner-friendly technical and workflow guide")
    canvas.drawRightString(width - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_story() -> list:
    story = []

    # Cover
    cover = Table([
        [P("BUILDSENSE AI", "cover_subtitle")],
        [P("Complete Project Handbook", "cover_title")],
        [P(
            "A beginner-friendly guide to the architecture, agents, workflow, "
            "database, user interface, reports, APIs, file structure, and build order.",
            "cover_subtitle",
        )],
        [Spacer(1, 22 * mm)],
        [P("Project type", "cover_subtitle")],
        [P("Autonomous Multi-Agent Business Intelligence Platform", "cover_title")],
        [Spacer(1, 10 * mm)],
        [P("Prepared from the actual BuildSense AI source code", "cover_subtitle")],
    ], colWidths=[170 * mm], rowHeights=[12 * mm, None, None, 25 * mm, 8 * mm, None, 12 * mm, None])
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("BOX", (0, 0), (-1, -1), 1, GREEN),
        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.extend([Spacer(1, 28 * mm), cover, PageBreak()])

    story += heading("1", "How to use this handbook")
    story += [
        P("This handbook is written for a person who is new to the project and may also be new to Flask, databases, APIs, and AI agents."),
        callout("Best reading order", "Read sections 2 to 8 first for the big picture. Use sections 9 to 13 while working with the code. Use the file reference in section 14 whenever you open an unfamiliar file."),
        P("Contents", "h2"),
    ]
    contents = [
        "2. Project idea in simple words", "3. Main users and outputs",
        "4. Complete end-to-end workflow", "5. System architecture",
        "6. Three-agent structure", "7. Controller and autonomy",
        "8. Data flow and MongoDB", "9. Backend routes and services",
        "10. Frontend pages and interactions", "11. Final report and PDF",
        "12. Safety, reliability, and fallbacks", "13. Recommended creation order",
        "14. File-by-file reference", "15. Code walkthrough one by one",
        "16. Running and testing", "17. Beginner glossary",
        "18. Limitations and production upgrades",
    ]
    story += [P(item, "toc") for item in contents]
    story.append(PageBreak())

    story += heading("2", "Project idea in simple words")
    story += [
        P("BuildSense AI helps a manager investigate a business question. The manager describes a goal, such as opening a pizza shop or improving pharmacy inventory. The system gathers public evidence, discovers what customers want, compares possible strategies, and presents a final report for human approval."),
        callout("Important idea", "The AI does not make the final business decision. It prepares evidence and recommendations. A human manager approves, modifies, rejects, or requests more work."),
        P("What problem does it solve?", "h2"),
    ]
    story += bullets([
        "Business decisions are often based on assumptions instead of customer evidence.",
        "Public information is spread across reviews, videos, websites, and directories.",
        "A manager needs a short, explainable recommendation rather than thousands of raw comments.",
        "Every recommendation should show its evidence, confidence, risks, and decision history.",
    ])
    story += [P("What the system produces", "h2")]
    story += bullets([
        "A market opportunity score and evidence confidence.",
        "Customer complaints, needs, trending products, and high-demand categories.",
        "Several business strategy options with scores, cost, impact, and risk.",
        "Marketing, operational, inventory, and launch recommendations.",
        "A transparent decision trail, approved JSON export, and professional PDF report.",
    ])

    story += heading("3", "Main users and outputs")
    roles = [
        ["Business manager", "Enters the goal, reviews evidence, and makes the final decision."],
        ["Controller", "Observes current state and selects exactly one legal next action."],
        ["Data Collection Agent", "Collects and normalizes public evidence."],
        ["Intelligence Agent", "Turns evidence into customer and market insights."],
        ["Strategy Agent", "Compares strategies and creates the final report."],
        ["Database", "Stores objectives, runs, evidence, reports, trails, and approvals."],
    ]
    story += [data_table(["Role", "Responsibility"], roles, [48, 120])]

    story += heading("4", "Complete end-to-end workflow")
    story += [P("The following sequence describes what happens from the first browser click to the final PDF.")]
    workflow = [
        ("User enters goal", "Title, description, industry, market, keywords, and optional URLs."),
        ("Flask validates", "Pydantic validates content and URL safety rules reject private URLs."),
        ("Objective stored", "A unique OBJ identifier is created and saved."),
        ("Execution starts", "A linked EXE record is created and a background worker begins."),
        ("Planner prepares", "Queries, tool priorities, constraints, and minimum evidence are selected."),
        ("Controller decides", "The reason-act-observe loop selects one currently legal action."),
        ("Agent 1 collects", "One source tool returns normalized evidence and tool metadata."),
        ("Evidence cleaned", "Invalid, repeated, or spam-like records are removed."),
        ("Controller observes", "Evidence count, attempted tools, errors, budgets, and retries are checked."),
        ("Agent 2 analyzes", "Sentiment, complaints, needs, trends, products, and confidence are produced."),
        ("Controller evaluates", "Low confidence can trigger broader collection; sufficient confidence continues."),
        ("Agent 3 strategizes", "Alternatives are generated, ranked, and checked against known evidence IDs."),
        ("Human reviews", "The workflow pauses at awaiting approval."),
        ("Decision stored", "Approve, modify, reject, more analysis, or restart is recorded."),
        ("Report downloaded", "Approved runs expose JSON data and a styled PDF."),
    ]
    for start in range(0, len(workflow), 3):
        story.extend([flow_row(workflow[start:start + 3]), Spacer(1, 4 * mm)])
    story += [
        callout("Why the controller repeats", "After every worker action, control returns to the controller. This allows the workflow to react to missing evidence, failures, confidence, budgets, and manager feedback."),
        PageBreak(),
    ]

    story += heading("5", "System architecture")
    architecture = [
        ("Browser", "Forms, dashboards, reports, approval controls"),
        ("Flask routes", "HTTP requests and responses"),
        ("Services", "Business rules and coordination"),
        ("Controller", "Reason - act - observe decisions"),
        ("Agents and tools", "Evidence, intelligence, strategy"),
        ("Repositories", "MongoDB or memory persistence"),
    ]
    story += [flow_row(architecture[:3]), Spacer(1, 4 * mm), flow_row(architecture[3:])]
    story += [
        P("Layer responsibilities", "h2"),
        data_table(
            ["Layer", "What belongs here", "What should not belong here"],
            [
                ["Templates/JavaScript", "Presentation and browser interaction", "Database queries or agent reasoning"],
                ["Routes", "Read request, call service, return response", "Complex business rules"],
                ["Services", "Application workflows and safety rules", "HTML layout"],
                ["Orchestration", "Action selection and agent sequencing", "Browser formatting"],
                ["Agents", "Evidence, intelligence, and strategy work", "HTTP routing"],
                ["Repositories", "Database reads and writes", "Business recommendation logic"],
                ["Schemas", "Validate structure and allowed values", "External API calls"],
            ],
            [31, 68, 69],
        ),
    ]

    story += heading("6", "Three-agent structure")
    agent_rows = [
        ["Agent 1 - Data Collection", "Objective + plan", "Normalized evidence, source errors, tool trace", "Google Places, YouTube, Firecrawl, scraper"],
        ["Agent 2 - Intelligence", "Objective + evidence", "Needs, complaints, sentiment, trends, products, confidence", "OpenAI or deterministic local analysis"],
        ["Agent 3 - Strategy", "Objective + intelligence", "Ranked strategies and final business report", "OpenAI or deterministic strategy builder"],
    ]
    story += [data_table(["Agent", "Input", "Output", "Engine/tools"], agent_rows, [37, 37, 58, 36])]
    story += [
        P("Agent 1 details", "h2"),
        P("The planner chooses tools that match the objective. Each source adapter converts different API responses into the same CollectedItem structure. The agent records tool name, source URL, text, timestamp, metadata, and a stable evidence ID."),
        P("Agent 2 details", "h2"),
        P("The intelligence agent removes weak material and summarizes repeated customer signals. Its confidence is not certainty; it expresses how adequate and consistent the available evidence appears."),
        P("Agent 3 details", "h2"),
        P("The strategy agent creates alternatives, ranks them, and validates grounding. If a strategy cites an evidence ID that was not present in the intelligence report, validation rejects the result. The final report always follows the same management structure."),
        callout("Fallback behavior", "If OpenAI is unavailable or returns invalid structured data, local deterministic logic keeps the demonstration functional and clearly identifies the analysis engine."),
    ]

    story += heading("7", "Controller and autonomy")
    story += [
        P("The controller is the central decision-maker for workflow sequencing. LangGraph StateGraph provides compiled state propagation and conditional routing, while the project-owned Python nodes contain the business decisions and agent work."),
        P("What the controller observes", "h2"),
    ]
    story += bullets([
        "Number of valid evidence records.",
        "Tools already attempted and tools still available.",
        "Collection retry count and source failures.",
        "Analysis confidence and recommendation availability.",
        "Controller cycle count, tool-call count, and elapsed time.",
        "Cancellation requests and manager feedback.",
    ])
    decision_rows = [
        ["Cancellation requested", "cancel"],
        ["Recommendation exists", "human_review"],
        ["Budget reached, no intelligence", "analyze available evidence"],
        ["Budget reached, intelligence exists", "generate strategy"],
        ["Confidence meets threshold", "strategy"],
        ["Confidence too low and retry available", "retry_collection"],
        ["Enough evidence", "analyze"],
        ["Unused tool remains", "collect from that tool"],
        ["No tool or retry remains", "analyze and disclose limitations"],
    ]
    story += [data_table(["Observed condition", "Controller action"], decision_rows, [105, 63])]
    story += [
        P("Optional AI controller", "h2"),
        P("When enabled, OpenAI may choose only from a bounded list of legal actions prepared by deterministic rules. Pydantic validates the response. An unknown action is rejected and the safe deterministic choice is used."),
    ]

    story += heading("8", "Data flow and MongoDB")
    data_rows = [
        ["objectives", "OBJ-*", "Business goal and market context"],
        ["executions", "EXE-*", "One workflow run, status, node, retry, parent run"],
        ["raw_data", "item_id", "Normalized public evidence"],
        ["intelligence", "execution_id", "Structured market analysis"],
        ["recommendations", "execution_id", "Strategies and final report"],
        ["decision_trail", "trail_id", "Controller and worker audit events"],
        ["approvals", "approval_id", "Human decision and feedback"],
    ]
    story += [
        data_table(["Collection", "Key", "Stored information"], data_rows, [43, 36, 89]),
        P("Relationships", "h2"),
        P("One objective can have multiple executions. Each execution can have evidence, one intelligence result, one recommendation, many trail events, and an approval. Follow-up analysis creates a child execution linked to its parent."),
        callout("Deletion rule", "A running objective cannot be deleted. A completed objective may be deleted, and the service removes every execution-linked child record before removing the execution and objective."),
        P("Memory mode", "h2"),
        P("Tests use a small in-memory database with MongoDB-like methods. Normal demonstrations should use MongoDB so records survive application restarts."),
    ]

    story += heading("9", "Backend routes and services")
    route_rows = [
        ["GET /", "Dashboard portfolio and new objective form"],
        ["POST /objectives", "Validate objective and start background execution"],
        ["GET /objectives/<id>", "Objective and execution history"],
        ["POST /objectives/<id>/delete", "Safely delete a past objective"],
        ["GET /executions/<id>/trail", "Decision trail page"],
        ["GET /executions/<id>/review", "Recommendation and approval page"],
        ["POST /executions/<id>/cancel", "Request workflow cancellation"],
        ["GET /executions/<id>/report.pdf", "Approved PDF download"],
        ["GET /api/health", "Basic application and integration status"],
        ["POST /api/readiness", "Live external-tool readiness test"],
    ]
    story += [
        data_table(["Route", "Purpose"], route_rows, [65, 103]),
        P("Why services exist", "h2"),
        P("Routes should remain small. A route translates HTTP data into a service call. Services contain reusable business rules such as creating executions, validating approval state, assembling dashboard data, and cascading deletion."),
    ]

    story += heading("10", "Frontend pages and interactions")
    frontend_rows = [
        ["Dashboard", "Create objectives, apply presets, view statistics, filter records, delete past records."],
        ["Objective detail", "Read the goal, inspect workflow stage, stop active work, and open each execution."],
        ["Decision trail", "Understand every controller decision, tool call, failure, retry, and result."],
        ["Recommendation review", "Inspect strategy, intelligence, final report, alternatives, and submit a decision."],
        ["Approved downloads", "Download a polished PDF or structured JSON data."],
    ]
    story += [
        data_table(["Page", "What the user does"], frontend_rows, [43, 125]),
        P("HTML templates receive prepared dictionaries from DashboardService. CSS provides the visual system and responsive layouts. JavaScript adds scenario presets, history filters, safe confirmation dialogs, source counters, automatic refresh, and form feedback."),
    ]

    story += heading("11", "Final report and PDF")
    report_fields = [
        "Business Goal", "Market Opportunity Score", "Confidence",
        "Data Sources Used", "Top Customer Complaints", "Trending Products",
        "High-Demand Categories", "Recommended Business Changes",
        "Marketing Recommendations", "Operational Improvements",
        "Target Market", "Overall Recommendation",
    ]
    story += [
        P("Every industry uses the same management-report structure. The values change according to the objective and evidence."),
        data_table(["Order", "Report section"], [[str(i), name] for i, name in enumerate(report_fields, 1)], [24, 144]),
        P("PDF generation flow", "h2"),
    ]
    story += bullets([
        "The review route checks that the execution is approved.",
        "DashboardService loads the objective, execution, evidence, intelligence, trail, and approval.",
        "PDFReportService creates styled ReportLab sections and tables.",
        "Flask returns the generated bytes with an attachment filename.",
        "The browser downloads the PDF without storing another database copy.",
    ])

    story += heading("12", "Safety, reliability, and fallbacks")
    safety_rows = [
        ["Pydantic schemas", "Reject missing fields and invalid score ranges."],
        ["CSRF tokens", "Protect browser forms from cross-site submission."],
        ["URL safety", "Reject localhost, private IPs, and unsafe redirects."],
        ["Evidence ID validation", "Prevent strategies from citing unknown records."],
        ["Controller budgets", "Limit cycles, tool calls, retries, and elapsed time."],
        ["Cancellation", "Stop at the next controller decision point."],
        ["Human approval", "Prevent AI output from becoming a final decision automatically."],
        ["Local fallback", "Continue with deterministic analysis when AI is unavailable."],
        ["Readiness check", "Distinguish configured integrations from actually working tools."],
    ]
    story += [data_table(["Safeguard", "Why it matters"], safety_rows, [51, 117])]

    story += heading("13", "Recommended project creation order")
    creation = [
        ("Define the problem", "Write the business objective, users, outputs, and approval requirement."),
        ("Create settings", "Add `.env.example`, settings loader, and logging."),
        ("Create schemas", "Define objective, evidence, intelligence, strategy, controller, and approval contracts."),
        ("Create database connection", "Support MongoDB and an in-memory test substitute."),
        ("Create data models", "Build document constructors for every collection."),
        ("Create repositories", "Add shared CRUD, then record-specific queries."),
        ("Create safety utilities", "IDs, timestamps, URL safety, and custom errors."),
        ("Create external clients", "OpenAI, Google Places, YouTube, Firecrawl, and scraper."),
        ("Create tool registry", "Expose only configured tools to planning."),
        ("Build Agent 1 helpers", "Validation, deduplication, retry, and source adapters."),
        ("Build Data Collection Agent", "Execute selected tools and normalize evidence."),
        ("Build Agent 2 helpers", "Spam, language, sentiment, pain points, intent, trends, confidence."),
        ("Build Intelligence Agent", "Create a complete structured analysis with fallback."),
        ("Build Agent 3 helpers", "Generate, compare, score, and format strategies."),
        ("Build Strategy Agent", "Ground citations and create the final report."),
        ("Build controller state", "Define data shared during an execution."),
        ("Build orchestration nodes", "Collect, retry, analyze, strategy, cancel, and review."),
        ("Build controller loop", "Observe results and select exactly one next action."),
        ("Build services", "Objective, execution, dashboard, approval, readiness, and PDF."),
        ("Build routes", "HTML pages first, then JSON API endpoints."),
        ("Build base frontend", "Navigation, alerts, global design, and JavaScript helpers."),
        ("Build dashboard", "Objective form, presets, statistics, filters, and delete controls."),
        ("Build detail and trail", "Workflow progress and explainability pages."),
        ("Build review page", "Strategy, report, approval controls, and downloads."),
        ("Add PDF export", "Generate, render, and visually inspect approved reports."),
        ("Add tests", "Cover agents, controller, routes, safety, deletion, scenarios, and PDF."),
        ("Add demo data and readiness", "Prepare repeatable presentation objectives and live checks."),
        ("Document and verify", "Run tests and keep this handbook synchronized with the code."),
    ]
    story += [data_table(["Step", "Create", "Reason"], [[str(i), a, b] for i, (a, b) in enumerate(creation, 1)], [14, 50, 104])]
    story.append(PageBreak())

    story += heading("14", "File-by-file reference")
    story += [
        P("The list below covers the readable project files. Generated output, caches, the virtual environment, Git internals, and secret `.env` values are intentionally excluded."),
    ]
    files = project_files()
    rows = [[str(i), path, describe_file(path)] for i, path in enumerate(files, 1)]
    story += [data_table(["No.", "File", "What it does"], rows, [12, 68, 88])]

    story.append(PageBreak())
    story += heading("15", "Code walkthrough one by one")
    story += [
        P(
            "This section opens each production Python module conceptually and "
            "explains its classes, functions, and methods in source-code order. "
            "Private helpers begin with an underscore. Methods are shown as "
            "ClassName.method()."
        ),
        callout(
            "How to study a file",
            "First read the file purpose. Then follow the numbered code units "
            "from top to bottom. Finally, search for where each public function "
            "is called to understand how data enters and leaves the file.",
        ),
    ]
    for file_path, code_rows in code_walkthrough():
        story += [
            P(file_path, "h2"),
            P(describe_file(file_path), "muted"),
            data_table(
                ["Order", "Code unit", "Type", "Beginner explanation"],
                code_rows,
                [12, 53, 22, 81],
            ),
            Spacer(1, 3 * mm),
        ]
    story += [
        P("Frontend code walkthrough", "h2"),
        data_table(
            ["File", "Read it in this order"],
            [
                [
                    "app/templates/base.html",
                    "1. HTML head and stylesheet. 2. Shared header navigation. "
                    "3. Flash messages. 4. Page content block. 5. Delete dialog. "
                    "6. Footer and JavaScript.",
                ],
                [
                    "app/templates/dashboard.html",
                    "1. Product hero and statistics. 2. Scenario selector. "
                    "3. Objective form. 4. Portfolio filters. 5. Objective cards "
                    "and safe delete forms.",
                ],
                [
                    "app/templates/objective_detail.html",
                    "1. Objective summary. 2. Workflow monitor. 3. Execution "
                    "history. 4. Status and decision-trail actions.",
                ],
                [
                    "app/templates/recommendation_review.html",
                    "1. Review header. 2. Approved download panel. 3. Recommended "
                    "strategy. 4. Standard final report. 5. Intelligence and "
                    "alternatives. 6. Human decision form.",
                ],
                [
                    "app/templates/decision_trail.html",
                    "1. Execution summary. 2. Ordered audit events. 3. Tool data "
                    "and reasoning. 4. Empty state.",
                ],
                [
                    "app/static/js/app.js",
                    "1. Shared DOM helpers. 2. Form validation/loading. 3. Auto "
                    "refresh. 4. Scenario presets. 5. History filters. 6. Delete "
                    "confirmation. 7. Keyboard and accessibility behavior.",
                ],
                [
                    "app/static/css/style.css",
                    "1. Color and spacing variables. 2. Base typography. 3. "
                    "Reusable controls/cards. 4. Page-specific layouts. 5. "
                    "Responsive media queries. 6. Print rules.",
                ],
            ],
            [55, 113],
        ),
    ]

    story += heading("16", "Running and testing")
    story += [
        P("Windows setup", "h2"),
        Paragraph(
            "cd C:\\Users\\Dilsh\\Desktop\\buildsense-ai-final<br/>"
            "python -m venv .venv<br/>"
            ".\\.venv\\Scripts\\Activate.ps1<br/>"
            "pip install -r requirements.txt<br/>"
            "copy .env.example .env<br/>"
            "python run.py",
            S["code"],
        ),
        P("Open http://127.0.0.1:5000 in the browser. Press Ctrl+F5 after frontend changes."),
        P("Testing", "h2"),
        Paragraph("python -m pytest -q", S["code"]),
        P("Before a presentation, configure MongoDB and the external API keys, run the live readiness endpoint, confirm at least three tools return usable evidence, and keep a second real objective ready."),
    ]

    story += heading("17", "Beginner glossary")
    glossary = [
        ["API", "A defined way for one program to request data from another."],
        ["Agent", "A component that receives a goal, performs a specialized task, and returns structured results."],
        ["Controller", "The component that chooses which agent action should happen next."],
        ["Flask", "The Python web framework serving pages and API endpoints."],
        ["Route", "A URL and function that handles a browser or API request."],
        ["Service", "Reusable application logic called by routes."],
        ["Schema", "A validated definition of required data fields and allowed values."],
        ["Repository", "A class that reads or writes one database collection."],
        ["MongoDB", "A document database that stores JSON-like records."],
        ["Evidence grounding", "Connecting a recommendation to known source records."],
        ["Confidence", "A score describing evidence adequacy, not a guarantee of success."],
        ["Fallback", "A safe alternative used when an external AI or source is unavailable."],
        ["CSRF", "A browser attack prevented here with a secret form token."],
        ["Human-in-the-loop", "A design where a human must review or control the final action."],
        ["Reason-act-observe", "Choose one action, run it, inspect the result, and decide again."],
    ]
    story += [data_table(["Term", "Simple meaning"], glossary, [42, 126])]

    story += heading("18", "Limitations and production upgrades")
    story += [
        P("BuildSense AI is a buildathon-ready MVP. It demonstrates the full intelligence workflow, but production deployment requires additional engineering."),
    ]
    story += bullets([
        "Add user accounts, roles, and organization-level access control.",
        "Replace local background threads with Celery, Redis, or another durable task queue.",
        "Add request rate limiting, centralized monitoring, and alerting.",
        "Store secrets in a managed secret service and rotate credentials.",
        "Add source-specific compliance, robots, licensing, and retention policies.",
        "Encrypt sensitive data and define backup and recovery procedures.",
        "Calibrate opportunity scores using historical outcomes instead of only evidence heuristics.",
        "Add financial models, competitor verification, and domain-expert review for real investment decisions.",
    ])
    story += [
        callout("Final understanding", "BuildSense AI is an evidence-to-decision system. Flask receives the goal, services start a controller execution, agents collect and analyze public evidence, the controller adapts the route, a strategy agent creates the standard report, MongoDB preserves traceability, and a human manager makes the final decision."),
    ]
    return story


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=21 * mm,
        rightMargin=21 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title="BuildSense AI Complete Project Handbook",
        author="BuildSense AI",
        subject="Beginner-friendly complete project architecture and workflow guide",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="content")
    doc.addPageTemplates([PageTemplate(id="handbook", frames=[frame], onPage=page_decoration)])
    doc.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()
