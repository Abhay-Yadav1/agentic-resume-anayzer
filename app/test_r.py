# test_r.py
import json
from job_workflow import build_job_workflow
from job_states import JobState

def main():
    try:
        # Import the specific function that works
        from resume_workflow import test_with_real_pdf
        
        print("🔍 Calling test_with_real_pdf()...")
        resume_data_str = test_with_real_pdf()
        
        # Debug what we got
        print(f"🔍 Return type: {type(resume_data_str)}")
        
        # Parse the JSON string into a dictionary
        if isinstance(resume_data_str, str):
            print("🔄 Parsing JSON string to dictionary...")
            resume_data = json.loads(resume_data_str)
        else:
            resume_data = resume_data_str  # Already a dict (unlikely)
        
        print(f"✅ Parsed resume data type: {type(resume_data)}")
        print(f"📊 Resume keys: {list(resume_data.keys())}")
        print(f"🔧 Skills: {resume_data.get('extracted_skills', [])[:5]}...")
        print(f"🎯 Primary Role: {resume_data.get('primary_role', 'N/A')}")
        print(f"💼 Experience Level: {resume_data.get('experience_level', 'N/A')}")
        
        # Build workflow
        workflow = build_job_workflow()
        
        # Initial state
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
        
        print("🚀 Starting Real Job Search...")
        
        # Execute workflow
        final_state = workflow.invoke(initial_state)
        
        print(f"✅ Found {len(final_state['top_recommendations'])} job recommendations!")
        
       
        
        # Print top recommendations
        print("\n🎯 TOP JOB RECOMMENDATIONS:")
        print("=" * 60)
        for i, job in enumerate(final_state["top_recommendations"][:5], 1):
            print(f"\n{i}. {job['title']} at {job['company']}")
            print(f"   📍 Location: {job['location']}")
            print(f"   🎯 Match Score: {job['match_score']*100:.0f}%")
            print(f"   📝 Explanation: {job['explanation']}")
            print(f"   🔗 Apply: {job['url']}")
            print("-" * 50)
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"🔍 Problematic JSON: {resume_data_str}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()