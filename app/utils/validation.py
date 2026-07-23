import pandas as pd
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

VALID_PREPROCESSING_OPS = {"drop_column", "drop_duplicate_rows", "fill_missing", "drop_rows_missing", "remove_outliers", "encode_categorical", "scale_numeric", "convert_dtype", "rename_column", "parse_datetime"}
VALID_FILL_STRATEGIES = {"mean", "median", "mode", "constant", "ffill", "bfill"}
VALID_OUTLIER_METHODS = {"iqr", "zscore"}
VALID_ENCODING_METHODS = {"one_hot", "label", "ordinal"}
VALID_SCALING_METHODS = {"standard", "minmax", "robust"}
VALID_TARGET_TYPES = {"int", "float", "str", "category", "bool"}
VALID_CHART_TYPES = {"histogram", "bar", "line", "scatter", "box", "correlation_heatmap", "pie", "count_plot"}
VALID_AGGREGATIONS = {"sum", "mean", "count", "median"}


def validate_preprocessing_plan(plan: List[Dict[str, Any]], df_columns: List[str]) -> tuple[bool, List[str]]:
    errors = []
    if not isinstance(plan, list):
        errors.append("Preprocessing plan must be a list")
        return False, errors
    for i, step in enumerate(plan):
        if not isinstance(step, dict):
            errors.append(f"Step {i}: must be a dictionary")
            continue
        op = step.get("op")
        if op not in VALID_PREPROCESSING_OPS:
            errors.append(f"Step {i}: invalid operation '{op}'")
            continue
        columns = step.get("columns", [])
        params = step.get("params", {})
        if op != "drop_duplicate_rows":
            for col in columns:
                if col not in df_columns:
                    errors.append(f"Step {i}: column '{col}' not found in dataframe")
        if op == "fill_missing":
            strategy = params.get("strategy")
            if strategy and strategy not in VALID_FILL_STRATEGIES:
                errors.append(f"Step {i}: invalid fill strategy '{strategy}'")
        elif op == "remove_outliers":
            method = params.get("method")
            if method and method not in VALID_OUTLIER_METHODS:
                errors.append(f"Step {i}: invalid outlier method '{method}'")
        elif op == "encode_categorical":
            method = params.get("method")
            if method and method not in VALID_ENCODING_METHODS:
                errors.append(f"Step {i}: invalid encoding method '{method}'")
        elif op == "scale_numeric":
            method = params.get("method")
            if method and method not in VALID_SCALING_METHODS:
                errors.append(f"Step {i}: invalid scaling method '{method}'")
        elif op == "convert_dtype":
            target_type = params.get("target_type")
            if target_type and target_type not in VALID_TARGET_TYPES:
                errors.append(f"Step {i}: invalid target type '{target_type}'")
        elif op == "rename_column":
            if len(columns) != 1:
                errors.append(f"Step {i}: rename_column requires exactly one column")
            if "new_name" not in params:
                errors.append(f"Step {i}: rename_column requires 'new_name' parameter")
    return len(errors) == 0, errors


def validate_chart_plan(plan: List[Dict[str, Any]], df: pd.DataFrame) -> tuple[bool, List[str]]:
    errors = []
    if not isinstance(plan, list):
        errors.append("Chart plan must be a list")
        return False, errors
    for i, chart_spec in enumerate(plan):
        if not isinstance(chart_spec, dict):
            errors.append(f"Chart {i}: must be a dictionary")
            continue
        chart_type = chart_spec.get("chart_type")
        if chart_type not in VALID_CHART_TYPES:
            errors.append(f"Chart {i}: invalid chart type '{chart_type}'")
            continue
        x = chart_spec.get("x")
        y = chart_spec.get("y")
        hue = chart_spec.get("hue")
        columns = chart_spec.get("columns")
        agg = chart_spec.get("agg")
        if x and x not in df.columns:
            errors.append(f"Chart {i}: x column '{x}' not found")
        if y and y not in df.columns:
            errors.append(f"Chart {i}: y column '{y}' not found")
        if hue and hue not in df.columns:
            errors.append(f"Chart {i}: hue column '{hue}' not found")
        if columns:
            for col in columns:
                if col not in df.columns:
                    errors.append(f"Chart {i}: column '{col}' not found")
        if agg and agg not in VALID_AGGREGATIONS:
            errors.append(f"Chart {i}: invalid aggregation '{agg}'")
        if chart_type in ["histogram", "scatter", "line"]:
            if x and not pd.api.types.is_numeric_dtype(df[x]):
                errors.append(f"Chart {i}: {chart_type} requires numeric x column")
            if y and not pd.api.types.is_numeric_dtype(df[y]):
                errors.append(f"Chart {i}: {chart_type} requires numeric y column")
        elif chart_type == "correlation_heatmap":
            if columns:
                numeric_cols = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
                if len(numeric_cols) < 2:
                    errors.append(f"Chart {i}: correlation_heatmap requires at least 2 numeric columns")
            else:
                numeric_count = len(df.select_dtypes(include=["number"]).columns)
                if numeric_count < 2:
                    errors.append(f"Chart {i}: correlation_heatmap requires at least 2 numeric columns in dataframe")
    return len(errors) == 0, errors


def get_fallback_preprocessing_plan(df: pd.DataFrame = None, columns: List[str] = None) -> List[Dict[str, Any]]:
    plan = []
    if df is not None:
        for col in df.columns:
            if df[col].isna().sum() == len(df):
                plan.append({"op": "drop_column", "columns": [col], "params": {}, "reason": f"Column '{col}' is 100% missing"})
        for col in df.columns:
            if df[col].isna().sum() > 0:
                if pd.api.types.is_numeric_dtype(df[col]):
                    plan.append({"op": "fill_missing", "columns": [col], "params": {"strategy": "median"}, "reason": f"Fill missing values in numeric column '{col}' with median"})
                else:
                    plan.append({"op": "fill_missing", "columns": [col], "params": {"strategy": "mode"}, "reason": f"Fill missing values in categorical column '{col}' with mode"})
        for col in df.columns:
            if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
                cardinality = df[col].nunique()
                if cardinality <= 10 and cardinality > 1:
                    plan.append({"op": "encode_categorical", "columns": [col], "params": {"method": "one_hot"}, "reason": f"One-hot encode low-cardinality categorical column '{col}'"})
    elif columns is not None:
        for col in columns:
            plan.append({"op": "fill_missing", "columns": [col], "params": {"strategy": "median"}, "reason": f"Fill missing values in column '{col}' with median"})
    return plan


def get_fallback_chart_plan(df: pd.DataFrame) -> List[Dict[str, Any]]:
    plan = []
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    for col in numeric_cols[:3]:
        plan.append({"chart_type": "histogram", "title": f"Distribution of {col}", "x": col, "reason": f"Show distribution of numeric column '{col}'"})
    for col in categorical_cols[:3]:
        plan.append({"chart_type": "bar", "title": f"Count of {col}", "x": col, "reason": f"Show value counts for categorical column '{col}'"})
    if len(numeric_cols) >= 2:
        plan.append({"chart_type": "correlation_heatmap", "title": "Correlation Heatmap", "columns": numeric_cols[:10], "reason": "Show correlations between numeric columns"})
    return plan[:8]
