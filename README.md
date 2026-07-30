<div align="center">

# BuildSense AI

### Autonomous Business Research and Decision Intelligence

BuildSense AI transforms an open-ended business objective into an evidence-backed, requirement-specific business recommendation through autonomous research, structured intelligence analysis, adaptive strategy generation, and human approval.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Orchestration-1C3C3C)](https://www.langchain.com/langgraph)
[![MongoDB](https://img.shields.io/badge/MongoDB-Supported-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org/)
[![Status](https://img.shields.io/badge/Status-MVP-orange)](#project-status)

</div>

---

## Overview

BuildSense AI is a multi-agent business intelligence application built with Python, Flask, LangGraph, Pydantic, MongoDB, and optional OpenAI integration.

A user can submit a business question such as:

> I want to open a quality shoe shop in Colombo. Recommend a suitable location, target audience, product mix, pricing approach, marketing strategy, and business improvements.

The system autonomously:

1. Interprets the business objective.
2. Extracts the user’s individual requirements.
3. Determines which information is missing.
4. Selects suitable research tools.
5. Collects and validates external evidence.
6. Analyzes customer, competitor, demand, and location signals.
7. Detects contradictions and research gaps.
8. Performs additional research when necessary.
9. Generates and compares multiple strategies.
10. Answers every user requirement directly.
11. Validates recommendation quality.
12. Pauses for human review.
13. Produces dashboard, JSON, and PDF outputs.

BuildSense AI is designed to provide researched recommendations—not generic instructions telling the user to conduct the research themselves.

---

## Table of Contents

- [Overview](#overview)
- [Why BuildSense AI?](#why-buildsense-ai)
- [Key Capabilities](#key-capabilities)
- [Example Use Cases](#example-use-cases)
- [How It Works](#how-it-works)
- [System Architecture](#system-architecture)
- [Agent Architecture](#agent-architecture)
- [Dynamic Orchestration](#dynamic-orchestration)
- [Evidence and Decision Quality](#evidence-and-decision-quality)
- [Human Review](#human-review)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [External Integrations](#external-integrations)
- [REST API](#rest-api)
- [Testing](#testing)
- [Security and Reliability](#security-and-reliability)
- [Documentation](#documentation)
- [Production Considerations](#production-considerations)
- [Project Status](#project-status)
- [Contributing](#contributing)
- [License](#license)

---

## Why BuildSense AI?

Traditional chatbots normally respond to one question at a time. They depend on a human to continue asking questions, interpret the responses, and decide what to do next.

BuildSense AI uses a bounded autonomous workflow.

The controller can independently decide whether it should:

- Collect new evidence
- Select a different research tool
- Modify a search query
- Retry a failed tool
- Analyze collected evidence
- Investigate a research gap
- Generate business strategies
- Stop because a budget was reached
- Request human review

This makes the system adaptive rather than a fixed pipeline.

Different business objectives can produce different research queries, tools, execution paths, intelligence findings, strategies, and report sections.

---

## Key Capabilities

### Autonomous research

- Converts a business objective into research needs
- Selects tools based on the current requirement
- Builds targeted research queries
- Performs multiple evidence-collection actions
- Adapts when results are missing or unsuccessful
- Operates within explicit execution budgets

### Evidence collection

- Google Places integration
- YouTube Data API integration
- Firecrawl integration
- Direct public webpage extraction
- Normalized evidence records
- Source metadata preservation
- Evidence validation and deduplication
- Tool-attempt and failure logging

### Business intelligence

- Verified market signals
- Explicitly labeled hypotheses
- Customer pain-point detection
- Customer sentiment analysis
- Purchase-intent detection
- Demand-signal analysis
- Competitor-signal analysis
- Location-candidate ranking
- Contradiction detection
- Opportunity identification
- Risk identification
- Research-gap detection
- Decision-readiness scoring

### Strategy generation

- Multiple strategy alternatives
- Evidence-grounded strategy comparison
- Opportunity and feasibility assessment
- Risk-aware ranking
- Human-constraint consideration
- Strategy selection with supporting reasons

### Adaptive recommendations

- Separate answer for every user requirement
- Business-specific report structure
- Concrete location recommendations when supported
- Target-audience recommendations
- Product and service recommendations
- Pricing and positioning guidance
- Marketing recommendations
- Operational improvements
- Implementation priorities
- Risks and validation steps
- Overall executive recommendation

### Human oversight

- Approve
- Approve with modifications
- Reject
- Request additional analysis
- Retry
- Cancel

### Reporting and transparency

- Interactive dashboard
- Execution status
- Tool-use history
- Decision trail
- Evidence summary
- Intelligence findings
- Strategy comparison
- Requirement answers
- JSON export
- Professional PDF report

---

## Example Use Cases

BuildSense AI can support business questions such as:

### New business planning

```text
I want to open a coffee shop in Colombo.

Recommend:
- A suitable location
- The target audience
- The product and menu mix
- A pricing approach
- A marketing strategy
- Operational improvements
- A 90-day launch plan
```

### Retail opportunity research

```text
Evaluate an affordable laptop retail opportunity for university students.

Identify:
- Target customers
- Product categories
- Competitor signals
- Pricing opportunities
- Sales channels
- Warranty and support services
- Business risks
```

### Existing business improvement

```text
Analyze how an existing pharmacy can improve customer retention,
product availability, local marketing, and operational efficiency.
```

### Location decision

```text
Find a suitable catchment for a quality-focused shoe shop and explain
the customer demand, nearby competition, risks, and validation steps.
```

The final report changes according to the business type and user requirements. It does not force every business into one generic template.

---

## How It Works

```text
User submits a business objective
                |
                v
Flask validates the request
                |
                v
Objective and execution records are created
                |
                v
LangGraph receives the initial execution state
                |
                v
Controller selects the next legal action
                |
       +--------+-------------------------------+
       |                                        |
       v                                        v
Plan and collect evidence                Inspect current findings
       |                                        |
       v                                        |
Select the most suitable tool <-----------------+
       |
       v
Collect, normalize, validate, and store evidence
       |
       v
Analyze business intelligence
       |
       +-------- Important evidence missing? --------+
       |                                              |
       | Yes                                          | No
       v                                              v
Perform additional research                 Generate alternatives
                                                      |
                                                      v
                                             Compare strategies
                                                      |
                                                      v
                                           Build direct answers
                                                      |
                                                      v
                                         Apply recommendation checks
                                                      |
                                                      v
                                           Human approval required
                                                      |
                                                      v
                                      Dashboard, JSON, and PDF report
```

---

## System Architecture

BuildSense AI uses a layered architecture that separates web concerns, application services, orchestration, specialist agents, tools, validation, and persistence.

```text
┌──────────────────────────────────────────────────────────────┐
│                       User Interface                         │
│              Browser Dashboard and REST API                  │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    Flask Application                         │
│       Dashboard Routes | API Routes | Approval Routes        │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    Application Services                      │
│ Objective | Execution | Approval | Dashboard | PDF | Status  │
└──────────────────────┬────────────────────────┬──────────────┘
                       │                        │
                       ▼                        ▼
┌──────────────────────────────┐  ┌────────────────────────────┐
│ Database and Repositories    │  │ LangGraph Orchestration    │
│                              │  │                            │
│ Objectives                   │  │ Shared execution state     │
│ Executions                   │  │ Dynamic controller         │
│ Evidence                     │  │ Conditional routing        │
│ Intelligence                 │  │ Retry policies             │
│ Recommendations              │  │ Human-review node          │
│ Approvals                    │  │ Execution budgets          │
│ Decision events              │  │                            │
└──────────────────────────────┘  └──────────────┬─────────────┘
                                                 │
                                                 ▼
                                  ┌────────────────────────────┐
                                  │     Specialist Agents      │
                                  │                            │
                                  │ Data Collection            │
                                  │ Intelligence Analysis      │
                                  │ Business Strategy          │
                                  └──────────────┬─────────────┘
                                                 │
                                                 ▼
                                  ┌────────────────────────────┐
                                  │      External Tools        │
                                  │                            │
                                  │ Google Places              │
                                  │ YouTube                    │
                                  │ Firecrawl                  │
                                  │ Direct Web Scraper         │
                                  │ OpenAI                     │
                                  └────────────────────────────┘
```

### Architectural responsibilities

| Layer | Responsibility |
|---|---|
| Routes | Receive HTTP requests and return HTML or JSON |
| Services | Coordinate application use cases |
| Orchestration | Select the next agent action |
| Agents | Perform specialized research, analysis, or strategy work |
| Tools | Communicate with external evidence sources |
| Schemas | Validate data crossing system boundaries |
| Repositories | Store and retrieve application records |
| Prompts | Define structured AI responsibilities |
| Templates | Present results to human users |
| Tests | Verify expected behavior and prevent regressions |

---

## Agent Architecture

### 1. Data Collection Agent

The data collection agent is responsible for acquiring usable evidence.

```text
Research request
      |
      v
Select source adapter
      |
      v
Call external tool
      |
      v
Normalize provider response
      |
      v
Validate evidence
      |
      v
Remove duplicates
      |
      v
Store usable evidence
```

It does not generate the final recommendation.

### 2. Intelligence Analysis Agent

The intelligence agent transforms evidence into structured business findings.

Its output can contain:

- Verified signals
- Hypotheses
- Contradictions
- Customer sentiment
- Customer problems
- Purchase intent
- Demand signals
- Competitor signals
- Location candidates
- Opportunities
- Risks
- Research gaps
- Next-best research actions
- Decision readiness

The agent separates evidence-backed findings from assumptions.

### 3. Business Strategy Agent

The strategy agent converts intelligence into decision alternatives.

It is responsible for:

- Creating meaningfully different strategies
- Comparing strategy tradeoffs
- Estimating opportunity and impact
- Evaluating feasibility and risk
- Extracting individual user requirements
- Producing direct requirement answers
- Building an adaptive final report
- Selecting the overall recommendation

---

## Dynamic Orchestration

The orchestration layer is implemented using a LangGraph `StateGraph`.

The controller reads the current execution state after every action.

Possible actions include:

```text
COLLECT
RETRY_COLLECTION
ANALYZE
GENERATE_STRATEGY
HUMAN_REVIEW
COMPLETE
FAIL
CANCEL
```

The controller considers:

- The original business objective
- Extracted user requirements
- Current evidence
- Evidence sufficiency
- Productive tool results
- Failed tool attempts
- Remaining retries
- Intelligence confidence
- Research gaps
- Location requirements
- Strategy availability
- Controller-cycle budget
- Tool-call budget
- Execution-time budget
- Cancellation status
- Human-review status

### Example adaptive branches

```text
No evidence
    -> collect evidence

Location requirement but no location candidates
    -> select Google Places research

Tool failure with retries available
    -> retry with an adjusted query

Low decision readiness
    -> collect additional evidence

Important contradiction
    -> investigate the conflicting signal

Sufficient intelligence but no recommendation
    -> generate and compare strategies

Recommendation ready
    -> pause for human review
```

---

## Evidence and Decision Quality

### Normalized evidence

External results are converted into a shared evidence format.

A normalized evidence record can include:

```json
{
  "evidence_id": "evidence-identifier",
  "source": "google_places",
  "title": "Place or source title",
  "url": "https://source.example",
  "content": "Useful extracted evidence",
  "metadata": {
    "address": "Formatted address",
    "rating": 4.4,
    "review_count": 250
  }
}
```

### Evidence validation

Collected records are checked for:

- Required content
- Supported source
- Safe URL
- Useful metadata
- Duplicate identifiers
- Duplicate URLs
- Provider errors
- Synthetic-data status

### Evidence grounding

Important intelligence and strategy claims reference evidence collected during the same execution.

Unknown evidence identifiers are rejected or removed.

### Location anti-fabrication

A proposed location candidate must match trusted collected metadata, including its name and formatted address.

If a candidate cannot be verified:

- It is not presented as a verified location
- Confidence is reduced
- The evidence gap is preserved
- Additional research can be requested
- The system does not invent a replacement

### Recommendation quality gate

The final quality gate rejects vague deferrals such as:

```text
Conduct market research.
Investigate suitable locations.
Identify the target audience.
Gather localized information.
Invest in inventory.
```

The agent is expected to provide the researched answer.

A high-quality requirement answer contains:

- Direct recommendation
- Suitability explanation
- Supporting evidence
- Confidence
- Risks
- Limitations
- Validation step

---

## Human Review

BuildSense AI uses a human-in-the-loop approval gate.

| Review action | Result |
|---|---|
| Approve | Accept the recommendation |
| Approve with modifications | Accept with recorded changes |
| Reject | Reject the recommendation |
| Request more analysis | Start follow-up analysis using human feedback |
| Retry | Create another execution |
| Cancel | Stop the execution |

Human feedback can be carried into follow-up planning while preserving the relationship between the original and subsequent executions.

Final reports are available only after the recommendation reaches an appropriate approval state.

---

## Outputs

### Dashboard

The dashboard presents:

- Objective information
- Execution status
- Controller decisions
- Tool attempts
- Evidence summary
- Intelligence findings
- Location candidates
- Strategy alternatives
- Requirement answers
- Overall recommendation
- Human-review controls

### Decision trail

The decision trail records observable execution events:

```text
Controller selected an action
Reason for the action
Tool selected
Tool input
Tool result
Evidence collected
Failure or retry
Intelligence readiness
Strategy comparison
Recommendation validation
Human-review decision
```

### JSON report

The JSON export provides a machine-readable result for integration with other systems.

### PDF report

The PDF output provides a professional human-readable business report containing the approved recommendation and supporting analysis.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Core programming language |
| Flask | Web application and REST API |
| LangGraph | Stateful agent orchestration |
| Pydantic | Runtime schema validation |
| Pydantic Settings | Environment-based configuration |
| MongoDB | Persistent document storage |
| PyMongo | MongoDB integration |
| OpenAI | Optional structured AI generation |
| Google Places API | Location and competitor evidence |
| YouTube Data API | Public content and market evidence |
| Firecrawl | Web content extraction |
| Beautiful Soup | Direct HTML parsing |
| ReportLab | PDF generation |
| PyPDF | PDF processing and validation |
| Jinja | HTML templates |
| Pytest | Automated testing |

---

## Project Structure

```text
buildsense-ai/
│
├── run.py
├── requirements.txt
├── README.md
│
├── config/
│   ├── settings.py
│   └── logging_config.py
│
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   ├── dashboard_routes.py
│   │   ├── api_routes.py
│   │   └── approval_routes.py
│   ├── services/
│   │   ├── objective_service.py
│   │   ├── execution_service.py
│   │   ├── approval_service.py
│   │   ├── dashboard_service.py
│   │   ├── readiness_service.py
│   │   └── pdf_report_service.py
│   ├── templates/
│   └── static/
│
├── orchestration/
│   ├── state.py
│   ├── graph_builder.py
│   ├── nodes.py
│   ├── retry_policies.py
│   └── hitl_node.py
│
├── agents/
│   ├── data_collection_agent/
│   ├── intelligence_analysis_agent/
│   └── business_strategy_agent/
│
├── core/
│   ├── execution_planner.py
│   ├── decision_trail_logger.py
│   ├── url_safety.py
│   ├── exceptions.py
│   └── utils.py
│
├── schemas/
│   ├── objective_schema.py
│   ├── collection_schema.py
│   ├── controller_schema.py
│   ├── intelligence_schema.py
│   ├── strategy_schema.py
│   └── approval_schema.py
│
├── prompts/
│   ├── planner_prompts.py
│   ├── intelligence_prompts.py
│   ├── strategy_prompts.py
│   └── recommendation_prompts.py
│
├── tools/
│   ├── tool_registry.py
│   ├── google_places_client.py
│   ├── youtube_client.py
│   ├── firecrawl_client.py
│   ├── scraper_client.py
│   └── openai_client.py
│
├── database/
    ├── connection.py
    ├── models/
    └── repositories/



```

---

## Getting Started

### Prerequisites

Install the following:

- Python 3.11 or newer
- `pip`
- Git
- Optional MongoDB database
- Optional external API credentials

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/buildsense-ai.git
cd buildsense-ai
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Windows Command Prompt

```bat
python -m venv .venv
.venv\Scripts\activate
```

#### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create `.env`

Create a file named `.env` in the project root.

```env
FLASK_ENV=development
SECRET_KEY=replace-this-with-a-secure-random-value
HOST=127.0.0.1
PORT=5000
DEBUG=true

USE_MEMORY_DB=true
MONGODB_URI=
MONGODB_DATABASE=buildsense_ai

OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini

YOUTUBE_API_KEY=
GOOGLE_MAPS_API_KEY=
FIRECRAWL_API_KEY=

REQUEST_TIMEOUT_SECONDS=15
MAX_SOURCE_ITEMS=30
MIN_EVIDENCE_ITEMS=3
MIN_EXTERNAL_TOOLS=3
MIN_ANALYSIS_CONFIDENCE=0.55

MAX_GRAPH_RETRIES=2
MAX_CONTROLLER_CYCLES=24
MAX_TOOL_CALLS=12
MAX_EXECUTION_SECONDS=180

ENABLE_AI_CONTROLLER=true
ENABLE_DEMO_DATA=false
ALLOW_PRIVATE_SOURCE_URLS=false
LOG_LEVEL=INFO
```

> Never commit `.env`, API keys, passwords, or private database connection strings.

### 5. Run the application

```bash
python run.py
```

Open the dashboard:

```text
http://127.0.0.1:5000
```

---

## Configuration

The primary configuration is defined in `config/settings.py`.

| Variable | Default | Description |
|---|---:|---|
| `FLASK_ENV` | `development` | Flask environment |
| `SECRET_KEY` | Generated | Flask session and CSRF secret |
| `HOST` | `127.0.0.1` | Development server host |
| `PORT` | `5000` | Development server port |
| `DEBUG` | `true` | Debug mode |
| `USE_MEMORY_DB` | `true` | Use in-memory storage |
| `MONGODB_URI` | Empty | MongoDB connection string |
| `MONGODB_DATABASE` | `buildsense_ai` | MongoDB database |
| `OPENAI_API_KEY` | Empty | OpenAI API credential |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Configured OpenAI model |
| `YOUTUBE_API_KEY` | Empty | YouTube Data API key |
| `GOOGLE_MAPS_API_KEY` | Empty | Google Places API key |
| `FIRECRAWL_API_KEY` | Empty | Firecrawl API key |
| `REQUEST_TIMEOUT_SECONDS` | `15` | External request timeout |
| `MAX_SOURCE_ITEMS` | `30` | Maximum collected source items |
| `MIN_EVIDENCE_ITEMS` | `3` | Minimum desired evidence |
| `MIN_EXTERNAL_TOOLS` | `3` | Desired external tool count |
| `MIN_ANALYSIS_CONFIDENCE` | `0.55` | Minimum analysis-confidence target |
| `MAX_GRAPH_RETRIES` | `2` | Maximum graph retries |
| `MAX_CONTROLLER_CYCLES` | `24` | Maximum controller iterations |
| `MAX_TOOL_CALLS` | `12` | Maximum external tool calls |
| `MAX_EXECUTION_SECONDS` | `180` | Maximum execution time |
| `ENABLE_AI_CONTROLLER` | `true` | Enable AI-assisted controller decisions |
| `ENABLE_DEMO_DATA` | `false` | Allow clearly marked demo evidence |
| `ALLOW_PRIVATE_SOURCE_URLS` | `false` | Allow private-network source URLs |
| `LOG_LEVEL` | `INFO` | Application logging level |

---

## External Integrations

All integrations are optional. The application can use local deterministic fallback behavior when supported integrations are not configured.

### OpenAI

```env
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4.1-mini
```

### MongoDB

```env
USE_MEMORY_DB=false
MONGODB_URI=mongodb+srv://username:password@cluster.example.mongodb.net/
MONGODB_DATABASE=buildsense_ai
```

For local in-memory execution:

```env
USE_MEMORY_DB=true
```

### Google Places

```env
GOOGLE_MAPS_API_KEY=your-google-maps-key
```

Enable **Places API (New)** in Google Cloud and restrict the key to the required API.

### YouTube Data API

```env
YOUTUBE_API_KEY=your-youtube-api-key
```

### Firecrawl

```env
FIRECRAWL_API_KEY=your-firecrawl-api-key
```

---

## REST API

### Health check

```bash
curl http://127.0.0.1:5000/api/health
```

The health endpoint reports configured integrations without exposing credentials.

### Create an objective

```bash
curl -X POST http://127.0.0.1:5000/api/objectives \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Quality shoe shop opportunity",
    "description": "Find a suitable Colombo location, target audience, product mix, pricing strategy, marketing plan, and operational improvements.",
    "keywords": [
      "shoe shop",
      "footwear",
      "Colombo"
    ]
  }'
```

### Get execution status

```bash
curl http://127.0.0.1:5000/api/executions/EXECUTION_ID
```

Replace `EXECUTION_ID` with the identifier returned by the create-objective endpoint.

### Live integration readiness check

```bash
curl -X POST http://127.0.0.1:5000/api/readiness \
  -H "Content-Type: application/json" \
  -d '{
    "live": true,
    "query": "Sri Lanka footwear retailer customer demand",
    "source_url": "https://example.com/public-source"
  }'
```

---

## Testing

Run the complete test suite:

```bash
pytest -q
```

Run one test file:

```bash
pytest tests/test_orchestration_graph.py -q
```

Run one test function:

```bash
pytest tests/test_orchestration_graph.py::test_name -q
```

### Test coverage areas

The project includes tests for:

- Objective and schema validation
- Data collection
- Evidence validation
- Evidence deduplication
- Intelligence analysis
- Strategy generation
- Recommendation quality
- Dynamic controller routing
- Tool retry behavior
- Execution budgets
- Human approval
- Dashboard routes
- PDF reports
- Prompt contracts
- Business scenarios
- Location recommendation behavior
- Anti-fabrication controls

---

## Security and Reliability

BuildSense AI includes the following safeguards:

### Input and output validation

- Pydantic schema validation
- Structured AI responses
- Required-field validation
- Evidence-reference validation
- Approval-state validation

### Web safety

- CSRF-protected dashboard actions
- Public URL validation
- Unsupported URL-scheme rejection
- Private-network URL blocking
- Loopback-address blocking
- Basic SSRF protection

### Agent safety

- Finite controller action set
- Controller-cycle limits
- Tool-call limits
- Retry limits
- Maximum execution time
- Cancellation support
- Human approval requirement

### Evidence safety

- Evidence deduplication
- Source metadata preservation
- Unknown evidence-ID rejection
- Location anti-fabrication
- Synthetic-data labeling
- No automatic presentation of demo evidence as live proof

### Failure handling

- External tool failure recording
- Query adjustment and retry
- Alternative-tool selection
- OpenAI local fallback
- In-memory database option
- Controlled terminal failure
- Transparent limitations and confidence

---

## Documentation

Beginner-friendly code documentation is available in:

```text
docs/study_guide/README.md
```

The study guide covers:

1. Product goal and project map
2. Python foundations
3. Application startup
4. Flask routes
5. Database models and repositories
6. Execution service and shared state
7. LangGraph controller
8. Research planning and tools
9. Intelligence analysis
10. Strategy generation
11. Human approval and reports
12. Security, testing, and debugging

---

## Recommended Demonstration Flow

For a realistic demonstration:

1. Configure live external integrations.
2. Start the Flask application.
3. Submit a new business objective.
4. Monitor the execution status.
5. Inspect controller decisions.
6. Inspect external tool attempts.
7. Confirm that real evidence was collected.
8. Review intelligence findings.
9. Compare generated strategies.
10. Inspect direct requirement answers.
11. Approve the recommendation.
12. Download the JSON and PDF reports.

Avoid using hardcoded or prefetched results as live execution evidence.

---

## Project Status

BuildSense AI is currently an MVP intended for:

- Agentic AI demonstrations
- Business research experiments
- Multi-agent architecture learning
- Human-in-the-loop workflow exploration
- Evidence-grounded recommendation research
- Portfolio and academic projects

It should not be treated as professional financial, legal, medical, or investment advice.

---

## Production Considerations

Before deploying the system for production use, consider adding:

- User authentication
- Role-based access control
- Tenant isolation
- Durable background-job processing
- Redis, Celery, RQ, or another job queue
- Production WSGI server
- Database migrations and indexing
- Idempotent execution handling
- Rate limiting
- Centralized secrets management
- Distributed tracing
- Metrics and alerting
- Cost and token monitoring
- Data-retention controls
- Audit-log retention
- Database backup and recovery
- Source-specific compliance checks
- Automated recommendation evaluation
- Broader geographic and market datasets
- Load, security, and penetration testing

## GitHub Topics

Suggested repository topics:

```text
python
flask
langgraph
ai-agents
multi-agent-system
business-intelligence
autonomous-agent
human-in-the-loop
market-research
recommendation-system
openai
mongodb
google-places
pydantic
pytest
```

---

## License

This repository does not automatically grant permission for commercial use, redistribution, or modification unless a license file is added.

Before publishing the repository, select a license that matches your intended use.

Common options include:

- MIT License
- Apache License 2.0
- GNU General Public License
- Proprietary or all-rights-reserved license

---


## Acknowledgements

BuildSense AI uses open-source and external technologies including Python, Flask, LangGraph, Pydantic, MongoDB, OpenAI, Google Places, YouTube, Firecrawl, Beautiful Soup, ReportLab, PyPDF, Jinja, and Pytest.

---

<div align="center">

### BuildSense AI

Evidence-backed business research, adaptive strategy generation, and human-controlled decision intelligence.

</div>