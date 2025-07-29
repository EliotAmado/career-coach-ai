from pydantic import BaseModel
from tools import fetch_news_articles, fetch_job_outlook, get_reddit_posts, generate_related_subreddits, scrape_coursera_courses, fetch_top_skills, fetch_recommended_majors
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse  #I dont think we need this, but lets keep it for now
from chains import summarize_career
import json

app = FastAPI(
    title="Career Coach AI",
    description="An AI-powered career coach that provides personalized career insights based on job trends, Reddit opinions, news articles, and course suggestions.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development; restrict in production
    allow_credentials=True, # Allow credentials for cookies, authorization headers, etc.
    allow_methods=["*"], # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers (Content-Type, Authorization, etc.)
)

@app.post("/chat", description="Generate a detailed career profile based on user input.")
def chat(career: str = Query(..., description="The career to analyze")):
    job_outlook_text = "Job outlook not available."
    news_text = "No recent news found."
    reddit_text = "Reddit insights unavailable."
    courses_text = "No relevant courses found."
    skills_text = "Skills data not available."
    skills_sources = ""
    majors_text = "Major recommendations not available."
    majors_sources = ""

    try:
        job_outlook = fetch_job_outlook(career)
        if "error" not in job_outlook:
            job_outlook_text = "\n".join([
                f"🔹 {r['title']}\n{r.get('link', '')}" for r in job_outlook.get("results", [])
            ])
        else:
            print(f"Job outlook error: {job_outlook['error']}")
    except Exception as e:
        print(f"Error fetching job outlook: {e}")

    try:
        news = fetch_news_articles(career)
        if isinstance(news, list) and not any("error" in item for item in news):
            news_text = "\n".join([
                f"📰 {a['title']} ({a['source']})\n{a['url']}" for a in news
            ])
        else:
            print(f"News error: {news}")
    except Exception as e:
        print(f"Error fetching news articles: {e}")

    try:
        reddit = get_reddit_posts(career)
        if "error" not in reddit:
            reddit_text = "\n".join([
                f"**{p['title']}** ({p['subreddit']})\n{p['url']}" for p in reddit.get("results", [])
            ])
        else:
            print(f"Reddit error: {reddit['error']}")
    except Exception as e:
        print(f"Error fetching Reddit posts: {e}")

    try:
        courses = scrape_coursera_courses(career)
        if isinstance(courses, list):
            courses_text = "\n".join([
                f"- {c['title']}\n  {c['url']}" for c in courses
            ])
        else:
            print(f"Coursera error: {courses}")
    except Exception as e:
        print(f"Error scraping Coursera: {e}")

    #added fetching top skills and recommended majors
    try:
        skills = fetch_top_skills(career)
        if "error" not in skills:
            skills_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(skills["skills"], start=1)])
            skills_sources = "\n".join([f"- {src}" for src in skills["sources"]])
        else:
            print(f"Skills error: {skills['error']}")
    except Exception as e:
        print(f"Error fetching skills: {e}")

    try:
        majors = fetch_recommended_majors(career)
        if "error" not in majors:
            majors_text = "\n".join([f"- {m}" for m in majors["majors"]])
            majors_sources = "\n".join([f"- {src}" for src in majors["sources"]])
        else:
            print(f"Majors error: {majors['error']}")
    except Exception as e:
        print(f"Error fetching majors: {e}")


    try:
        summary = summarize_career(
            career=career,
            job_outlook=job_outlook_text,
            news_articles=news_text,
            reddit_posts=reddit_text,
            courses=courses_text,
            skills=skills_text,
            skills_sources=skills_sources,
            majors=majors_text,
            majors_sources=majors_sources
        )
        return JSONResponse(content={"summary": summary})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"LLM error: {str(e)}"})
    


@app.get("/", description="Health check endpoint to verify the API is running.")
def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: A simple message indicating the API is running.
    """
    return {"message": "Career Coach AI API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)