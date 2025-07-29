from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(model="gpt-4", temperature=0.4, max_tokens=1200)

prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are Career Coach AI — an expert assistant that gives personalized career insights based on multiple sources.

Use job trend data, Reddit opinions, news articles, and course suggestions to build a useful and realistic career summary.
"""
    ),
    (
        "user",
        """Generate a detailed yet readable career profile for: **{career}**

Format it as follows in **markdown**:

---

## 💼 Career Overview
Brief 2-3 sentence intro about what this career involves.

---

## 📈 Job Outlook
Summarize demand, salary, and trends. Use bullets:
{job_outlook}

---

## 📚 Courses to Get Started
List top courses to learn this field:
{courses}

---

## 🎓 Recommended Majors for College Students
List the most relevant college majors (and closely related fields) that prepare someone for this career:
{majors}

**Sources:**
{majors_sources}

---

## 🛠️ Top 10 Skills Companies Look For
List the top 10 most in-demand technical and soft skills for this role:
{skills}

**Sources:**
{skills_sources}

---

## 📰 Recent Industry News
Show 2-3 bullet points or blurbs:
{news_articles}

---

## 💬 Reddit Insights
Include up to 3 community insights (one specifically on the current job market of that career) with sentiment:
{reddit_posts}

---

## ✅ Final Verdict
Who is this career good for? What are smart next steps? Be clear and practical.

Format with headers, bullets, and links as needed. Be concise, helpful, and positive."""
    )
])


def summarize_career(career: str, job_outlook: str, courses: str, majors: str, majors_sources: str, skills: str, skills_sources: str, news_articles: str, reddit_posts: str) -> str:
    prompt = prompt_template.format_messages(
        career=career,
        job_outlook=job_outlook,
        courses=courses,
        majors=majors,
        majors_sources=majors_sources,
        skills=skills,
        skills_sources=skills_sources,
        news_articles=news_articles,
        reddit_posts=reddit_posts
    )
    response = llm.invoke(prompt)
    return response.content

#we did not use pydanticparser because we are not using the API, but rather the LLM directly (look at notes)