# 🧠 Smart Data Pipeline

**Agentic Data Preprocessing & Visualization Pipeline**

A web application where users upload raw data files (`.xlsx` / `.csv`) and a **multi-agent AI pipeline** automatically understands the dataset, plans and executes preprocessing operations, and generates relevant visualizations — with zero manual data wrangling.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Why This Project

Cleaning and exploring a new dataset is repetitive: check for missing values, fix types, encode categoricals, pick the right chart... This pipeline automates that entire workflow using a **team of specialized AI agents**, while keeping every operation deterministic, auditable, and safe.

> **Core principle:** LLM agents only **plan** — they output structured, validated JSON describing *what* to do. Deterministic Python code (pandas / scikit-learn / matplotlib) **executes** those plans. No LLM ever touches raw data cell values directly.

This design keeps the pipeline **reliable, auditable, and cheap to run**.

---

## 🏗️ Architecture

```
[Browser: Upload Form]
        │  POST /api/analyze  (multipart/form-data, field: "file")
        ▼
[FastAPI Endpoint] → saves file → kicks off LangGraph run → returns job result
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│                     LangGraph StateGraph                        │
│                                                                   │
│  Node 1 → understand_data        (local LLM: qwen2.5:3b)         │
│  Node 2 → plan_preprocessing     (API LLM: gpt-4o-mini)          │
│  Node 3 → execute_preprocessing  (pure Python, no LLM)           │
│  Node 4 → plan_charts            (API LLM: gpt-4o-mini)          │
│  Node 5 → generate_charts        (pure Python, no LLM)           │
│                                                                   │
│  Edges: linear   1 → 2 → 3 → 4 → 5 → END                        │
└───────────────────────────────────────────────────────────────┘
```

| Stage | Agent | Engine | Role |
|---|---|---|---|
| 1 | `understand_data` | Local LLM (Ollama) | Profiles data structure & quality issues |
| 2 | `plan_preprocessing` | API LLM | Builds a tailored, structured cleaning plan |
| 3 | `execute_preprocessing` | Pure Python | Executes the plan with pandas / scikit-learn |
| 4 | `plan_charts` | API LLM | Decides which visualizations best fit the data |
| 5 | `generate_charts` | Pure Python | Renders charts with matplotlib / seaborn |

---

## 🚀 Features

- 🔍 **Automated Data Understanding** — a local LLM profiles structure & quality issues, with zero cost per run
- 🧩 **Intelligent Preprocessing Planning** — an API LLM designs a cleaning plan tailored to the actual dataset
- ✅ **Safe, Validated Execution** — every LLM plan is validated against the real dataframe before running, with graceful fallback to safe defaults
- 📊 **Automatic Visualization** — relevant charts are chosen and generated based on the data's characteristics
- 🔁 **Error Recovery** — retry-and-repair loops handle malformed LLM responses
- 🔒 **Privacy by Design** — raw data is never sent to API-based LLMs, only computed summaries
- 🔌 **Swappable LLM Providers** — switch between OpenAI and Anthropic (or local models) via `.env`, no code changes needed

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Orchestration | LangGraph (StateGraph) |
| Planning LLM | OpenAI `gpt-4o-mini` or Anthropic `claude-haiku` (configurable) |
| Descriptive LLM | Local model via Ollama — `qwen2.5:3b` (runs on 4GB VRAM) |
| Data Processing | pandas, numpy, scikit-learn |
| Charting | matplotlib + seaborn (server-side rendering to PNG) |
| Validation | Pydantic v2 models for every LLM JSON response |
| Frontend | Single-page HTML (vanilla JS + fetch) |

---

## 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/smart-data-pipeline.git
cd smart-data-pipeline

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# then fill in your OPENAI_API_KEY / ANTHROPIC_API_KEY

# 4. Pull and run the local model
ollama pull qwen2.5:3b
ollama serve
```

---

## ▶️ Usage

```bash
# Start the FastAPI server
python -m app.main

# or, using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

1. Open your browser at `http://localhost:8000`
2. Upload a `.csv` or `.xlsx` file and click **Process Data**
3. The pipeline will:
   - Analyze your data structure and quality
   - Plan and apply appropriate preprocessing steps
   - Clean the data (missing values, encoding, etc.)
   - Plan and generate relevant charts
   - Provide download links for the cleaned dataset

---

## ⚙️ Configuration

Set these in your `.env` file:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | Required for the planning LLM |
| `PLANNING_LLM_PROVIDER` | `openai` or `anthropic` |
| `PLANNING_LLM_MODEL` | e.g. `gpt-4o-mini`, `claude-haiku` |
| `LOCAL_LLM_PROVIDER` | `ollama` (only supported option) |
| `LOCAL_LLM_MODEL` | e.g. `qwen2.5:3b` |
| `OLLAMA_BASE_URL` | Default: `http://localhost:11434` |
| `MAX_UPLOAD_SIZE_MB` | Default: `25` |

---

## 📁 Project Structure

```
smart-data-pipeline/
├── app/
│   ├── main.py                       # FastAPI app, endpoints, static file serving
│   ├── config.py                     # settings (pydantic-settings, reads .env)
│   ├── llm.py                        # get_llm() factory
│   ├── graph.py                      # builds & compiles the LangGraph StateGraph
│   ├── state.py                      # PipelineState TypedDict
│   ├── schemas.py                    # all Pydantic models
│   ├── jobs.py                       # in-memory job store + status tracking
│   ├── agents/
│   │   ├── understand_data.py        # Node 1
│   │   ├── plan_preprocessing.py     # Node 2
│   │   ├── execute_preprocessing.py  # Node 3
│   │   ├── plan_charts.py            # Node 4
│   │   └── generate_charts.py        # Node 5
│   └── utils/
│       ├── data_profiler.py          # pure-pandas profiling functions
│       ├── preprocessing_ops.py      # dispatch table: op name -> pandas/sklearn function
│       ├── chart_ops.py              # dispatch table: chart_type -> matplotlib function
│       └── validation.py             # cross-checks LLM plans against actual dataframe
├── frontend/
│   └── index.html
├── outputs/                          # generated cleaned files (gitignored)
├── uploads/                          # temp uploaded files (gitignored)
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analyze` | Upload a file and start processing |
| `GET` | `/api/jobs/{job_id}` | Poll job status |
| `GET` | `/api/download/{job_id}/csv` | Download the cleaned CSV |
| `GET` | `/api/download/{job_id}/xlsx` | Download the cleaned XLSX |
| `GET` | `/` | Serve the frontend |

---

## ✅ Acceptance Criteria

- ✅ Uploading a `.xlsx` / `.csv` returns a cleaned dataset + relevant charts
- ✅ Invalid LLM JSON triggers self-correction or graceful fallback
- ✅ No raw full-dataset content is ever sent to an API-based LLM
- ✅ Preprocessing operations in the `cleaning_log` match actual execution
- ✅ Cleaned data downloadable as both CSV and XLSX
- ✅ Switching LLM providers via `.env` requires no code changes outside `llm.py`

---

## 🗺️ Roadmap

- [ ] Support additional file formats (JSON, Parquet)
- [ ] Add an authentication layer for multi-user deployments
- [ ] Persist job history in a real database instead of in-memory storage
- [ ] Add a chart customization UI

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](../../issues).

## 📄 License

This project is licensed under the MIT License.
