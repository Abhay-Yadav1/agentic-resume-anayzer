from typing import TypedDict, List, Dict, Any
from langgraph.graph.message import add_messages

class JobState(TypedDict):
    # Input from Phase 2
    resume_data: Dict[str, Any]
    
    # Job Search
    job_queries: List[str]
    job_listings: List[Dict[str, Any]]
    filtered_jobs: List[Dict[str, Any]]
    
    # Matching Results
    matched_jobs: List[Dict[str, Any]]
    match_scores: Dict[str, float]
    top_recommendations: List[Dict[str, Any]]
    
    # System State
    current_step: str
    errors: List[str]
    is_complete: bool