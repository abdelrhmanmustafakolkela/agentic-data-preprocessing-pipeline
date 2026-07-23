import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


def drop_column(df: pd.DataFrame, columns: List[str], params: Dict[str, Any]) -> Tuple[pd.DataFrame, str]:
    existing_cols = [col for col in columns if col in df.columns]
    if not existing_cols:
        return df, f"No columns to drop (specified columns not found: {columns})"
    df = df.drop(columns=existing_cols)
    return df, f"Dropped columns: {existing_cols}"


def drop_duplicate_rows(df: pd.DataFrame, columns: List[str], params: Dict[str, Any]) -> Tuple[pd.DataFrame, str]:
    initial_count = len(df)
    df = df.drop_duplicates()
    dropped = initial_count - len(df)
    return df, f"Dropped {dropped} duplicate rows"


def fill_missing(df: pd.DataFrame, columns: List[str], params: Dict[str, Any]) -> Tuple[pd.DataFrame, str]:
    strategy = params.get("strategy", "median")
    value = params.get("value")
    logs = []
    for col in columns:
        if col not in df.columns:
            continue
        if df[col].isna().sum() == 0:
            continue
        missing_count = df[col].isna().sum()
        if strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
            fill_value = df[col].mean()
            df[col] = df[col].fillna(fill_value)
            logs.append(f"Filled {missing_count} missing values in '{col}' using mean ({fill_value:.2f})")
        elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
            fill_value = df[col].median()
            df[col] = df[col].fillna(fill_value)
            logs.append(f"Filled {missing_count} missing values in '{col}' using median ({fill_value:.2f})")
        elif strategy == "mode":
            fill_value = df[col].mode()[0] if not df[col].mode().empty else "unknown"
            df[col] = df[col].fillna(fill_value)
            logs.append(f"Filled {missing_count} missing values in '{col}' using mode ({fill_value})")
        elif strategy == "constant":
            if value is None:
                value = 0 if pd.api.types.is_numeric_dtype(df[col]) else "unknown"
            df[col] = df[col].fillna(value)
            logs.append(f"Filled {missing_count} missing values in '{col}' with constant ({value})")
        elif strategy == "ffill":
            df[col] = df[col].fillna(method="ffill")
            logs.append(f"Filled {missing_count} missing values in '{col}' using forward fill")
        elif strategy == "bfill":
            df[col] = df[col].fillna(method="bfill")
            logs.append(f"Filled {missing_count} missing values in '{col}' using backward fill")
        else:
            logger.warning(f"Strategy '{strategy}' not applicable for column '{col}'")
    return df, "; ".join(logs) if logs else "No missing values filled"


def drop_rows_missing(df: pd.DataFrame, columns: List[str], params: Dict[str, Any]) -> Tuple[pd.DataFrame, str]:
    target_cols = columns if columns else df.columns.tolist()
    existing_cols = [col for col in target_cols if col in df.columns]
    initial_count = len(df)
    df = df.dropna(subset=existing_cols)
    dropped = initial_count - len(df)
    return df, f"Dropped {dropped} rows with missing values in {existing_cols}"


def remove_outliers(df: pd.DataFrame, columns: List[str], params: Dict[str, Any]) -> Tuple[pd.DataFrame, str]:
    method = params.get("method", "iqr")
    threshold = params.get("threshold", 3.0 if method == "zscore" else 1.5)
    logs = []
    initial_count = len(df)
    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue
        if method == "iqr":
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            outlier_count = outlier_mask.sum()
            df = df[~outlier_mask]
            if outlier_count > 0:
                logs.append(f"Removed {outlier_count} outliers from '{col}' using IQR method")
        elif method == "zscore":
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outlier_mask = z_scores > threshold
            outlier_count = outlier_mask.sum()
            df = df[~outlier_mask]
            if outlier_count > 0:
                logs.append(f"Removed {outlier_count} outliers from '{col}' using Z-score method")
    total_dropped = initial_count - len(df)
    if logs:
        logs.append(f"Total rows removed: {total_dropped}")
    return df, "; ".join(logs) if logs else "No outliers removed"


