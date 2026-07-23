import pandas as pd
from app.state import PipelineState
from app.schemas import ChartPlan
from app.llm import get_llm
from app.utils.validation import validate_chart_plan, get_fallback_chart_plan
import json
import logging

logger = logging.getLogger(__name__)


def plan_charts(state: PipelineState) -> PipelineState:
    max_retries = 3
    try:
        df = pd.read_csv(state["cleaned_file_path"]) if state["cleaned_file_path"].endswith(".csv") else pd.read_excel(state["cleaned_file_path"])
        llm = get_llm("planning")
        profile_summary = json.dumps({"shape": state["post_clean_profile"]["shape"], "columns": state["post_clean_profile"]["columns"], "dtypes": state["post_clean_profile"]["dtypes"], "nunique": state["post_clean_profile"]["nunique"]}, indent=2)
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        prompt = f"""You are a data visualization expert. Analyze the following cleaned dataset profile and create a chart plan.

Dataset Profile:
{profile_summary}

Numeric columns: {numeric_cols}
Categorical columns: {categorical_cols}

Available chart types: histogram, bar, line, scatter, box, correlation_heatmap, pie, count_plot.

Create a chart plan with 5-10 charts. Return JSON: {{"charts": [{{"chart_type": "...", "title": "...", "x": "...", "y": null, "hue": null, "agg": null, "columns": null, "reason": "..."}}]}}"""
        for attempt in range(max_retries):
            try:
                structured_llm = llm.with_structured_output(ChartPlan)
                result = structured_llm.invoke(prompt)
                plan_dict = result.model_dump()
                chart_specs = plan_dict["charts"]
                is_valid, errors = validate_chart_plan(chart_specs, df)
                if is_valid:
                    state["chart_plan"] = chart_specs[:10]
                    state["status"] = "running"
                    return state
                else:
                    logger.warning(f"Validation failed (attempt {attempt + 1}): {errors}")
                    if attempt < max_retries - 1:
                        prompt += f"\n\nYour previous plan had these validation errors:\n{json.dumps(errors, indent=2)}\n\nPlease fix these issues and try again."
                    else:
                        state["chart_plan"] = get_fallback_chart_plan(df)
                        state["errors"].append(f"Chart plan validation failed after {max_retries} attempts, using fallback plan")
            except Exception as e:
                logger.warning(f"LLM call failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    state["chart_plan"] = get_fallback_chart_plan(df)
                    state["errors"].append(f"Chart plan LLM failed after {max_retries} attempts, using fallback plan")
        state["status"] = "running"
    except Exception as e:
        logger.error(f"Error in plan_charts: {e}")
        state["errors"].append(f"plan_charts failed: {str(e)}")
        state["status"] = "failed"
    return state
