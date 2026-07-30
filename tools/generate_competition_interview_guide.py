"""Generate a competition interview question-and-answer PDF for BuildSense AI."""

from pathlib import Path
from html import escape

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
OUTPUT = ROOT / "output" / "pdf" / "buildsense-ai-competition-interview-guide.pdf"

NAVY = colors.HexColor("#10243B")
GREEN = colors.HexColor("#14885D")
MINT = colors.HexColor("#E9F7F0")
LIGHT = colors.HexColor("#F4F7FA")
TEXT = colors.HexColor("#26384A")
MUTED = colors.HexColor("#647488")
BORDER = colors.HexColor("#D8E1E8")
AMBER = colors.HexColor("#D89221")

base = getSampleStyleSheet()
S = {
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
        fontSize=13.5, leading=18, textColor=GREEN, spaceBefore=8,
        spaceAfter=6, keepWithNext=True,
    ),
    "body": ParagraphStyle(
        "Body", parent=base["BodyText"], fontName="Helvetica",
        fontSize=9, leading=13.5, textColor=TEXT, spaceAfter=6,
    ),
    "small": ParagraphStyle(
        "Small", parent=base["BodyText"], fontName="Helvetica",
        fontSize=7.8, leading=11, textColor=TEXT,
    ),
    "head": ParagraphStyle(
        "Head", parent=base["BodyText"], fontName="Helvetica-Bold",
        fontSize=7.8, leading=10.5, textColor=colors.white,
    ),
    "table": ParagraphStyle(
        "Table", parent=base["BodyText"], fontName="Helvetica",
        fontSize=7.7, leading=10.7, textColor=TEXT,
    ),
    "question": ParagraphStyle(
        "Question", parent=base["BodyText"], fontName="Helvetica-Bold",
        fontSize=9.2, leading=13, textColor=NAVY,
    ),
    "answer": ParagraphStyle(
        "Answer", parent=base["BodyText"], fontName="Helvetica",
        fontSize=8.5, leading=12.5, textColor=TEXT,
    ),
    "label": ParagraphStyle(
        "Label", parent=base["BodyText"], fontName="Helvetica-Bold",
        fontSize=7, leading=9, textColor=GREEN,
    ),
}


def P(text: str, style: str = "body") -> Paragraph:
    safe = (
        escape(str(text))
        .replace("&lt;b&gt;", "<b>")
        .replace("&lt;/b&gt;", "</b>")
        .replace("&lt;br/&gt;", "<br/>")
    )
    return Paragraph(safe, S[style])


