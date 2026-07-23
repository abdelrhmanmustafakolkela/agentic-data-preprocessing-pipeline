import pandas as pd
import os
from pathlib import Path
from app.state import PipelineState
from app.utils.preprocessing_ops import apply_preprocessing_plan
from app.utils.data_profiler import profile_dataframe
import logging

logger = logging.getLogger(__name__)


def execute_preprocessing(state: PipelineState) -> PipelineState:
    """
    Node 3: Execute the preprocessing plan using pure Python (pandas/sklearn).
    No LLM involved - deterministic execution of the plan.
    """
    try:
        df = pd.read_csv(state["file_path"]) if state["file_path"].endswith(".csv") else pd.read_excel(state["file_path"])
        cleaned_df, cleaning_log = apply_preprocessing_plan(df, state["preprocessing_plan"])
        state["cleaning_log"] = cleaning_log
        base_name = Path(state["original_filename"]).stem
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        csv_path = output_dir / f"{base_name}_cleaned.csv"
        xlsx_path = output_dir / f"{base_name}_cleaned.xlsx"
        cleaned_df.to_csv(csv_path, index=False)
        cleaned_df.to_excel(xlsx_path, index=False)
        state["cleaned_file_path"] = str(csv_path)
        state["post_clean_profile"] = profile_dataframe(cleaned_df)
        state["status"] = "running"
    except Exception as e:
        logger.error(f"Error in execute_preprocessing: {e}")
        state["errors"].append(f"execute_preprocessing failed: {str(e)}")
        state["status"] = "failed"
    return state
