from bs4 import BeautifulSoup
import datetime 
import os
import httpx
import praw
import json
from urllib.parse import quote


def fetch_news_articles(career: str, num_articles: int = 5) -> list:
    """
    Fetches news articles based on the career provided using NewsAPI.
    
    Args:
        career (str): The career field to search for.
        num_articles (int): The number of articles to fetch. Default is 5.
    
    Returns:
        list: A list of dictionaries containing article titles, descriptions, and URLs.
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return {"error": "NEWS_API_KEY not found in environment variables"}
    
    # Search for recent news about the career
    query = f"{career} jobs career industry trends"
    url = f"https://newsapi.org/v2/everything"
    
    params = {
        'q': query,
        'sortBy': 'relevancy',
        'pageSize': num_articles,
        'apiKey': api_key,
        'language': 'en'
    }
    
    try:
        response = httpx.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        for article in data.get('articles', []):
            articles.append({
                'title': article.get('title', 'No title'),
                'description': article.get('description', 'No description'),
                'url': article.get('url', ''),
                'published_at': article.get('publishedAt', ''),
                'source': article.get('source', {}).get('name', 'Unknown')
            })
        
        return articles
    
    except Exception as e:
        return {"error": f"Failed to fetch news articles: {str(e)}"}


def fetch_job_outlook(career: str):
    """
    Fetches job outlook data using Serper API to search for BLS and other career outlook data.
    
    Args:
        career (str): The career field to search for.
    
    Returns:
        dict: Job outlook data including search results.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return {"error": "SERPER_API_KEY not found in environment variables"}
    
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    # Multiple search queries for comprehensive data
    queries = [
        f"{career} job outlook salary growth BLS bureau labor statistics",
        f"{career} career prospects future demand 2024 2025",
        f"{career} average salary median pay trends"
    ]
    
    all_results = []
    
    for query in queries:
        payload = {"q": query}
        
        try:
            response = httpx.post("https://google.serper.dev/search", 
                                headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("organic", [])[:2]  # Top 2 results per query
            all_results.extend(results)
            
        except Exception as e:
            continue
    
    return {
        "results": all_results[:6],  # Top 6 overall results
        "career": career,
        "search_queries": queries
    }


def generate_related_subreddits(query: str) -> list:
    """
    Dynamically generate subreddit name variations based on a user's query.
    """
    base = query.lower().replace(" ", "")
    under = query.lower().replace(" ", "_")
    
    return list(dict.fromkeys([  # remove duplicates while preserving order
        base,
        f"{base}careers",
        f"{base}jobs",
        under,
        f"{under}_careers",
        f"{under}_jobs",
        "careerguidance",  # good catch-all
        "jobs"             # general job advice
    ]))

def get_reddit_posts(query: str):
    """
    Dynamically searches Reddit subreddits related to a career and returns post/comment data.
    """
    try:
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )

        all_results = []
        used_subreddits = set()

        potential_subreddits = generate_related_subreddits(query)

        for subreddit_name in potential_subreddits:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                posts = list(subreddit.search(query, limit=2, time_filter='year'))
                if not posts:
                    continue

                for post in posts:
                    used_subreddits.add(post.subreddit.display_name)

                    # Get top-level comments
                    post.comments.replace_more(limit=0)
                    top_comments = sorted(
                        [c for c in post.comments.list() if len(c.body) > 20],
                        key=lambda c: c.score,
                        reverse=True
                    )[:3]

                    summarized_comments = [
                        {
                            "comment": comment.body[:500] + "..." if len(comment.body) > 500 else comment.body,
                            "upvotes": comment.score
                        }
                        for comment in top_comments
                    ]

                    all_results.append({
                        "title": post.title,
                        "url": f"https://www.reddit.com{post.permalink}",
                        "score": post.score,
                        "subreddit": post.subreddit.display_name,
                        "created_utc": datetime.datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        "comments": summarized_comments
                    })
            except Exception:
                continue  # Skip invalid or private subreddits

        return {
            "subreddits": list(used_subreddits),
            "results": all_results[:5],  # Top 5 cleaned results
            "tools_used": ["reddit_search"],
            "query": query
        }

    except Exception as e:
        return {"error": f"Failed to fetch Reddit posts: {str(e)}"}


def scrape_coursera_courses(career: str):
    """
    Scrapes relevant courses from Coursera for a given career.
    
    Args:
        career (str): The career field to search for.
    
    Returns:
        list: List of courses with titles and URLs.
    """
    try:
        # Use proper URL encoding
        encoded_career = quote(career)
        url = f"https://www.coursera.org/search?query={encoded_career}&"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = httpx.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        courses = []
        
        # Try multiple selectors as Coursera's structure may vary
        course_selectors = [
            'div[data-testid="search-filter-group-results"] a',
            'div.cds-CommonCard-container a',
            'div.rc-SearchCard a',
            'a[href*="/learn/"]'
        ]
        
        course_links = []
        for selector in course_selectors:
            course_links = soup.select(selector)
            if course_links:
                break
        
        for link in course_links[:8]:  # Get up to 8 courses
            href = link.get('href', '')
            if not href.startswith('http'):
                href = f"https://www.coursera.org{href}"
            
            # Try to find title in different ways
            title = ""
            title_selectors = [
                'h3', 'h2', '[data-testid="course-name"]', 
                '.cds-119', '.card-title'
            ]
            
            for title_sel in title_selectors:
                title_elem = link.select_one(title_sel)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            if not title:
                title = link.get_text(strip=True)[:100]  # Fallback to link text
            
            if title and href and '/learn/' in href:
                courses.append({
                    "title": title,
                    "url": href
                })
        
        # Remove duplicates
        seen_urls = set()
        unique_courses = []
        for course in courses:
            if course['url'] not in seen_urls:
                seen_urls.add(course['url'])
                unique_courses.append(course)
        
        return unique_courses[:5]  # Return top 5 unique courses
        
    except Exception as e:
        return {"error": f"Failed to scrape Coursera courses: {str(e)}"}


#recently added tools to fetch top skills and recommended majors
def fetch_top_skills(career: str):
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return {"error": "SERPER_API_KEY not found"}
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    query = f"Top 10 skills required for {career} 2025 site:linkedin.com OR site:indeed.com"
    payload = {"q": query}

    try:
        response = httpx.post("https://google.serper.dev/search", headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        skills = []
        sources = []
        for item in data.get("organic", [])[:3]:
            title = item.get("title", "Skill info")
            link = item.get("link", "")
            skills.append(f"{title}")
            sources.append(f"{title} - {link}")

        return {"skills": skills, "sources": sources}
    except Exception as e:
        return {"error": str(e)}


def fetch_recommended_majors(career: str):
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return {"error": "SERPER_API_KEY not found"}
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    query = f"Best college majors for {career} 2025 site:usnews.com OR site:princetonreview.com"
    payload = {"q": query}

    try:
        response = httpx.post("https://google.serper.dev/search", headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        majors = []
        sources = []
        for item in data.get("organic", [])[:3]:
            title = item.get("title", "Major info")
            link = item.get("link", "")
            majors.append(f"{title}")
            sources.append(f"{title} - {link}")

        return {"majors": majors, "sources": sources}
    except Exception as e:
        return {"error": str(e)}


# Consider adding potential schooling requirements for the career chosen.
# Consider adding relevant / recent linkedin posts/articles about the career.

# FIX REDDIT TOOL TO PROVIDE BETTER INSIGHTS, LOOK AT CHATGPT ADVICE