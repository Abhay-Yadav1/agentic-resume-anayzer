from langgraph.graph import StateGraph, END # type: ignore
from state import ResumeState
from resume_nodes import LLMResumeNodes # type: ignore
import json

from datetime import date
import os
def build_resume_workflow():
    # Create graph
    graph = StateGraph(ResumeState)
    nodes = LLMResumeNodes()
    
    # Add nodes - LangGraph automatically merges partial updates
    graph.add_node("detect_file_type", nodes.file_type_detector)
    graph.add_node("extract_text", nodes.text_extractor)
    graph.add_node("llm_analysis", nodes.llm_analyzer)
    graph.add_node("skill_enhancer", nodes.skill_enhancer)
    graph.add_node("handle_errors", nodes.error_handler)
    graph.add_node("fallback_parser", nodes.fallback_parser)
    
    # Define workflow
    graph.set_entry_point("detect_file_type")
    
    # Normal flow
    graph.add_edge("detect_file_type", "extract_text")
    graph.add_edge("extract_text", "llm_analysis")
    graph.add_edge("llm_analysis", "skill_enhancer")
    graph.add_edge("skill_enhancer", END)
    
    # Error handling flow
    def should_handle_errors(state: ResumeState) -> str:
        return "handle_errors" if state.get("errors") else "continue"
    
    def route_errors(state: ResumeState) -> str:
        if state.get("errors"):
            if "LLM analysis failed" in str(state["errors"]):
                return "fallback_parser"
            return "handle_errors"
        return "continue"
    
    # Error handling for file detection and text extraction
    graph.add_conditional_edges(
        "detect_file_type",
        should_handle_errors,
        {
            "handle_errors": "handle_errors",
            "continue": "extract_text"
        }
    )
    
    graph.add_conditional_edges(
        "extract_text",
        should_handle_errors,
        {
            "handle_errors": "handle_errors", 
            "continue": "llm_analysis"
        }
    )
    
    # Special error handling for LLM analysis that can fallback to basic parsing
    graph.add_conditional_edges(
        "llm_analysis",
        route_errors,
        {
            "fallback_parser": "fallback_parser",
            "handle_errors": "handle_errors",
            "continue": "skill_enhancer"
        }
    )
    
    # Error handling for skill enhancer
    graph.add_conditional_edges(
        "skill_enhancer",
        should_handle_errors,
        {
            "handle_errors": "handle_errors",
            "continue": END
        }
    )
    
    # Route from error handler to fallback if needed, otherwise end
    graph.add_conditional_edges(
        "handle_errors",
        lambda state: "fallback_parser" if "LLM" in str(state.get("errors", [])) else END
    )
    
    # Fallback parser goes to end
    graph.add_edge("fallback_parser", END)
    
    workflow = graph.compile()
    return workflow



def test_with_real_pdf():
    # Use an existing PDF file
    pdf_file_path = "D:\\Downloads\\kritika kapoor CV.pdf"
    
    if not os.path.exists(pdf_file_path):
        print(f"❌ PDF file not found: {pdf_file_path}")
        return
    
    workflow = build_resume_workflow()
    
    initial_state: ResumeState = {
        "file_path": pdf_file_path,
        "file_type": "",
        "raw_text": "",
        "name":"",
        "address": "",
        "email":"",
        "phone":"",
        "Date":date.today().strftime("%Y-%m-%d"),
        "extracted_skills": [],
        "experience_level": "",
        "education": [],
        "years_experience": 0,
        "job_titles": [],
        "industries": [],
        "categorized_skills": {},
        "missing_skills": [],
        "primary_role": "",
        "skill_gap_analysis": "",
        "current_step": "start",
        "errors": [],
        "is_complete": False,
        "fallback_used": False,
        "enhancement_failed": False
    }
    
    try:
        final_state = workflow.invoke(initial_state)
        
        # Create JSON output
        resume_json = {
            "name": final_state.get("name", ""),
            "address": final_state.get("address", ""),
            "email": final_state.get("email", ""),
            "phone": final_state.get("phone", ""),
            "Date": final_state.get("Date", ""),
            "extracted_skills": final_state.get("extracted_skills", []),
            "experience_level": final_state.get("experience_level", ""),
            "education": final_state.get("education", []),
            "years_experience": final_state.get("years_experience", 0),
            "job_titles": final_state.get("job_titles", []),
            "industries": final_state.get("industries", []),
            "categorized_skills": final_state.get("categorized_skills", {}),
            "missing_skills": final_state.get("missing_skills", []),
            "primary_role": final_state.get("primary_role", ""),
            "skill_gap_analysis": final_state.get("skill_gap_analysis", ""),
            "is_complete": final_state.get("is_complete", False),
            "fallback_used": final_state.get("fallback_used", False),
            "errors": final_state.get("errors", [])
        }
        
        
        return json.dumps(resume_json, indent=2)
        
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")

