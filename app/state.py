from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages # type: ignore


class ResumeState(TypedDict):
    # User Input
    name: Optional[str]
    file_path: str
    file_type: str
    address: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    Date:str
    # Processing Steps
    raw_text: str
    extracted_skills: List[str]
    experience_level: str
    education: List[str]
    years_experience: int
    job_titles: List[str]
    industries: List[str]
    
    # Enhanced fields
    categorized_skills: dict
    missing_skills: List[str]
    primary_role: str
    skill_gap_analysis: str
    
    # System State
    current_step: Annotated[str, add_messages]
    errors: Annotated[List[str], add_messages]
    is_complete: bool
    fallback_used: bool
    enhancement_failed: bool


class CoverLetterState(TypedDict):
    cover_letter: str
    enhanced_cover_letter: str


class RecommendationState(TypedDict):
    jobs_data: List[dict]
    job_recommendations: str    