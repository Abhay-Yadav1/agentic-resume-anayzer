# streamlit_app.py
import streamlit as st
import json
import os
import tempfile
from job_workflow import build_job_workflow
from job_states import JobState
from cover_letter import give_cover_letter_workflow
from resume_workflow import test_with_real_pdf, build_resume_workflow
from state import ResumeState
from datetime import date

# Page configuration
st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2e86ab;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .job-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    .match-score {
        font-weight: bold;
        color: #28a745;
    }
</style>
""", unsafe_allow_html=True)

def process_uploaded_resume(uploaded_file):
    """Process the uploaded resume file and return resume data"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        # Process the resume
        workflow = build_resume_workflow()
        
        initial_state: ResumeState = {
            "file_path": temp_path,
            "file_type": "",
            "raw_text": "",
            "name": "",
            "address": "",
            "email": "",
            "phone": "",
            "Date": date.today().strftime("%Y-%m-%d"),
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
        
        final_state = workflow.invoke(initial_state)
        
        # Create resume JSON
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
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return resume_json
        
    except Exception as e:
        st.error(f"Error processing resume: {str(e)}")
        return None

def find_job_recommendations(resume_data):
    """Find job recommendations based on resume data"""
    try:
        workflow = build_job_workflow()
        
        initial_state: JobState = {
            "resume_data": resume_data,
            "job_queries": [],
            "job_listings": [],
            "filtered_jobs": [],
            "matched_jobs": [],
            "match_scores": {},
            "top_recommendations": [],
            "current_step": "start",
            "errors": [],
            "is_complete": False
        }
        
        final_state = workflow.invoke(initial_state)
        return final_state["top_recommendations"]
        
    except Exception as e:
        st.error(f"Error finding job recommendations: {str(e)}")
        return []

def generate_cover_letter_streamlit(resume_data):
    """Generate cover letter based on resume data"""
    try:
        # We need to modify the cover_letter module to accept resume data
        # For now, we'll use the existing function
        cover_letter = give_cover_letter_workflow()
        return cover_letter
    except Exception as e:
        st.error(f"Error generating cover letter: {str(e)}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">💼 AI Career Assistant</h1>', unsafe_allow_html=True)
    st.markdown("### Upload your resume and get AI-powered job recommendations and cover letters!")
    
    # Initialize session state
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = None
    if 'job_recommendations' not in st.session_state:
        st.session_state.job_recommendations = None
    if 'cover_letter' not in st.session_state:
        st.session_state.cover_letter = None
    
    # Sidebar
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="sub-header">📄 Upload Your Resume</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file", 
            type="pdf",
            help="Upload your resume in PDF format"
        )
        
        if uploaded_file is not None:
            with st.spinner("Analyzing your resume..."):
                resume_data = process_uploaded_resume(uploaded_file)
                
                if resume_data:
                    st.session_state.resume_data = resume_data
                    st.success("✅ Resume processed successfully!")
                    
                    # Display resume summary
                    with st.expander("📊 Resume Summary", expanded=True):
                        st.write(f"**Name:** {resume_data.get('name', 'N/A')}")
                        st.write(f"**Primary Role:** {resume_data.get('primary_role', 'N/A')}")
                        st.write(f"**Experience Level:** {resume_data.get('experience_level', 'N/A')}")
                        st.write(f"**Skills:** {', '.join(resume_data.get('extracted_skills', [])[:10])}")
                        if len(resume_data.get('extracted_skills', [])) > 15:
                            st.write(f"*... and {len(resume_data.get('extracted_skills', [])) - 15} more skills*")
    
    with col2:
        st.markdown('<div class="sub-header">🚀 Career Tools</div>', unsafe_allow_html=True)
        
        if st.session_state.resume_data:
            # Job Recommendations Section
            st.markdown("### 🔍 Find Job Recommendations")
            if st.button("Find Matching Jobs", use_container_width=True):
                with st.spinner("Searching for the best job matches..."):
                    job_recommendations = find_job_recommendations(st.session_state.resume_data)
                    st.session_state.job_recommendations = job_recommendations
            
            # Cover Letter Section
            st.markdown("### 📝 Generate Cover Letter")
            if st.button("Generate Cover Letter", use_container_width=True):
                with st.spinner("Creating your personalized cover letter..."):
                    cover_letter = generate_cover_letter_streamlit(st.session_state.resume_data)
                    st.session_state.cover_letter = cover_letter
        else:
            st.info("👆 Please upload your resume first to access career tools")
    
    # Display Results
    st.markdown("---")
    
    # Job Recommendations Results
    if st.session_state.job_recommendations:
        st.markdown('<div class="sub-header">🎯 Job Recommendations</div>', unsafe_allow_html=True)
        st.write(f"Found **{len(st.session_state.job_recommendations)}** matching jobs")
        
        for i, job in enumerate(st.session_state.job_recommendations[:10], 1):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{i}. {job['title']}**")
                    st.write(f"🏢 **Company:** {job['company']}")
                    st.write(f"📍 **Location:** {job['location']}")
                    st.write(f"📊 **Match Score:** <span class='match-score'>{job['match_score']*100:.0f}%</span>", unsafe_allow_html=True)
                    st.write(f"💡 **Why it matches:** {job['explanation']}")
                
                with col2:
                    st.link_button("Apply Now", job['url'])
                
                st.markdown("---")
    
    # Cover Letter Results
    if st.session_state.cover_letter:
        st.markdown('<div class="sub-header">📄 Generated Cover Letter</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.text_area("Cover Letter", st.session_state.cover_letter, height=300)
        
        with col2:
            st.download_button(
                label="📥 Download Cover Letter",
                data=st.session_state.cover_letter,
                file_name="cover_letter.txt",
                mime="text/plain"
            )
        
        st.markdown("---")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Built with ❤️ using Streamlit, LangGraph, and Groq AI"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":

    main()

