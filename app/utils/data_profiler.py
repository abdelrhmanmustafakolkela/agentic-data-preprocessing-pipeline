import pandas as pd
import numpy as np
from typing import Dict, Any


def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    profile = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_percentages": {},
        "describe": {},
        "nunique": {},
        "duplicate_rows": int(df.duplicated().sum()),
        "sample_rows": [],
    }
    for col in df.columns:
        missing_pct = (df[col].isna().sum() / len(df)) * 100
        profile["missing_percentages"][col] = round(missing_pct, 2)
    try:
        desc = df.describe(include="all")
        profile["describe"] = desc.to_dict()
    except Exception:
        numeric_desc = df.describe().to_dict()
        profile["describe"] = numeric_desc
    for col in df.columns:
        profile["nunique"][col] = int(df[col].nunique())
    sample_df = df.head(5)
    for _, row in sample_df.iterrows():
        row_dict = {}
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                row_dict[col] = None
            elif isinstance(val, (str, bytes)):
                if len(str(val)) > 100:
                    row_dict[col] = str(val)[:100] + "..."
                else:
                    row_dict[col] = str(val)
            else:
                row_dict[col] = val
        profile["sample_rows"].append(row_dict)
    return profile


def compute_correlations(df: pd.DataFrame) -> Dict[str, Any]:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        return None
    corr_matrix = df[numeric_cols].corr()
    return corr_matrix.to_dict()
