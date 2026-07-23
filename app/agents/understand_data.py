import pandas as pd
from app.state import PipelineState
from app.schemas import ProfileSummary
from app.llm import get_llm
from app.utils.data_profiler import profile_dataframe
import json
import logging

logger = logging.getLogger(__name__)


def understand_data(state: PipelineState) -> PipelineState:
    try:
        df = pd.read_csv(state["file_path"]) if state["file_path"].endswith(".csv") else pd.read_excel(state["file_path"])
        data_profile = profile_dataframe(df)
        state["data_profile"] = data_profile
        profile_summary_text = json.dumps({
            "shape": data_profile["shape"],
            "columns": data_profile["columns"],
            "dtypes": data_profile["dtypes"],
            "missing_percentages": data_profile["missing_percentages"],
            "describe": data_profile["describe"],
            "nunique": data_profile["nunique"],
            "duplicate_rows": data_profile["duplicate_rows"],
            "sample_rows": data_profile["sample_rows"],
        }, indent=2)
        llm = get_llm("descriptive")
        prompt = f"""You are a data analysis assistant. Analyze this dataset profile and provide insights.

Dataset Profile:
{profile_summary_text}

Provide: 1) a brief description, 2) best guess target column or null, 3) data quality notes with severity.

Return JSON: {{"dataset_description": "...", "target_column_guess": null, "notes": [{{"column": "...", "issue": "...", "severity": "low|medium|high"}}]}}"""
        try:
            structured_llm = llm.with_structured_output(ProfileSummary)
            result = structured_llm.invoke(prompt)
            state["profile_summary_text"] = result.dataset_description
            state["data_profile"]["llm_analysis"] = result.model_dump()
        except Exception as e:
            logger.warning(f"Failed to get structured output from LLM: {e}")
            state["profile_summary_text"] = "Dataset profile computed. LLM analysis unavailable."
        state["status"] = "running"
    except Exception as e:
        logger.error(f"Error in understand_data: {e}")
        state["errors"].append(f"understand_data failed: {str(e)}")
        state["status"] = "failed"
    return state
