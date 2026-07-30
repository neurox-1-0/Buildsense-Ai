"""Generate a focused PDF explaining the project's most important code."""

from __future__ import annotations

import ast
from html import escape
from pathlib import Path
import textwrap

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "buildsense-ai-important-code-explained.pdf"

NAVY = colors.HexColor("#10243B")
GREEN = colors.HexColor("#14885D")
MINT = colors.HexColor("#E9F7F0")
LIGHT = colors.HexColor("#F4F7FA")
TEXT = colors.HexColor("#26384A")
MUTED = colors.HexColor("#647488")
BORDER = colors.HexColor("#D8E1E8")

base = getSampleStyleSheet()
STYLES = {
    "cover": ParagraphStyle(
        "Cover", parent=base["Title"], fontName="Helvetica-Bold",
        fontSize=27, leading=33, textColor=colors.white,
    ),
    "cover_small": ParagraphStyle(
        "CoverSmall", parent=base["BodyText"], fontName="Helvetica",
        fontSize=11, leading=17, textColor=colors.HexColor("#CFE8DD"),
    ),
    "h1": ParagraphStyle(
        "H1", parent=base["Heading1"], fontName="Helvetica-Bold",
        fontSize=19, leading=24, textColor=NAVY, spaceAfter=10,
    ),
    "h2": ParagraphStyle(
        "H2", parent=base["Heading2"], fontName="Helvetica-Bold",
        fontSize=13, leading=17, textColor=GREEN, spaceBefore=7, spaceAfter=6,
    ),
    "body": ParagraphStyle(
        "Body", parent=base["BodyText"], fontName="Helvetica",
        fontSize=9.1, leading=13.5, textColor=TEXT, spaceAfter=6,
    ),
    "small": ParagraphStyle(
        "Small", parent=base["BodyText"], fontName="Helvetica",
        fontSize=7.6, leading=10.5, textColor=TEXT,
    ),
    "muted": ParagraphStyle(
        "Muted", parent=base["BodyText"], fontName="Helvetica",
        fontSize=8, leading=11.5, textColor=MUTED, spaceAfter=5,
    ),
    "code": ParagraphStyle(
        "Code", parent=base["Code"], fontName="Courier",
        fontSize=6.5, leading=9, textColor=colors.HexColor("#E9F3EE"),
    ),
    "head": ParagraphStyle(
        "Head", parent=base["BodyText"], fontName="Helvetica-Bold",
        fontSize=7.6, leading=10, textColor=colors.white,
    ),
    "table": ParagraphStyle(
        "Table", parent=base["BodyText"], fontName="Helvetica",
        fontSize=7.5, leading=10.5, textColor=TEXT,
    ),
}


def P(text: str, style: str = "body") -> Paragraph:
    safe = (
        escape(str(text))
        .replace("&lt;b&gt;", "<b>")
        .replace("&lt;/b&gt;", "</b>")
        .replace("&lt;br/&gt;", "<br/>")
    )
    return Paragraph(safe, STYLES[style])