def encode_categorical(df: pd.DataFrame, columns: List[str], params: Dict[str, Any]) -> Tuple[pd.DataFrame, str]:
    method = params.get("method", "one_hot")
    logs = []
    for col in columns:
        if col not in df.columns:
            continue
        if not pd.api.types.is_object_dtype(df[col]) and not pd.api.types.is_categorical_dtype(df[col]):
            continue
        if method == "one_hot":
            dummies = pd.get_dummies(df[col], prefix=col, prefix_sep="_", dummy_na=False)
            df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
            logs.append(f"One-hot encoded '{col}' into {len(dummies.columns)} columns")
        elif method == "label":
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            logs.append(f"Label encoded '{col}'")
        elif method == "ordinal":
            le = LabelEncoder()
            unique_vals = sorted(df[col].dropna().unique())
            le.fit(unique_vals)
            df[col] = le.transform(df[col].astype(str))
            logs.append(f"Ordinal encoded '{col}'")
    return df, "; ".join(logs) if logs else "No categorical encoding applied"


def scale_numeric(df: pd.DataFrame, columns: List[str], params: Dict[str, Any]) -> Tuple[pd.DataFrame, str]:
    method = params.get("method", "standard")
    logs = []
    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue
        if method == "standard":
            scaler = StandardScaler()
            df[col] = scaler.fit_transform(df[[col]])
            logs.append(f"Standard scaled '{col}'")
        elif method == "minmax":
            scaler = MinMaxScaler()
            df[col] = scaler.fit_transform(df[[col]])
            logs.append(f"Min-Max scaled '{col}'")
        elif method == "robust":
            scaler = RobustScaler()
            df[col] = scaler.fit_transform(df[[col]])
            logs.append(f"Robust scaled '{col}'")
    return df, "; ".join(logs) if logs else "No scaling applied"


def convert_dtype(df: pd.DataFrame, columns: List[str], params: Dict[str, Any]) -> Tuple[pd.DataFrame, str]:
    target_type = params.get("target_type", "str")
    logs = []
    for col in columns:
        if col not in df.columns:
            continue
        try:
            if target_type == "int":
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            elif target_type == "float":
                df[col] = pd.to_numeric(df[col], errors="coerce")
            elif target_type == "str":
                df[col] = df[col].astype(str)
            elif target_type == "category":
                df[col] = df[col].astype("category")
            elif target_type == "bool":
                df[col] = df[col].astype(bool)
            logs.append(f"Converted '{col}' to {target_type}")
        except Exception as e:
            logger.warning(f"Failed to convert '{col}' to {target_type}: {e}")
            logs.append(f"Failed to convert '{col}' to {target_type}: {str(e)}")
    return df, "; ".join(logs) if logs else "No type conversions applied"


def rename_column(df: pd.DataFrame, columns: List[str], params: Dict[str, Any]) -> Tuple[pd.DataFrame, str]:
    new_name = params.get("new_name")
    if not new_name or len(columns) != 1:
        return df, "Invalid rename operation: need exactly one column and 'new_name' parameter"
    old_col = columns[0]
    if old_col not in df.columns:
        return df, f"Column '{old_col}' not found"
    df = df.rename(columns={old_col: new_name})
    return df, f"Renamed '{old_col}' to '{new_name}'"


def parse_datetime(df: pd.DataFrame, columns: List[str], params: Dict[str, Any]) -> Tuple[pd.DataFrame, str]:
    logs = []
    for col in columns:
        if col not in df.columns:
            continue
        try:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            logs.append(f"Parsed '{col}' as datetime")
        except Exception as e:
            logger.warning(f"Failed to parse '{col}' as datetime: {e}")
            logs.append(f"Failed to parse '{col}' as datetime: {str(e)}")
    return df, "; ".join(logs) if logs else "No datetime parsing applied"


PREPROCESSING_DISPATCH = {"drop_column": drop_column, "drop_duplicate_rows": drop_duplicate_rows, "fill_missing": fill_missing, "drop_rows_missing": drop_rows_missing, "remove_outliers": remove_outliers, "encode_categorical": encode_categorical, "scale_numeric": scale_numeric, "convert_dtype": convert_dtype, "rename_column": rename_column, "parse_datetime": parse_datetime}


def apply_preprocessing_plan(df: pd.DataFrame, plan: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, List[str]]:
    cleaning_log = []
    for step in plan:
        op = step.get("op")
        columns = step.get("columns", [])
        params = step.get("params", {})
        if op not in PREPROCESSING_DISPATCH:
            error_msg = f"Unknown operation: {op}"
            logger.error(error_msg)
            cleaning_log.append(error_msg)
            continue
        try:
            func = PREPROCESSING_DISPATCH[op]
            df, log = func(df, columns, params)
            cleaning_log.append(log)
        except Exception as e:
            error_msg = f"Error applying {op} on {columns}: {str(e)}"
            logger.error(error_msg)
            cleaning_log.append(error_msg)
    return df, cleaning_log
