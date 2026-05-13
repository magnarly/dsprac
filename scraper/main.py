"""
Web Scraper Service for DSA Learning Platform
Scrapes educational resources from various websites
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

app = FastAPI(
    title="DSA Web Scraper API",
    description="Scrapes DSA educational content from web resources",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    topics: List[str]
    sources: Optional[List[str]] = ["geeksforgeeks", "leetcode", "codeforces"]

class ScrapedContent(BaseModel):
    topic: str
    source: str
    title: str
    url: str
    content: str
    problem_statement: Optional[str] = None
    solution: Optional[str] = None
    difficulty: Optional[str] = None

# Target websites configuration
SOURCES = {
    "geeksforgeeks": {
        "base_url": "https://www.geeksforgeeks.org",
        "search_pattern": "/{topic}-problems",
    },
    "leetcode": {
        "base_url": "https://leetcode.com",
        "search_pattern": "/problemset/?search={topic}",
    },
    "codeforces": {
        "base_url": "https://codeforces.com",
        "search_pattern": "/problemset?tags={topic}",
    }
}

@app.get("/")
async def root():
    return {"message": "DSA Web Scraper Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/scrape", response_model=List[ScrapedContent])
async def scrape_topics(request: ScrapeRequest):
    """
    Scrape educational content for given topics from multiple sources
    """
    results = []
    
    for topic in request.topics:
        for source in request.sources:
            try:
                content = await scrape_source(topic, source)
                if content:
                    results.extend(content)
            except Exception as e:
                # Log error but continue with other sources
                print(f"Error scraping {source} for {topic}: {e}")
    
    if not results:
        # Return mock data if scraping fails
        results = await _mock_scrape(request.topics)
    
    return results

async def scrape_source(topic: str, source: str) -> List[ScrapedContent]:
    """Scrape a specific source for a topic"""
    contents = []
    
    if source == "geeksforgeeks":
        contents = await scrape_geeksforgeeks(topic)
    elif source == "leetcode":
        contents = await scrape_leetcode(topic)
    elif source == "codeforces":
        contents = await scrape_codeforces(topic)
    
    return contents

async def scrape_geeksforgeeks(topic: str) -> List[ScrapedContent]:
    """Scrape GeeksforGeeks for DSA problems"""
    # Normalize topic for URL
    topic_slug = topic.lower().replace(" ", "-")
    url = f"https://www.geeksforgeeks.org/{topic_slug}-data-structure-and-algorithms-tutorials/"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Extract article links
                    articles = []
                    for link in soup.find_all('a', href=True):
                        if topic_slug in link.get('href', '').lower():
                            articles.append({
                                "title": link.text.strip(),
                                "url": link['href']
                            })
                    
                    return [
                        ScrapedContent(
                            topic=topic,
                            source="geeksforgeeks",
                            title=art.get("title", "Untitled"),
                            url=art.get("url", ""),
                            content="",
                            difficulty="medium"
                        )
                        for art in articles[:5]  # Limit to 5 results
                    ]
        except Exception:
            pass
    
    return []

async def scrape_leetcode(topic: str) -> List[ScrapedContent]:
    """Scrape LeetCode for problems"""
    # LeetCode requires JavaScript rendering, so we'll use their API indirectly
    # This is a simplified version - in production you'd use their official API
    return []

async def scrape_codeforces(topic: str) -> List[ScrapedContent]:
    """Scrape Codeforces for problems"""
    url = f"https://codeforces.com/problemset?tags={topic}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    problems = []
                    for row in soup.find_all('tr', class_=lambda x: x and 'problemset-table' in str(x)):
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            problems.append({
                                "id": cells[0].text.strip(),
                                "title": cells[1].text.strip()
                            })
                    
                    return [
                        ScrapedContent(
                            topic=topic,
                            source="codeforces",
                            title=p.get("title", "Untitled"),
                            url=f"https://codeforces.com/problemset/problem/{p.get('id', '')}",
                            content="",
                            difficulty="medium"
                        )
                        for p in problems[:5]
                    ]
        except Exception:
            pass
    
    return []

async def _mock_scrape(topics: List[str]) -> List[ScrapedContent]:
    """Return mock scraped content for demo/testing"""
    mock_data = []
    
    for topic in topics:
        mock_data.extend([
            ScrapedContent(
                topic=topic,
                source="geeksforgeeks",
                title=f"Complete Guide to {topic}",
                url=f"https://geeksforgeeks.org/{topic.lower().replace(' ', '-')}",
                content=f"This is a comprehensive guide covering all aspects of {topic}.",
                problem_statement=f"Given an array, implement {topic} algorithm...",
                solution=f"def solution(arr):\n    # Implementation of {topic}\n    pass",
                difficulty="medium"
            ),
            ScrapedContent(
                topic=topic,
                source="codeforces",
                title=f"{topic} Practice Problems",
                url=f"https://codeforces.com/problemset/tags/{topic.lower().replace(' ', '_')}",
                content=f"Collection of competitive programming problems on {topic}",
                difficulty="hard"
            )
        ])
    
    return mock_data

@app.post("/scrape/notebooklm")
async def scrape_for_notebooklm(topics: List[str]):
    """
    Scrape content formatted for NotebookLM integration
    Returns structured data compatible with NotebookLM's import format
    """
    scraped = await scrape_topics(ScrapeRequest(topics=topics))
    
    # Format for NotebookLM
    notebooklm_format = []
    for item in scraped:
        notebooklm_format.append({
            "title": f"{item.topic}: {item.title}",
            "content": f"{item.content}\n\nProblem: {item.problem_statement or 'N/A'}\n\nSolution: {item.solution or 'N/A'}",
            "source": item.source,
            "url": item.url
        })
    
    return {"documents": notebooklm_format}

@app.get("/sources")
async def list_sources():
    """List available scraping sources"""
    return {"sources": list(SOURCES.keys())}
