import os
import requests
import json
from typing import Dict, Any, List
from job_states import JobState
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

class JobSearchNodes:
    def __init__(self):
        GROQ_API_KEY = "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"
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=GROQ_API_KEY
        )
        self.jsearch_api_key = "bad496d39bmsh6431b54cfc3a7b4p137541jsn2ec44d039f51"  # Get from RapidAPI
    
    def generate_job_queries(self, state: JobState) -> Dict[str, Any]:
        """Generate search queries based on resume data"""
        print("📝 Generating job search queries...")
        
        resume_data = state["resume_data"]
        skills = resume_data.get("extracted_skills", [])
        experience = resume_data.get("experience_level", "")
        primary_role = resume_data.get("primary_role", "")
        job_titles = resume_data.get("job_titles", [])
        
        prompt = f"""
        Based on this resume data, generate 3 specific job search queries for job search APIs:
        
        Technical Skills: {skills[:10]}  # First 10 skills
        Experience Level: {experience}
        Previous Job Titles: {job_titles}
        Primary Role: {primary_role}
        
        Create specific search queries that would find relevant jobs on LinkedIn/Indeed.
        Return JSON: {{"queries": ["query1", "query2", "query3"]}}
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Clean JSON response
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            queries_data = json.loads(content)
            return {
                "job_queries": queries_data.get("queries", []),
                "current_step": "search_jobs"
            }
        except Exception as e:
            return {
                "errors": [f"Query generation failed: {str(e)}"],
                "current_step": "error"
            }
    
    def search_jsearch_api(self, state: JobState) -> Dict[str, Any]:
        """Search jobs using JSearch API (free tier)"""
        queries = state["job_queries"]
        all_jobs = []
        
        for query in queries[:2]:  # Limit to 2 queries to stay within free tier
            try:
                jobs = self._call_jsearch_api(query)
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"JSearch API error for query '{query}': {e}")
                continue
        
        # If JSearch fails, use mock data as fallback
        if not all_jobs:
            print("Using mock data as fallback")
            all_jobs = self._get_mock_job_listings(queries)
        
        return {
            "job_listings": all_jobs,
            "current_step": "filter_jobs"
        }
    
    def _call_jsearch_api(self, query: str) -> List[Dict[str, Any]]:
        """Call JSearch API from RapidAPI"""
        url = "https://jsearch.p.rapidapi.com/search?query=developer%20jobs%20in%20chicago&page=1&num_pages=1&country=us&date_posted=all"
        
        querystring = {
            "query": f"{query} India",  # Focus on India jobs
            "page": "1",
            "num_pages": "1"
        }
        
        headers = {
            "X-RapidAPI-Key": "bad496d39bmsh6431b54cfc3a7b4p137541jsn2ec44d039f51",  # Get from https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job_data in data.get("data", [])[:10]:  # Limit to 10 jobs per query
                job = {
                    "title": job_data.get("job_title", ""),
                    "company": job_data.get("employer_name", ""),
                    "location": job_data.get("job_city", "") + ", " + job_data.get("job_country", ""),
                    "type": job_data.get("job_employment_type", ""),
                    "description": job_data.get("job_description", ""),
                    "skills": self._extract_skills_from_description(job_data.get("job_description", "")),
                    "experience_level": self._infer_experience_level(job_data.get("job_title", ""), job_data.get("job_description", "")),
                    "salary": job_data.get("job_salary", ""),
                    "url": job_data.get("job_apply_link", ""),
                    "posted_date": job_data.get("job_posted_at_datetime_utc", ""),
                    "source": "JSearch API"
                }
                jobs.append(job)
            
            return jobs
        else:
            raise Exception(f"JSearch API error: {response.status_code}")
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skills from job description using LLM"""
        if not description:
            return []
        
        # Truncate long descriptions
        if len(description) > 2000:
            description = description[:2000] + "..."
        
        prompt = f"""
        Extract technical skills and technologies from this job description.
        Return ONLY a JSON list of skills: ["skill1", "skill2", ...]
        
        Job Description:
        {description}
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            skills_data = json.loads(response.content)
            return skills_data if isinstance(skills_data, list) else []
        except:
            # Fallback: basic keyword matching
            common_skills = ["python", "java", "javascript", "react", "node.js", "sql", "mongodb", 
                           "aws", "docker", "kubernetes", "machine learning", "ai", "fastapi"]
            description_lower = description.lower()
            return [skill for skill in common_skills if skill in description_lower]
    
    def _infer_experience_level(self, title: str, description: str) -> str:
        """Infer experience level from job title and description"""
        text = (title + " " + description).lower()
        
        if any(word in text for word in ["senior", "lead", "principal", "manager", "5+ years", "8+ years"]):
            return "senior"
        elif any(word in text for word in ["mid-level", "mid level", "3+ years", "4+ years"]):
            return "mid"
        elif any(word in text for word in ["junior", "entry", "fresher", "0-2 years", "intern"]):
            return "junior"
        else:
            return "mid"  # Default
    
    def _get_mock_job_listings(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Fallback mock data"""
        return [
            {
                "title": "Python Developer",
                "company": "Tech Solutions Inc.",
                "location": "Remote",
                "type": "Full-time",
                "description": "Looking for Python developer with FastAPI experience.",
                "skills": ["python", "fastapi", "aws", "docker"],
                "experience_level": "mid",
                "salary": "₹8L - ₹12L",
                "url": "https://linkedin.com/jobs/view/123",
                "source": "Mock Data"
            },
            {
                "title": "Full Stack Developer", 
                "company": "Startup XYZ",
                "location": "Bangalore, India",
                "type": "Full-time",
                "description": "React and Node.js developer needed.",
                "skills": ["javascript", "react", "node.js", "python"],
                "experience_level": "mid", 
                "salary": "₹10L - ₹15L",
                "url": "https://linkedin.com/jobs/view/124",
                "source": "Mock Data"
            }
        ]
    
    def filter_and_match_jobs(self, state: JobState) -> Dict[str, Any]:
        """Match jobs with resume skills"""
        resume_data = state["resume_data"]
        job_listings = state["job_listings"]
        
        resume_skills = set([s.lower() for s in resume_data.get("extracted_skills", [])])
        resume_experience = resume_data.get("experience_level", "").lower()
        
        matched_jobs = []
        match_scores = {}
        
        for job in job_listings:
            score = self._calculate_match_score(job, resume_skills, resume_experience)
            if score > 0.2:  # Lower threshold for real data
                job["match_score"] = score
                matched_jobs.append(job)
                match_scores[job["title"]] = score
        
        # Sort by match score
        matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "matched_jobs": matched_jobs,
            "match_scores": match_scores,
            "current_step": "generate_recommendations"
        }
    
    def _calculate_match_score(self, job: Dict, resume_skills: set, resume_experience: str) -> float:
        """Calculate job-resume match score"""
        job_skills = set([s.lower() for s in job.get("skills", [])])
        job_experience = job.get("experience_level", "").lower()
        
        # Skill matching (70% weight)
        if job_skills:
            skill_intersection = resume_skills.intersection(job_skills)
            skill_score = len(skill_intersection) / len(job_skills)
        else:
            skill_score = 0
        
        # Experience matching (30% weight)
        exp_levels = {"intern": 0, "junior": 1, "mid": 2, "senior": 3}
        resume_exp = exp_levels.get(resume_experience, 1)
        job_exp = exp_levels.get(job_experience, 2)  # Default to mid
        
        if resume_exp >= job_exp:
            exp_score = 1.0
        else:
            exp_score = max(0, 1 - (job_exp - resume_exp) * 0.3)
        
        total_score = (skill_score * 0.7) + (exp_score * 0.3)
        return round(total_score, 2)
    
    def generate_recommendations(self, state: JobState) -> Dict[str, Any]:
        """Generate final recommendations with explanations"""
        matched_jobs = state["matched_jobs"][:8]  # Top 8 matches
        resume_data = state["resume_data"]
        
        recommendations = []
        
        for job in matched_jobs:
            explanation = self._generate_job_explanation(job, resume_data)
            recommendations.append({
                **job,
                "explanation": explanation
            })
        
        return {
            "top_recommendations": recommendations,
            "current_step": "complete", 
            "is_complete": True
        }
    
    def _generate_job_explanation(self, job: Dict, resume_data: Dict) -> str:
        """Generate why this job is a good match"""
        resume_skills = set([s.lower() for s in resume_data.get("extracted_skills", [])])
        job_skills = set([s.lower() for s in job.get("skills", [])])
        
        matching_skills = resume_skills.intersection(job_skills)
        missing_skills = job_skills - resume_skills
        
        match_percentage = int(job.get("match_score", 0) * 100)
        
        explanation = f"{match_percentage}% match! "
        
        if matching_skills:
            explanation += f"You have {len(matching_skills)} required skills including {', '.join(list(matching_skills)[:3])}. "
        
        if missing_skills:
            explanation += f"Consider learning {', '.join(list(missing_skills)[:2])}."
        
        return explanation