def callout(title: str, text: str, background=MINT) -> Table:
    table = Table([[P(title, "label"), P(text, "body")]], colWidths=[39 * mm, 129 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), background),
        ("BOX", (0, 0), (-1, -1), 0.6, GREEN),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def qa_card(number: int, question: str, answer: str, tip: str = "") -> Table:
    content = [
        P(f"QUESTION {number}", "label"),
        P(question, "question"),
        Spacer(1, 2 * mm),
        P(answer, "answer"),
    ]
    if tip:
        content += [Spacer(1, 2 * mm), P(f"<b>Judge tip:</b> {tip}", "small")]
    table = Table([[content]], colWidths=[168 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("LINEBEFORE", (0, 0), (0, -1), 3, GREEN),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


SECTIONS = [
    (
        "Project idea and value",
        [
            (
                "What is BuildSense AI?",
                "BuildSense AI is an evidence-to-decision platform for business managers. A manager enters a business objective, three specialized agents collect public evidence, extract market intelligence, compare strategies, and produce a standard final report. A human manager keeps control of the final decision.",
                "Start with the business value, then mention the technology.",
            ),
            (
                "What real problem does this project solve?",
                "Business owners often make decisions from assumptions or manually inspect thousands of reviews and pages. BuildSense collects scattered public signals, converts them into explainable insights, and presents practical actions with evidence and confidence.",
                "",
            ),
            (
                "Who is the target user?",
                "The primary user is a business manager, entrepreneur, retailer, or analyst who needs evidence before making a market, inventory, product, or launch decision.",
                "",
            ),
            (
                "What is the main output?",
                "The main output is a management-ready report containing the business goal, opportunity score, confidence, sources, complaints, trends, high-demand categories, business changes, marketing actions, operational improvements, target market, and overall recommendation.",
                "",
            ),
            (
                "Why is this better than asking a chatbot one question?",
                "A normal chatbot usually answers from one prompt. BuildSense plans research, uses external tools, stores normalized evidence, adapts after observing results, validates structured schemas, compares alternatives, records a decision trail, and requires human approval.",
                "Emphasize workflow, evidence, traceability, and control.",
            ),
            (
                "Give one simple use case.",
                "A pharmacy in Sri Lanka asks what to stock for the next three months. BuildSense studies reviews, discussions, competitors, and health websites, identifies out-of-stock complaints and trending wellness products, then recommends inventory, marketing, and operational changes.",
                "",
            ),
            (
                "What makes the project innovative?",
                "Its innovation is the combination of adaptive multi-agent research, structured evidence grounding, a transparent controller, human approval, durable records, and a reusable final-report contract that works across industries.",
                "",
            ),
        ],
    ),
    (
        "Architecture and workflow",
        [
            (
                "Explain the architecture in one sentence.",
                "Flask receives the goal, application services start a LangGraph StateGraph, the controller node routes work through three agents and external tools, repositories store everything in MongoDB, and the dashboard pauses for human approval and report download.",
                "",
            ),
            (
                "What are the main architectural layers?",
                "The layers are frontend templates and JavaScript, Flask routes, application services, orchestration/controller, specialized agents, external tool clients, Pydantic schemas, and MongoDB repositories.",
                "",
            ),
            (
                "Explain the complete workflow.",
                "The user submits a goal. Flask validates and stores it. ExecutionService creates a run. The planner prepares tools and queries. The controller selects one action. Agent 1 collects evidence. Agent 2 analyzes it. Low confidence may trigger more research. Agent 3 generates strategies. The workflow pauses for a manager decision. Approved results can be downloaded as JSON or PDF.",
                "Explain in chronological order and keep each step short.",
            ),
            (
                "Why did you separate routes and services?",
                "Routes translate HTTP requests into service calls. Services contain reusable business rules such as safe deletion, workflow startup, approval, readiness, and report generation. This separation improves testing and maintainability.",
                "",
            ),
            (
                "Why use schemas?",
                "Pydantic schemas define exactly what objectives, evidence, intelligence, strategies, controller decisions, and approvals must contain. They reject missing fields, invalid values, and scores outside allowed ranges.",
                "",
            ),
            (
                "What is stored in workflow state?",
                "The state contains the objective, execution ID, plan, evidence, attempted tools, errors, retries, intelligence, recommendation, action history, human guidance, status, and trace events.",
                "",
            ),
            (
                "How does data move from the browser to the PDF?",
                "The form becomes an objective document, the execution produces evidence, intelligence, and recommendation documents, approval changes the execution status, DashboardService assembles the records, and PDFReportService converts the approved bundle into PDF bytes.",
                "",
            ),
        ],
    ),
    (
        "Agents and autonomy",
        [
            (
                "How many agents are there and what do they do?",
                "There are three worker agents. Agent 1 collects and normalizes public evidence. Agent 2 extracts sentiment, complaints, trends, products, needs, and confidence. Agent 3 creates alternatives, ranks strategies, validates grounding, and builds the final report.",
                "",
            ),
            (
                "Why is the system agentic?",
                "The controller repeatedly observes current results and selects the next legal action. It can choose another collection tool, retry with a broader plan, analyze available evidence, generate strategy, cancel, or move to human review. The next step is not decided by the previous worker.",
                "",
            ),
            (
                "Is the workflow a fixed pipeline?",
                "No. Collection, retries, analysis, and strategy are legal actions selected from observations. The controller adapts to evidence count, attempted tools, confidence, failures, budgets, cancellation, and human guidance.",
                "This is a very likely competition question.",
            ),
            (
                "What is the reason-act-observe pattern?",
                "Reason means inspect the current state and choose one action. Act means run the selected worker. Observe means merge its output back into state. The controller then reasons again until human review or cancellation.",
                "",
            ),
            (
                "Do you use LangGraph or another framework?",
                "Yes. The project uses LangGraph StateGraph with START, END, worker nodes, and conditional edges. The controller and agent logic remain project-owned Python functions, while LangGraph runs the stateful graph.",
                "Show orchestration/graph_builder.py if the judge asks for proof.",
            ),
            (
                "How does the controller choose the next action?",
                "It prioritizes cancellation, then checks whether a recommendation is ready, whether budgets are reached, whether intelligence confidence is sufficient, whether more research is allowed, whether enough evidence exists, and which tools remain unused.",
                "",
            ),
            (
                "Can AI control the workflow?",
                "Optionally, OpenAI may select from a bounded list of currently legal actions. Its JSON response is validated. If it selects an unknown action or fails validation, the deterministic safety controller uses the fallback action.",
                "",
            ),
            (
                "How does Agent 1 choose tools?",
                "The execution planner examines the objective, industry, location, keywords, source URLs, retry count, and human guidance. It ranks configured tools and records a rationale for each selected source.",
                "",
            ),
            (
                "How does Agent 2 calculate confidence?",
                "Confidence is based on evidence volume and quality signals. It represents evidence adequacy, not a probability that the business will definitely succeed.",
                "Never claim confidence is guaranteed business success.",
            ),
            (
                "How does Agent 3 avoid hallucinated evidence?",
                "Strategies carry evidence IDs. The agent compares those IDs with the analyzed source records. Unknown IDs are rejected, so the recommendation cannot claim support from evidence that was never collected.",
                "",
            ),
            (
                "What happens when confidence is low?",
                "If the retry budget allows it, the controller selects broader evidence collection. If retries are exhausted, the system creates a lower-confidence recommendation and exposes the limitation for human review.",
                "",
            ),
        ],
    ),
    (
        "Tools, data, and MongoDB",
        [
            (
                "Which external tools are supported?",
                "The project supports Google Places for business reviews, YouTube for public discussions, Firecrawl for structured webpage extraction, BeautifulSoup-based direct scraping, and OpenAI for structured intelligence and strategy generation.",
                "",
            ),
            (
                "What happens if one external tool fails?",
                "The source error is recorded in the decision trail. The controller observes the failure and may select another unused tool or retry with a broader plan. The complete execution does not automatically fail because one source failed.",
                "",
            ),
            (
                "Why normalize evidence?",
                "Every source returns different data. Normalization converts them into one CollectedItem structure with an ID, source, title, content, URL, and metadata, so later agents do not need source-specific logic.",
                "",
            ),
            (
                "How do you remove duplicate evidence?",
                "The collection layer cleans and compares normalized content, then keeps unique records. This prevents repeated reviews or pages from inflating evidence volume and confidence.",
                "",
            ),
            (
                "Why use MongoDB?",
                "The workflow produces flexible JSON-like documents from different agents. MongoDB fits that structure, supports execution-linked collections, and preserves objectives, evidence, intelligence, recommendations, trails, and approvals across restarts.",
                "",
            ),
            (
                "What collections exist?",
                "The main collections are objectives, executions, raw_data, intelligence, recommendations, decision_trail, and approvals.",
                "",
            ),
            (
                "Why is memory storage still present?",
                "The in-memory implementation is a test and local fallback. It makes automated tests fast and isolated. A real demonstration should use MongoDB because memory records disappear after restart.",
                "",
            ),
            (
                "How are records related?",
                "An objective can have multiple executions. Child collections use execution_id. Follow-up runs also store parent_execution_id, so manager-requested restarts or more analysis remain traceable.",
                "",
            ),
            (
                "What is the readiness check?",
                "It performs live checks against configured integrations and distinguishes configured, working, failed, empty, and unavailable states. It also reports whether at least three tools produced usable evidence.",
                "",
            ),
        ],
    ),
    (
        "Human control, safety, and reliability",
        [
            (
                "Why include human-in-the-loop approval?",
                "Business recommendations can affect money and operations. The agents prepare evidence and options, but a manager must approve, modify, reject, request more analysis, or restart the workflow.",
                "",
            ),
            (
                "Which approval actions are supported?",
                "Approve, modify and approve, reject, request more analysis, and restart. Follow-up actions can create a linked child execution using the manager's feedback.",
                "",
            ),
            (
                "Can the same execution be approved twice?",
                "No. ApprovalService requires the execution to be in awaiting_approval state. Once a terminal decision changes the status, another approval is rejected.",
                "",
            ),
            (
                "How do you prevent endless loops?",
                "The controller enforces maximum cycles, tool calls, retries, and elapsed execution time. LangGraph also applies a recursion limit above the application's own stricter budget.",
                "",
            ),
            (
                "How does cancellation work?",
                "The user marks a running execution as cancel_requested. At the next controller decision point, cancellation has highest priority and the cancel node ends the run safely.",
                "",
            ),
            (
                "How do you protect source URL scraping?",
                "The URL validator allows HTTP and HTTPS only, requires a host, resolves addresses, and rejects private, loopback, link-local, reserved, or otherwise unsafe targets. Redirect destinations are validated again.",
                "",
            ),
            (
                "How do you protect browser forms?",
                "Flask creates a session-backed CSRF token, inserts it into templates, and checks it before non-API POST requests. Invalid or missing tokens receive a 400 response.",
                "",
            ),
            (
                "How do you protect API keys?",
                "Keys are loaded from environment variables and never returned by health or readiness responses. For production, they should move to a managed secret store with rotation.",
                "",
            ),
            (
                "What happens when OpenAI is unavailable?",
                "The intelligence and strategy agents use deterministic local logic. The output records which engine was used, so fallback behavior is transparent.",
                "",
            ),
            (
                "Is the recommendation guaranteed to succeed?",
                "No. It is evidence-informed decision support. Scores and confidence are not guarantees. The report should be combined with financial, legal, operational, and domain-expert validation.",
                "This honest answer increases credibility.",
            ),
        ],
    ),
    (
        "Frontend, report, testing, and production",
        [
            (
                "What does the dashboard show?",
                "It shows objective creation, demonstration presets, portfolio statistics, status filters, active and historical opportunities, workflow progress, execution history, recommendations, evidence, and approval controls.",
                "",
            ),
            (
                "What is inside the final PDF?",
                "It contains an executive summary, objective context, recommended strategy, alternative strategies, standard final business report, market intelligence, supporting evidence, controller trail, human approval, and a decision disclaimer.",
                "",
            ),
            (
                "How did you fix PDF text overlap?",
                "Every strategy table cell is rendered as a ReportLab Paragraph, allowing long model-generated values to wrap within fixed column widths. Padding, top alignment, and repeating headers keep the table readable.",
                "",
            ),
            (
                "How is deletion made safe?",
                "Only non-running objectives can be deleted. The service first finds all linked executions, removes evidence, intelligence, recommendations, trail records, and approvals, then deletes executions and the objective. The UI also requires confirmation.",
                "",
            ),
            (
                "How did you test the project?",
                "The automated tests cover routes, CSRF, URL safety, MongoDB metadata cleanup, cancellation, approvals, agents, controller behavior, pharmacy and pizza scenarios, cascade deletion, and PDF generation.",
                "",
            ),
            (
                "What are the biggest current limitations?",
                "It is an MVP. Background work uses local threads, there is no user authentication, opportunity scoring is heuristic, external sources can be unavailable, and production compliance, monitoring, rate limits, and secret management require further work.",
                "",
            ),
            (
                "What would you change for production?",
                "Add authentication and roles, Celery and Redis for durable tasks, managed secrets, rate limiting, monitoring, encrypted data, backups, retention policies, source compliance controls, and outcome-based score calibration.",
                "",
            ),
            (
                "How would this project scale?",
                "Move executions to a distributed task queue, scale workers independently by tool or agent, cache repeated public sources, paginate evidence, add database indexes on objective_id and execution_id, and use observability for queue and API performance.",
                "",
            ),
            (
                "What would you build next?",
                "I would add authenticated organizations, scheduled market monitoring, source-quality scoring, financial scenario modeling, comparison across previous executions, and feedback-based recommendation evaluation.",
                "",
            ),
        ],
    ),
]


RAPID_FIRE = [
    ("Backend framework?", "Flask."),
    ("Validation library?", "Pydantic."),
    ("Primary database?", "MongoDB, with memory mode for tests."),
    ("Number of worker agents?", "Three."),
    ("Controller pattern?", "Reason-act-observe."),
    ("Final authority?", "The human manager."),
    ("Evidence tools?", "Google Places, YouTube, Firecrawl, and safe webpage scraping."),
    ("AI provider?", "OpenAI, with deterministic local fallback."),
    ("Durable identifier examples?", "OBJ-* for objectives and EXE-* for executions."),
    ("How is evidence grounded?", "Strategies cite validated evidence IDs."),
    ("How is workflow stopped?", "Cancellation is observed at the next controller decision."),
    ("How are unsafe URLs blocked?", "Scheme, host, DNS, IP, and redirect validation."),
    ("Approved export formats?", "PDF and JSON."),
    ("How are long PDF values handled?", "Wrapping Paragraph cells with fixed widths."),
    ("Current controller framework?", "LangGraph StateGraph with project-owned controller nodes."),
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
    canvas.drawRightString(width - 18 * mm, height - 9.5 * mm, "Competition Interview Guide")
    canvas.setStrokeColor(BORDER)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.3)
    canvas.drawString(18 * mm, 9 * mm, "Judge questions, strong answers, and demo preparation")
    canvas.drawRightString(width - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def table(headers, rows, widths):
    data = [[P(value, "head") for value in headers]]
    data.extend([[P(value, "table") for value in row] for row in rows])
    result = Table(data, colWidths=[width * mm for width in widths], repeatRows=1)
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return result


def build_story():
    total_questions = sum(len(items) for _, items in SECTIONS) + len(RAPID_FIRE)
    story = [Spacer(1, 28 * mm)]
    cover = Table([
        [P("BUILDSENSE AI", "cover_small")],
        [P("Competition Interview Guide", "cover")],
        [P(
            "Likely judge questions, strong project-specific answers, technical "
            "challenges, demo preparation, and rapid revision.",
            "cover_small",
        )],
        [Spacer(1, 25 * mm)],
        [P(f"{total_questions} questions and answers", "cover_small")],
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
        P("How to prepare", "h1"),
        callout(
            "Answer formula",
            "Use three parts: 1. Direct answer. 2. How BuildSense implements "
            "it. 3. Why that design matters. Keep the first answer under 30 "
            "seconds, then expand only if the judge asks.",
        ),
        P("60-second project pitch", "h2"),
        P(
            "BuildSense AI is an autonomous multi-agent business intelligence "
            "platform. A manager enters a business goal, and a custom "
            "reason-act-observe controller coordinates three agents. The first "
            "collects public evidence from reviews, discussions, and websites. "
            "The second identifies customer complaints, demand, products, "
            "trends, and confidence. The third compares business strategies and "
            "creates a standard management report. Every source, controller "
            "decision, retry, and recommendation is stored for traceability. "
            "The system then pauses for a human manager to approve, modify, "
            "reject, or request more analysis. Approved results can be "
            "downloaded as JSON or a professional PDF."
        ),
        P("What to demonstrate first", "h2"),
        table(
            ["Order", "Show", "What to say"],
            [
                ["1", "Objective form", "This is the high-level business goal, not a technical prompt."],
                ["2", "Workflow monitor", "The controller chooses actions from current observations."],
                ["3", "Decision trail", "Every tool call, retry, and reason is visible."],
                ["4", "Final report", "Raw evidence becomes practical management actions."],
                ["5", "Approval", "The human remains the final authority."],
                ["6", "PDF download", "The approved result becomes a portable business document."],
            ],
            [14, 48, 106],
        ),
        PageBreak(),
    ]

    number = 1
    for title, questions in SECTIONS:
        story += [P(title, "h1")]
        for question, answer, tip in questions:
            story += [qa_card(number, question, answer, tip), Spacer(1, 3 * mm)]
            number += 1
        story.append(PageBreak())

    story += [
        P("Rapid-fire revision", "h1"),
        P("Use these answers when a judge asks for one short fact."),
        table(
            ["Question", "Short answer"],
            [[question, answer] for question, answer in RAPID_FIRE],
            [75, 93],
        ),
        Spacer(1, 6 * mm),
        P("Difficult challenge questions", "h1"),
    ]
    challenge_rows = [
        ["Why should I trust public reviews?", "Do not trust one review. Normalize many records, remove duplicates, compare sources, expose confidence, and keep human review."],
        ["Can competitors manipulate evidence?", "Yes. That is why source diversity, spam filtering, provenance, and human validation matter. Production should add stronger source-quality and anomaly scoring."],
        ["Why is 90% confidence not misleading?", "It can be if presented as success probability. In BuildSense it represents evidence adequacy and should always be explained with volume, quality, and limitations."],
        ["What if all APIs fail during judging?", "The readiness check detects this before the demo. The system records failures, uses alternative configured tools, and can demonstrate transparent local fallback without pretending synthetic data is live evidence."],
        ["Why not automate approval?", "Business decisions can create financial and operational risk. Human approval is a deliberate governance boundary."],
        ["Is this production ready?", "It is a competition-ready MVP. I can clearly identify the required production upgrades rather than overstating readiness."],
    ]
    story += [
        table(["Challenge", "Strong answer"], challenge_rows, [66, 102]),
        Spacer(1, 6 * mm),
        callout(
            "Final competition advice",
            "Never claim guaranteed business success, unlimited autonomy, or "
            "production readiness. Judges usually reward a clear problem, real "
            "evidence, explainable architecture, honest limitations, and a "
            "reliable live demonstration.",
            colors.HexColor("#FFF6E6"),
        ),
    ]
    return story


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=21 * mm,
        rightMargin=21 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title="BuildSense AI Competition Interview Guide",
        author="BuildSense AI",
        subject="Competition judge questions and strong project-specific answers",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="content")
    doc.addPageTemplates([PageTemplate(id="guide", frames=[frame], onPage=page_decoration)])
    doc.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()
