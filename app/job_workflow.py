from langgraph.graph import StateGraph, END
from job_states import JobState
from job_nodes import JobSearchNodes

def build_job_workflow():
    graph = StateGraph(JobState)
    nodes = JobSearchNodes()
    
    # Add nodes
    graph.add_node("generate_queries", nodes.generate_job_queries)
    graph.add_node("search_jobs", nodes.search_jsearch_api)
    graph.add_node("filter_jobs", nodes.filter_and_match_jobs)
    graph.add_node("generate_recommendations", nodes.generate_recommendations)
    
    # Define workflow
    graph.set_entry_point("generate_queries")
    graph.add_edge("generate_queries", "search_jobs")
    graph.add_edge("search_jobs", "filter_jobs")
    graph.add_edge("filter_jobs", "generate_recommendations")
    graph.add_edge("generate_recommendations", END)
    
    return graph.compile()