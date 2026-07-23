from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any


class DataQualityNote(BaseModel):
    column: str
    issue: str
    severity: Literal["low", "medium", "high"]


class ProfileSummary(BaseModel):
    dataset_description: str
    target_column_guess: Optional[str] = None
    notes: List[DataQualityNote] = []


class PreprocessingOp(BaseModel):
    op: Literal["drop_column", "drop_duplicate_rows", "fill_missing", "drop_rows_missing", "remove_outliers", "encode_categorical", "scale_numeric", "convert_dtype", "rename_column", "parse_datetime"]
    columns: List[str]
    params: Dict[str, Any] = Field(default_factory=dict)
    reason: str


class PreprocessingPlan(BaseModel):
    steps: List[PreprocessingOp]


class ChartSpec(BaseModel):
    chart_type: Literal["histogram", "bar", "line", "scatter", "box", "correlation_heatmap", "pie", "count_plot"]
    title: str
    x: Optional[str] = None
    y: Optional[str] = None
    hue: Optional[str] = None
    agg: Optional[Literal["sum", "mean", "count", "median"]] = None
    columns: Optional[List[str]] = None
    reason: str


class ChartPlan(BaseModel):
    charts: List[ChartSpec]
