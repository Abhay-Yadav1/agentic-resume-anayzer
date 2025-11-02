from state import ResumeState
import PyPDF2 
import docx
from typing import Dict, Any
import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage 

class LLMResumeNodes:
    
    def __init__(self):
        GROQ_API_KEY="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"
        self.client = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=GROQ_API_KEY  # Reads from .env
        )
    
    def file_type_detector(self, state: ResumeState) -> Dict[str, Any]:
        """Node 1: Detect file type"""
        file_path = state["file_path"]
        
        if file_path.endswith('.pdf'):
            return {
                "file_type": "pdf",
                "current_step": "text_extraction"
            }
        elif file_path.endswith('.docx'):
            return {
                "file_type": "docx", 
                "current_step": "text_extraction"
            }
        else:
            return {
                "errors": ["Unsupported file format"],
                "current_step": "error"
            }
    
    def text_extractor(self, state: ResumeState) -> Dict[str, Any]:
        """Node 2: Extract text from files"""
        if state["current_step"] == "error":
            return {}  # Don't change anything if in error state
            
        try:
            text = ""
            if state["file_type"] == "pdf":
                with open(state["file_path"], 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            elif state["file_type"] == "docx":
                doc = docx.Document(state["file_path"])
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
            
            return {
                "raw_text": text,
                "current_step": "llm_analysis"
            }
            
        except Exception as e:
            return {
                "errors": [f"Text extraction failed: {str(e)}"],
                "current_step": "error"
            }
    
    def llm_analyzer(self, state: ResumeState) -> Dict[str, Any]:
        """Node 3: Use LLM to extract structured information from resume"""
        if state["current_step"] == "error":
            return {}  # Don't change anything if in error state
        
        resume_text = state["raw_text"]
        
        # Truncate very long resumes to save tokens
        if len(resume_text) > 4000:
            resume_text = resume_text[:4000] + "... [truncated]"
        
        system_prompt = """You are an expert resume parser. Extract structured information from resumes and return ONLY valid JSON format.

        Return JSON with these exact fields:
        {
            "technical_skills": ["list", "of", "technical", "skills"],
            "experience_level": "junior/mid/senior/intern",
            "education": ["degree1", "degree2"],
            "years_experience": number,
            "job_titles": ["title1", "title2"],
            "name": "Full Name",
            "address": "Full Address",
            "email": "Users Email",
            "phone": "Phone Number",

            "industries": ["industry1", "industry2"]
        }"""
        
        user_prompt = f"""
        Analyze this resume and extract the structured information:
        
        RESUME TEXT:
        {resume_text}
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.client.invoke(messages)
            llm_output = response.content
            
            # Clean the response - remove markdown code blocks if present
            if "```json" in llm_output:
                llm_output = llm_output.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_output:
                llm_output = llm_output.split("```")[1].split("```")[0].strip()
            
            parsed_data = json.loads(llm_output)
            
            return {
                "name": parsed_data.get("name", ""),
                "address": parsed_data.get("address", ""),
                "email": parsed_data.get("email", ""),
                "phone": parsed_data.get("phone", ""),
                "extracted_skills": parsed_data.get("technical_skills", []),
                "experience_level": parsed_data.get("experience_level", "unknown"),
                "education": parsed_data.get("education", []),
                "years_experience": parsed_data.get("years_experience", 0),
                "job_titles": parsed_data.get("job_titles", []),
                "industries": parsed_data.get("industries", []),
                "current_step": "skill_enhancement"
            }
            
        except Exception as e:
            return {
                "errors": [f"LLM analysis failed: {str(e)}"],
                "current_step": "error"
            }
    
    def skill_enhancer(self, state: ResumeState) -> Dict[str, Any]:
        """Node 4: Use LLM to enhance skill categorization"""
        if state["current_step"] == "error":
            return {}  # Don't change anything if in error state
        
        skills = state["extracted_skills"]
        job_titles = state["job_titles"]
        
        system_prompt = """You are a career advisor and technical recruiter. Analyze skills and suggest improvements. Return ONLY valid JSON.

        Return JSON with these exact fields:
        {
            "categorized_skills": {
                "programming_languages": ["list"],
                "frameworks": ["list"], 
                "tools": ["list"],
                "cloud_technologies": ["list"],
                "databases": ["list"]
            },
            "missing_skills": ["list", "of", "relevant", "skills"],
            "primary_role": "most likely job role",
            "skill_gap_analysis": "brief analysis text"
        }"""
        
        user_prompt = f"""
        Analyze these skills and job titles:
        
        Skills: {skills}
        Job Titles: {job_titles}
        
        Categorize the skills and suggest missing relevant skills for these roles.
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.client.invoke(messages)
            llm_output = response.content
            
            # Clean the response
            if "```json" in llm_output:
                llm_output = llm_output.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_output:
                llm_output = llm_output.split("```")[1].split("```")[0].strip()
            
            enhanced_data = json.loads(llm_output)
            
            return {
                "categorized_skills": enhanced_data.get("categorized_skills", {}),
                "missing_skills": enhanced_data.get("missing_skills", []),
                "primary_role": enhanced_data.get("primary_role", ""),
                "skill_gap_analysis": enhanced_data.get("skill_gap_analysis", ""),
                "current_step": "complete",
                "is_complete": True
            }
            
        except Exception as e:
            # If enhancement fails, still mark as complete with basic data
            return {
                "current_step": "complete",
                "is_complete": True,
                "enhancement_failed": True
            }
    
    def error_handler(self, state: ResumeState) -> Dict[str, Any]:
        """Node 5: Handle errors gracefully"""
        if state.get("errors"):
            print(f"Workflow errors: {state['errors']}")
            # For LLM errors, route to fallback
            if any("LLM" in error for error in state["errors"]):
                return {"current_step": "fallback_parsing"}
        return {}
    
    def fallback_parser(self, state: ResumeState) -> Dict[str, Any]:
        """Node 6: Fallback parsing if LLM fails"""
        # Basic keyword matching as fallback
        text_lower = state["raw_text"].lower()
        
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb',
            'aws', 'docker', 'kubernetes', 'machine learning', 'ai', 'fastapi',
            'langchain', 'langgraph', 'data analysis', 'pandas', 'numpy'
        ]
        
        found_skills = [skill for skill in skill_keywords if skill in text_lower]
        
        return {
            "extracted_skills": found_skills,
            "experience_level": "unknown",
            "current_step": "complete", 
            "is_complete": True,
            "fallback_used": True
        }


    
