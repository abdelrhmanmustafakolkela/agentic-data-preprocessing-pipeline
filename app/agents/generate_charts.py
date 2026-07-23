import pandas as pd
from app.state import PipelineState
from app.utils.chart_ops import generate_charts as generate_charts_from_plan
import logging

logger = logging.getLogger(__name__)


def generate_charts(state: PipelineState) -> PipelineState:
    """
    Node 5: Generate charts based on the chart plan using pure Python (matplotlib/seaborn).
    """
    try:
        df = pd.read_csv(state["cleaned_file_path"]) if state["cleaned_file_path"].endswith(".csv") else pd.read_excel(state["cleaned_file_path"])
        charts = generate_charts_from_plan(df, state["chart_plan"])
        state["charts"] = charts
        state["status"] = "done"
    except Exception as e:
        logger.error(f"Error in generate_charts: {e}")
        state["errors"].append(f"generate_charts failed: {str(e)}")
        state["status"] = "failed"
    return state
