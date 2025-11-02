from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from state import CoverLetterState
from langgraph.graph import StateGraph, END ,START
import os
from  resume_workflow import test_with_real_pdf
# Load environment variables
load_dotenv()

# Get Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")
jsonfile=test_with_real_pdf()
# Initialize Groq chat model
llm= ChatGroq(
    model_name="llama-3.1-8b-instant",
    api_key=groq_api_key
)



def generate_cover_letter(state: CoverLetterState):
    """Node 1: Generate cover letter from JSON CV data"""
    
    
    prompt = f"""
    Generate a cover letter based on this Json data . Also fill all the placeholders like Job Title, Your Name, Your Address,Email Address, Phone Number, Date etc. with appropriate values that are in JSON file:
    {jsonfile}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"cover_letter": response.content}

def enhance_cover_letter(state: CoverLetterState):
    """Node 2: Enhance the generated cover letter"""
    cover_letter = state["cover_letter"]
    
    prompt = f"""
    Enhance this cover letter to make it more professional and impactful and in 100 words :
    {cover_letter}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"enhanced_cover_letter": response.content}

def build_cover_letter_workflow():
    graph=StateGraph(CoverLetterState)
    graph.add_node("generate_cover_letter", generate_cover_letter)
    graph.add_node("enhance_cover_letter", enhance_cover_letter)
    graph.add_edge(START, "generate_cover_letter")
    graph.add_edge("generate_cover_letter", "enhance_cover_letter")
    graph.add_edge("enhance_cover_letter", END)
    workflow=graph.compile()
    return workflow


def give_cover_letter_workflow():
    workflow=build_cover_letter_workflow()
    initial_state:CoverLetterState={
        "cover_letter": "",
        "enhanced_cover_letter": ""
    }
    try:
        final_state=workflow.invoke(initial_state)
       
        return final_state["enhanced_cover_letter"]
    except Exception as e:
        print(f"❌ Workflow failed: {e}")


if __name__=="__main__":
    cover_letter=give_cover_letter_workflow()
    print("📄 Generated Cover Letter:")
    print("="*60)
    print(cover_letter)        