import streamlit as st
import os
import uuid
from resume_workflow import build_resume_workflow
from state import ResumeState

# Page config
st.set_page_config(
    page_title="Resume Upload",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Upload Your Resume")

# File upload
uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])

if uploaded_file is not None:
    # Save the uploaded file temporarily
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(uploaded_file.name)[1]
    file_path = f"uploads/{file_id}{file_extension}"
    
    # Create uploads directory if not exists
    os.makedirs("uploads", exist_ok=True)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    st.info(f"📁 File saved at: {file_path}")
    
    # Process button
    if st.button("Process Resume"):
        with st.spinner("Processing your resume..."):
            try:
                # Initialize your workflow
                workflow = build_resume_workflow()
                
                # Set up the state with the uploaded file path
                initial_state: ResumeState = {
                    "file_path": file_path,  # This sends the uploaded file to your workflow
                    "file_type": "",
                    "raw_text": "",
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
                
                # Run your existing workflow - it will use the file_path we provided
                final_state = workflow.invoke(initial_state)
                
                # Display results
                st.subheader("📊 Analysis Results")
                st.json(final_state)
                
                # Clean up the temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)
                    st.info("🗑️ Temporary file cleaned up")
                    
            except Exception as e:
                st.error(f"Error processing file: {e}")
                # Clean up on error too
                if os.path.exists(file_path):
                    os.remove(file_path)