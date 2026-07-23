from app.state import PipelineState
from app.schemas import PreprocessingPlan
from app.llm import get_llm
from app.utils.validation import validate_preprocessing_plan, get_fallback_preprocessing_plan
import json
import logging

logger = logging.getLogger(__name__)


def plan_preprocessing(state: PipelineState) -> PipelineState:
    max_retries = 3
    try:
        llm = get_llm("planning")
        profile_summary = json.dumps({
            "shape": state["data_profile"]["shape"],
            "columns": state["data_profile"]["columns"],
            "dtypes": state["data_profile"]["dtypes"],
            "missing_percentages": state["data_profile"]["missing_percentages"],
            "nunique": state["data_profile"]["nunique"],
            "duplicate_rows": state["data_profile"]["duplicate_rows"],
            "llm_notes": state["data_profile"].get("llm_analysis", {}),
        }, indent=2)
        prompt = f"""You are a data preprocessing expert. Analyze this dataset profile and create a preprocessing plan.

Dataset Profile:
{profile_summary}

Available operations: drop_column, drop_duplicate_rows, fill_missing, drop_rows_missing, remove_outliers, encode_categorical, scale_numeric, convert_dtype, rename_column, parse_datetime.

Create a plan with 3-8 steps. Return JSON: {{"steps": [{{"op": "...", "columns": ["..."], "params": {{}}, "reason": "..."}}]}}"""
        for attempt in range(max_retries):
            try:
                structured_llm = llm.with_structured_output(PreprocessingPlan)
                result = structured_llm.invoke(prompt)
                plan_dict = result.model_dump()
                plan_steps = plan_dict["steps"]
                df_columns = state["data_profile"]["columns"]
                is_valid, errors = validate_preprocessing_plan(plan_steps, df_columns)
                if is_valid:
                    state["preprocessing_plan"] = plan_steps
                    state["status"] = "running"
                    return state
                else:
                    logger.warning(f"Validation failed (attempt {attempt + 1}): {errors}")
                    if attempt < max_retries - 1:
                        prompt += f"\n\nYour previous plan had these validation errors:\n{json.dumps(errors, indent=2)}\n\nPlease fix these issues and try again."
                    else:
                        state["preprocessing_plan"] = get_fallback_preprocessing_plan(columns=df_columns)
                        state["errors"].append(f"Preprocessing plan validation failed after {max_retries} attempts, using fallback plan")
            except Exception as e:
                logger.warning(f"LLM call failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    state["preprocessing_plan"] = get_fallback_preprocessing_plan(columns=state["data_profile"]["columns"])
                    state["errors"].append(f"Preprocessing plan LLM failed after {max_retries} attempts, using fallback plan")
        state["status"] = "running"
    except Exception as e:
        logger.error(f"Error in plan_preprocessing: {e}")
        state["errors"].append(f"plan_preprocessing failed: {str(e)}")
        state["status"] = "failed"
    return state
