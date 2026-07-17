import streamlit as st
from google import genai
import json
import urllib.parse
import os

# 1. Setup
# Streamlit Cloud will read GEMINI_API_KEY from your Settings -> Secrets
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="AI Career Mentor", layout="wide")

st.title("🚀 Simple Career Roadmap")
st.sidebar.title("How it works")
st.sidebar.info("Fill in the form below. We will build a 30-day learning plan for you.")

# 2. Professional Form
with st.form("profile_form"):
    st.subheader("📝 Tell us about you")
    
    col1, col2 = st.columns(2)
    with col1:
        major = st.text_input("What are you studying?", placeholder="Example: Computer Science, Mechanical")
        personality = st.selectbox("What is your style?", ["Dominant (Leader)", "Steady (Team Player)", "Influential (Creative)", "Conscientious (Detail-oriented)"])
        
    with col2:
        interest = st.text_input("What task do you enjoy?", placeholder="Example: Solving math problems, Managing people")
        time_per_day = st.slider("Hours to study per day?", 1, 5, 2)
    
    projects = st.text_area("What skills or projects have you done?", placeholder="Example: Built a calculator, know basic HTML.")
    submitted = st.form_submit_button("Create My Roadmap")

# 3. Logic
if submitted:
    with st.spinner("Building your custom plan..."):
        try:
            prompt = f"""
            Analyze this student: 
            Major: {major}, Style: {personality}, Interests: {interest}, 
            Time: {time_per_day} hours/day, Background: {projects}. 
            
            Return ONLY raw JSON with keys 'career_paths'. 
            Each path must have: 
            1. 'title' 
            2. 'reasoning' (use very simple language)
            3. 'roadmap' (a list of objects with 'topic', 'skills_covered', and 'youtube_search').
            """
            
            # Using the new Google GenAI library
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            
            raw_text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw_text)

            for path in data['career_paths']:
                with st.container(border=True):
                    st.subheader(path['title'])
                    st.write(path['reasoning'])
                    
                    st.markdown("### 🗺️ Your Step-by-Step Plan")
                    for step in path['roadmap']:
                        query = urllib.parse.quote(step['youtube_search'])
                        url = f"https://www.youtube.com/results?search_query={query}"
                        
                        with st.expander(f"Step: {step['topic']}"):
                            skills = step['skills_covered']
                            skills_display = ', '.join(skills) if isinstance(skills, list) else skills
                            st.write(f"**Skills to learn:** {skills_display}")
                            st.markdown(f"[🔗 Click here to watch free lessons]({url})")
                            
        except Exception as e:
            st.error(f"Error: {e}")