def source_symbol(relative_path: str, symbol: str, max_lines: int = 34) -> tuple[int, list[str]]:
    """Extract one real function, class, or method from the current source."""
    source = (ROOT / relative_path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    target = None
    if "." in symbol:
        class_name, member_name = symbol.split(".", 1)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                target = next(
                    (
                        child for child in node.body
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and child.name == member_name
                    ),
                    None,
                )
                break
    else:
        target = next(
            (
                node for node in tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                and node.name == symbol
            ),
            None,
        )
    if target is None:
        raise ValueError(f"{symbol} not found in {relative_path}")
    lines = source.splitlines()[target.lineno - 1:target.end_lineno]
    if len(lines) > max_lines:
        head = max_lines - 5
        lines = lines[:head] + ["    # ... remaining implementation omitted for focus ..."] + lines[-4:]
    return target.lineno, lines


def code_table(start_line: int, lines: list[str]) -> Table:
    """Render source code safely without allowing long lines to overlap."""
    rows = []
    current_number = start_line
    for original in lines:
        expanded = original.expandtabs(4)
        wrapped = textwrap.wrap(
            expanded,
            width=88,
            subsequent_indent="    ",
            replace_whitespace=False,
            drop_whitespace=False,
        ) or [""]
        for index, part in enumerate(wrapped):
            number = str(current_number) if index == 0 else ""
            rows.append([
                number,
                Paragraph(escape(part).replace(" ", "&nbsp;"), STYLES["code"]),
            ])
        current_number += 1
    table = Table(rows, colWidths=[13 * mm, 155 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("FONTNAME", (0, 0), (0, -1), "Courier"),
        ("FONTSIZE", (0, 0), (0, -1), 6.5),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#7ED8A8")),
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("LINEAFTER", (0, 0), (0, -1), 0.4, colors.HexColor("#395066")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
    ]))
    return table


def explanation_table(rows: list[tuple[str, str]]) -> Table:
    data = [[P("Code idea", "head"), P("Beginner explanation", "head")]]
    data.extend([[P(left, "table"), P(right, "table")] for left, right in rows])
    table = Table(data, colWidths=[55 * mm, 113 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def callout(title: str, text: str) -> Table:
    table = Table([[P(title, "table"), P(text, "body")]], colWidths=[40 * mm, 128 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), MINT),
        ("BOX", (0, 0), (-1, -1), 0.6, GREEN),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


SECTIONS = [
    {
        "title": "Application startup and protection",
        "file": "app/__init__.py",
        "symbol": "create_app",
        "purpose": "This is the composition root. It creates Flask, loads settings, prepares the controller, protects forms, and registers all routes.",
        "flow": "run.py -> create_app() -> Flask configuration -> controller graph -> routes",
        "points": [
            ("Flask(__name__)", "Creates the web application object."),
            ("app.config.update(...)", "Adds the secret key and test mode."),
            ("app.extensions", "Stores the reusable controller graph inside Flask."),
            ("context_processor", "Makes the CSRF token available to every template."),
            ("before_request", "Checks browser POST forms before route code runs."),
            ("register_blueprint", "Attaches dashboard, approval, and JSON API URLs."),
        ],
    },
    {
        "title": "Creating a business objective",
        "file": "app/routes/dashboard_routes.py",
        "symbol": "create_objective",
        "purpose": "This route converts an HTML form submission into a validated objective and starts the autonomous workflow.",
        "flow": "Browser form -> route payload -> ObjectiveService -> ExecutionService -> objective page",
        "points": [
            ("request.form.get", "Reads values submitted from the browser."),
            ("keywords/source_urls", "Converts comma or line-separated text into lists."),
            ("objectives.create", "Validates and stores the business goal."),
            ("executions.start", "Creates a linked execution and starts background work."),
            ("flash + redirect", "Shows feedback and opens the new objective page."),
            ("except Exception", "Returns the user safely to the dashboard when validation fails."),
        ],
    },
    {
        "title": "Starting and running an execution",
        "file": "app/services/execution_service.py",
        "symbol": "ExecutionService.start",
        "purpose": "This method creates the execution record and chooses background or synchronous processing.",
        "flow": "Objective ID -> execution document -> database -> worker thread -> controller",
        "points": [
            ("objective lookup", "Prevents a workflow from starting for a missing objective."),
            ("new_id('EXE')", "Creates a readable unique execution identifier."),
            ("parent_execution_id", "Links follow-up work to an earlier execution."),
            ("background=True", "Runs analysis without blocking the browser request."),
            ("Thread(..., daemon=True)", "Starts a local worker for this MVP."),
            ("return execution", "Immediately gives the UI a record it can display."),
        ],
    },
    {
        "title": "The reason-act-observe loop",
        "file": "orchestration/graph_builder.py",
        "symbol": "build_graph",
        "purpose": "LangGraph executes the compiled StateGraph. It repeatedly runs the controller, routes to one worker, and propagates the updated state.",
        "flow": "LangGraph state -> controller decision -> conditional edge -> worker -> controller",
        "points": [
            ("StateGraph", "Defines a graph whose nodes read and update BuildSenseState."),
            ("START edge", "Runs the controller first."),
            ("conditional edges", "Route the controller's action to exactly one worker."),
            ("worker edges", "Return fresh observations to the controller."),
            ("END edges", "Stop after human review or cancellation."),
        ],
    },
    {
        "title": "Controller decision rules",
        "file": "orchestration/nodes.py",
        "symbol": "controller_node",
        "max_lines": 46,
        "purpose": "The controller observes evidence, tools, confidence, retries, budgets, cancellation, and recommendation state before selecting one action.",
        "flow": "Observe -> calculate legal actions -> optional bounded AI choice -> trace decision",
        "points": [
            ("execution status", "Cancellation has the highest priority."),
            ("recommendation exists", "Moves finished work to human review."),
            ("budget checks", "Prevent endless cycles, calls, or execution time."),
            ("confidence threshold", "Determines whether to strategize or collect more evidence."),
            ("remaining_tools", "Avoids repeating a tool until retry logic changes the plan."),
            ("allowed_actions", "Restricts optional AI control to safe choices."),
            ("action_history", "Stores the reason and observations for explainability."),
        ],
    },
    {
        "title": "Data Collection Agent",
        "file": "agents/data_collection_agent/agent.py",
        "symbol": "DataCollectionAgent.run",
        "max_lines": 42,
        "purpose": "Agent 1 runs the selected public-source adapters, validates results, removes duplicates, stores evidence, and records tool traces.",
        "flow": "Objective + plan -> selected source -> raw results -> validation -> deduplication -> stored evidence",
        "points": [
            ("preferred_tools", "Contains the tools selected by the planner/controller."),
            ("source.collect", "Calls one adapter using a normalized interface."),
            ("validate_items", "Removes incomplete or unusable evidence."),
            ("deduplicate", "Prevents repeated content from inflating confidence."),
            ("RawDataRepository", "Stores normalized evidence for later analysis."),
            ("trace_events", "Records inputs, counts, previews, and failures."),
        ],
    },
    {
        "title": "Intelligence Analysis Agent",
        "file": "agents/intelligence_analysis_agent/agent.py",
        "symbol": "IntelligenceAnalysisAgent.run",
        "max_lines": 42,
        "purpose": "Agent 2 converts collected text into a validated market intelligence report using OpenAI or a deterministic local fallback.",
        "flow": "Evidence -> AI/local analysis -> Pydantic validation -> intelligence document",
        "points": [
            ("evidence payload", "Contains normalized source records and IDs."),
            ("OpenAIClient", "Requests structured analysis only when configured."),
            ("IntelligenceReport", "Validates every required field and score range."),
            ("_local_analysis", "Keeps the workflow operational without external AI."),
            ("analysis_engine", "Discloses whether AI or local logic produced the result."),
            ("confidence", "Estimates evidence quality and adequacy, not guaranteed success."),
        ],
    },
    {
        "title": "Business Strategy Agent",
        "file": "agents/business_strategy_agent/agent.py",
        "symbol": "BusinessStrategyAgent.run",
        "max_lines": 42,
        "purpose": "Agent 3 creates strategy options, validates evidence grounding, ranks alternatives, and returns the standard final report.",
        "flow": "Objective + intelligence -> candidates -> grounding check -> ranking -> report",
        "points": [
            ("constraints", "Carries required and prohibited strategy conditions."),
            ("generate_local_strategies", "Provides repeatable offline alternatives."),
            ("Recommendation", "Validates strategy fields and final-report structure."),
            ("_validate_grounding", "Rejects citations to evidence that does not exist."),
            ("rank_strategies", "Places the strongest score first."),
            ("strategy_engine", "Discloses the generation method."),
        ],
    },
    {
        "title": "Standard final business report",
        "file": "agents/business_strategy_agent/recommendation_builder.py",
        "symbol": "build_recommendation",
        "max_lines": 44,
        "purpose": "This builder ensures pharmacy, restaurant, laptop, and other scenarios always produce the same management-friendly report sections.",
        "flow": "Objective + intelligence + ranked strategy -> fixed report contract",
        "points": [
            ("business_goal", "Repeats the decision the manager asked the system to support."),
            ("opportunity_score", "Combines evidence confidence and strategy strength."),
            ("data_sources_used", "Shows where the supporting information came from."),
            ("recommended_business_changes", "Adapts practical changes to the objective's industry."),
            ("marketing/operations", "Separates customer acquisition from internal execution."),
            ("overall_recommendation", "Provides one concise management conclusion."),
        ],
    },
    {
        "title": "MongoDB repository boundary",
        "file": "database/repositories/base_repo.py",
        "symbol": "BaseRepository",
        "max_lines": 45,
        "purpose": "This shared repository keeps database code out of agents and services and removes MongoDB-only metadata from application data.",
        "flow": "Service -> repository -> MongoDB collection -> cleaned Python dictionary",
        "points": [
            ("collection property", "Selects the MongoDB collection for the child repository."),
            ("_clean_document", "Removes `_id` and recursively converts database-specific values."),
            ("deepcopy", "Prevents PyMongo from mutating live application dictionaries."),
            ("list(...).sort(...)", "Returns newest records first."),
            ("update", "Adds a fresh updated_at timestamp automatically."),
            ("delete_many", "Supports safe cascade deletion of related records."),
        ],
    },
    {
        "title": "Public URL safety",
        "file": "core/url_safety.py",
        "symbol": "validate_public_url",
        "max_lines": 40,
        "purpose": "This function prevents source URLs from reaching local machines, private networks, or other unsafe destinations.",
        "flow": "User URL -> parse -> hostname resolution -> IP checks -> safe public URL",
        "points": [
            ("urlparse", "Separates the URL scheme, host, port, path, and query."),
            ("http/https only", "Rejects file, FTP, and other unsupported schemes."),
            ("hostname required", "Rejects malformed URLs."),
            ("ipaddress", "Identifies private, loopback, reserved, and link-local addresses."),
            ("DNS resolution", "Checks the actual addresses behind a public hostname."),
            ("redirect checks", "The scraper revalidates the final destination after redirects."),
        ],
    },
    {
        "title": "Human approval logic",
        "file": "app/services/approval_service.py",
        "symbol": "ApprovalService.apply",
        "max_lines": 44,
        "purpose": "This service makes the manager the final authority and controls approve, modify, reject, more-analysis, and restart actions.",
        "flow": "Review form -> validated action -> approval record -> status update or child execution",
        "points": [
            ("awaiting_approval", "Only a reviewable execution may receive a decision."),
            ("ApprovalRequest", "Requires feedback for actions that need explanation."),
            ("approval_document", "Stores the action, feedback, and optional modified summary."),
            ("approve/modify/reject", "Updates the current execution to a terminal status."),
            ("more_analysis/restart", "Creates a linked follow-up execution."),
            ("human_guidance", "Injects manager feedback into the next research plan."),
        ],
    },
    {
        "title": "PDF generation and safe table wrapping",
        "file": "app/services/pdf_report_service.py",
        "symbol": "PDFReportService._strategy_comparison",
        "max_lines": 38,
        "purpose": "This code builds the comparison table and wraps every value so long AI-generated text cannot overlap another column.",
        "flow": "Strategy dictionaries -> wrapping Paragraph cells -> styled ReportLab table",
        "points": [
            ("Paragraph per cell", "Allows long text to wrap within its own column."),
            ("fixed colWidths", "Keeps the complete table inside the printable page width."),
            ("repeatRows=1", "Repeats the header when a table spans pages."),
            ("VALIGN TOP", "Keeps multi-line cells aligned consistently."),
            ("cell padding", "Separates text from borders and neighboring columns."),
            ("ROWBACKGROUNDS", "Improves scanning with alternating row colors."),
        ],
    },
    {
        "title": "Approved PDF download route",
        "file": "app/routes/dashboard_routes.py",
        "symbol": "approved_pdf_report",
        "max_lines": 34,
        "purpose": "This route allows PDF download only after approval, assembles the complete record bundle, and returns a browser attachment.",
        "flow": "Download click -> approval check -> PDFReportService -> PDF response",
        "points": [
            ("execution lookup", "Returns 404 when the execution does not exist."),
            ("approved status check", "Prevents downloading an unfinished final report."),
            ("objective lookup", "Adds the original business goal to the PDF data."),
            ("PDFReportService().build", "Generates the PDF bytes in memory."),
            ("Content-Type", "Tells the browser that the response is a PDF."),
            ("Content-Disposition", "Creates a clear downloadable filename."),
        ],
    },
]


def page_decoration(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 15 * mm, width, 15 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(18 * mm, height - 9.5 * mm, "BuildSense AI")
    canvas.setFont("Helvetica", 7.3)
    canvas.setFillColor(colors.HexColor("#CBD8E2"))
    canvas.drawRightString(width - 18 * mm, height - 9.5 * mm, "Important Code Explained")
    canvas.setStrokeColor(BORDER)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.3)
    canvas.drawString(18 * mm, 9 * mm, "Real source code with beginner explanations")
    canvas.drawRightString(width - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_story() -> list:
    story = [Spacer(1, 28 * mm)]
    cover = Table([
        [P("BUILDSENSE AI", "cover_small")],
        [P("Important Code Explained", "cover")],
        [P(
            "A focused beginner guide to the real code that starts the app, "
            "runs the controller, coordinates agents, stores evidence, protects "
            "users, records approval, and generates the final PDF.",
            "cover_small",
        )],
        [Spacer(1, 28 * mm)],
        [P(f"{len(SECTIONS)} essential code paths in runtime order", "cover_small")],
    ], colWidths=[170 * mm])
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("BOX", (0, 0), (-1, -1), 1, GREEN),
        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story += [cover, PageBreak()]
    story += [
        P("How to read this guide", "h1"),
        P("Each chapter follows the order in which the system normally runs. The displayed snippets are extracted from the current project source whenever the PDF is generated."),
        callout(
            "Reading method",
            "Read Purpose first, then Runtime flow, then the code from top to "
            "bottom. Use the explanation table to connect Python syntax to the "
            "business behavior.",
        ),
        P("Runtime map", "h2"),
    ]
    runtime_rows = [
        ["1", "Flask starts", "Configuration, security, and routes are connected."],
        ["2", "User creates objective", "Goal is validated, stored, and linked to an execution."],
        ["3", "Controller loops", "One legal action is selected and observed each cycle."],
        ["4", "Agents work", "Evidence is collected, analyzed, and converted into strategies."],
        ["5", "MongoDB stores", "Every result and decision remains traceable."],
        ["6", "Human decides", "Manager approval controls the final outcome."],
        ["7", "PDF downloads", "Approved records become a professional report."],
    ]
    story += [explanation_table([(f"{a}. {b}", c) for a, b, c in runtime_rows]), PageBreak()]

    for number, section in enumerate(SECTIONS, 1):
        line, code_lines = source_symbol(
            section["file"],
            section["symbol"],
            min(section.get("max_lines", 14), 14),
        )
        story += [
            P(f"{number}. {section['title']}", "h1"),
            P(section["file"], "h2"),
            P(f"<b>Purpose:</b> {section['purpose']}"),
            callout("Runtime flow", section["flow"]),
            P(f"Real code excerpt - starts at source line {line}", "h2"),
            code_table(line, code_lines),
            Spacer(1, 3 * mm),
            P("What the important parts mean", "h2"),
            explanation_table(section["points"]),
            PageBreak(),
        ]

    story += [
        P("Final code understanding", "h1"),
        P("The important code forms one continuous evidence-to-decision pipeline:"),
        explanation_table([
            ("Flask", "Accepts requests and connects pages to application services."),
            ("Services", "Apply reusable business rules and coordinate records."),
            ("Controller", "Selects one action based on current observations."),
            ("Agents", "Collect evidence, extract intelligence, and generate strategy."),
            ("Schemas", "Keep every input and output structured and valid."),
            ("Repositories", "Preserve objectives, executions, evidence, reports, and decisions."),
            ("Human approval", "Keeps the final management choice under human control."),
            ("PDF service", "Transforms approved structured data into a downloadable report."),
        ]),
        Spacer(1, 5 * mm),
        callout(
            "Best next step",
            "Open each referenced file beside this PDF. Set breakpoints in "
            "create_objective(), build_graph(), controller_node(), "
            "and each Agent.run() method, then submit one small objective and "
            "watch the same data move through the complete workflow.",
        ),
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
        title="BuildSense AI Important Code Explained",
        author="BuildSense AI",
        subject="Beginner explanation of the project's most important source code",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="content")
    doc.addPageTemplates([PageTemplate(id="guide", frames=[frame], onPage=page_decoration)])
    doc.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()
