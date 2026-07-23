# 🧠 Smart Data Pipeline

**Agentic Data Preprocessing & Visualization Pipeline**

A web application where users upload raw data files (`.xlsx` / `.csv`) and a **multi-agent AI pipeline** automatically understands the dataset, plans and executes preprocessing operations, and generates relevant visualizations — with zero manual data wrangling.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Why This Project

Cleaning and exploring a new dataset is repetitive. This pipeline automates that entire workflow using a **team of specialized AI agents**, while keeping every operation deterministic, auditable, and safe.

> **Core principle:** LLM agents only **plan** — they output structured, validated JSON describing *what* to do. Deterministic Python code (pandas / scikit-learn / matplotlib) **executes** those plans. No LLM ever touches raw data cell values directly.

---

## 🏗️ Architecture

```
[Browser: Upload Form]
        │  POST /api/analyze
        ▼
[FastAPI Endpoint] → saves file → kicks off LangGraph run → returns job result
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│                     LangGraph StateGraph                        │
│  Node 1 → understand_data        (local LLM: qwen2.5:3b)         │
│  Node 2 → plan_preprocessing     (API LLM: gpt-4o-mini)          │
│  Node 3 → execute_preprocessing  (pure Python, no LLM)           │
│  Node 4 → plan_charts            (API LLM: gpt-4o-mini)          │
│  Node 5 → generate_charts        (pure Python, no LLM)           │
│  Edges: linear   1 → 2 → 3 → 4 → 5 → END                        │
└───────────────────────────────────────────────────────────────┘
```

---

## 🚀 Features

- 🔍 Automated Data Understanding (local LLM, zero cost per run)
- 🧩 Intelligent Preprocessing Planning (API LLM)
- ✅ Safe, Validated Execution with graceful fallback
- 📊 Automatic Visualization
- 🔁 Error Recovery (retry-and-repair loops)
- 🔒 Privacy by Design — raw data never sent to API LLMs
- 🔌 Swappable LLM Providers via `.env`

---

## 🧰 Tech Stack

FastAPI · LangGraph (StateGraph) · OpenAI `gpt-4o-mini` / Anthropic `claude-haiku` · Ollama `qwen2.5:3b` · pandas / numpy / scikit-learn · matplotlib + seaborn · Pydantic v2

---

## 📦 Installation

```bash
git clone https://github.com/abdelrhmanmustafakolkela/agentic-data-preprocessing-pipeline.git
cd agentic-data-preprocessing-pipeline
pip install -r requirements.txt
cp .env.example .env
# fill in your OPENAI_API_KEY / ANTHROPIC_API_KEY
ollama pull qwen2.5:3b
ollama serve
```

---

## ▶️ Usage

```bash
python -m app.main
# or
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000`, upload a `.csv`/`.xlsx`, click **Process Data**.

---

## ⚙️ Configuration (`.env`)

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | Required for the planning LLM |
| `PLANNING_LLM_PROVIDER` | `openai` or `anthropic` |
| `PLANNING_LLM_MODEL` | e.g. `gpt-4o-mini` |
| `LOCAL_LLM_PROVIDER` | `ollama` |
| `LOCAL_LLM_MODEL` | e.g. `qwen2.5:3b` |
| `OLLAMA_BASE_URL` | Default `http://localhost:11434` |
| `MAX_UPLOAD_SIZE_MB` | Default `25` |

---

## 📁 Project Structure

```
app/
├── main.py            # FastAPI app, endpoints
├── config.py          # settings
├── llm.py             # get_llm() factory
├── graph.py           # LangGraph StateGraph
├── state.py           # PipelineState
├── schemas.py         # Pydantic models
├── jobs.py            # job store
├── agents/            # the 5 pipeline nodes
└── utils/              # profiler, ops dispatch tables, validation
frontend/index.html
requirements.txt
.env.example
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analyze` | Upload a file and start processing |
| `GET` | `/api/jobs/{job_id}` | Poll job status |
| `GET` | `/api/download/{job_id}/csv` | Download cleaned CSV |
| `GET` | `/api/download/{job_id}/xlsx` | Download cleaned XLSX |
| `GET` | `/` | Serve the frontend |

---

## ✅ Acceptance Criteria

- ✅ Upload returns cleaned dataset + relevant charts
- ✅ Invalid LLM JSON triggers self-correction or fallback
- ✅ No raw dataset content sent to API LLMs
- ✅ `cleaning_log` matches actual execution
- ✅ Cleaned data downloadable as CSV & XLSX
- ✅ Switching LLM providers needs no code changes outside `llm.py`

---

## 🗺️ Roadmap

- [ ] Support JSON/Parquet
- [ ] Auth layer for multi-user deployments
- [ ] Persist job history in a real database
- [ ] Chart customization UI

---

## 📄 License

MIT License.
