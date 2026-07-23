from typing import TypedDict, List, Dict, Any, Optional


class PipelineState(TypedDict):
    file_path: str
    original_filename: str
    data_profile: Dict[str, Any]
    profile_summary_text: str
    preprocessing_plan: List[Dict]
    cleaned_file_path: str
    cleaning_log: List[str]
    post_clean_profile: Dict[str, Any]
    chart_plan: List[Dict]
    charts: List[Dict]
    errors: List[str]
    status: str
