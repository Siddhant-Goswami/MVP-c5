"""
Working news scraper that actually gets real recent content
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_recent_news_working(category: str, max_articles=5):
    """Working news scraper that gets real recent content"""
    print(f"🔍 Scraping recent {category} news (working method)...")
    
    articles = []
    
    # Use working news sources that are known to work
    working_sources = get_working_sources(category)
    
    for source in working_sources:
        try:
            print(f"📰 Checking: {source['name']}")
            articles_from_source = scrape_working_source(source)
            articles.extend(articles_from_source)
            
            if len(articles) >= max_articles:
                break
                
        except Exception as e:
            print(f"   ⚠️ Failed to scrape {source['name']}: {e}")
    
    print(f"✅ Found {len(articles)} real articles")
    return articles[:max_articles]

def get_working_sources(category):
    """Get working news sources for each category from config"""
    from config.sources import NEWS_SOURCES
    
    category_data = NEWS_SOURCES.get(category, {})
    api_sources = category_data.get('api_sources', [])
    
    sources = []
    
    for url in api_sources:
        if 'hn.algolia.com' in url:
            sources.append({
                'name': f'Hacker News {category}',
                'url': url,
                'type': 'api'
            })
        elif 'reddit.com' in url:
            sources.append({
                'name': f'Reddit {category}',
                'url': url,
                'type': 'reddit'
            })
        elif 'arxiv.org' in url:
            sources.append({
                'name': f'ArXiv {category}',
                'url': url,
                'type': 'arxiv'
            })
    
    return sources

def scrape_working_source(source):
    """Scrape from a working source"""
    articles = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        if source['type'] == 'api':
            articles = scrape_api_source(source, headers)
        elif source['type'] == 'reddit':
            articles = scrape_reddit_source(source, headers)
        elif source['type'] == 'arxiv':
            articles = scrape_arxiv_source(source, headers)
            
    except Exception as e:
        print(f"   ❌ Error scraping {source['name']}: {e}")
    
    return articles

def scrape_api_source(source, headers):
    """Scrape from API source (like Hacker News)"""
    articles = []
    
    try:
        response = requests.get(source['url'], headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'hits' in data:
            for hit in data['hits'][:5]:
                title = hit.get('title', '')
                url = hit.get('url', '')
                points = hit.get('points', 0)
                created_at = hit.get('created_at', '')
                
                if title and url and points > 5:  # Only articles with some engagement
                    # Get content from the article
                    content = get_article_content_safe(url)
                    
                    if content:
                        articles.append({
                            'source': url,
                            'title': title,
                            'content': content[:1500],
                            'published': created_at
                        })
                        print(f"   ✅ Found: {title[:50]}...")
                        
    except Exception as e:
        print(f"   ⚠️ API scraping error: {e}")
    
    return articles

def scrape_reddit_source(source, headers):
    """Scrape from Reddit source"""
    articles = []
    
    try:
        response = requests.get(source['url'], headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'data' in data and 'children' in data['data']:
            for post in data['data']['children'][:5]:
                post_data = post.get('data', {})
                title = post_data.get('title', '')
                url = post_data.get('url', '')
                score = post_data.get('score', 0)
                selftext = post_data.get('selftext', '')
                
                if title and url and score > 10:  # Only posts with some engagement
                    content = selftext if selftext else f"Reddit discussion about: {title}"
                    
                    articles.append({
                        'source': url,
                        'title': title,
                        'content': content[:1500],
                        'published': None
                    })
                    print(f"   ✅ Found: {title[:50]}...")
                    
    except Exception as e:
        print(f"   ⚠️ Reddit scraping error: {e}")
    
    return articles

def scrape_arxiv_source(source, headers):
    """Scrape from ArXiv source"""
    articles = []
    
    try:
        response = requests.get(source['url'], headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse XML response
        from xml.etree import ElementTree as ET
        root = ET.fromstring(response.content)
        
        # ArXiv namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        for entry in root.findall('atom:entry', ns)[:5]:
            title_elem = entry.find('atom:title', ns)
            summary_elem = entry.find('atom:summary', ns)
            link_elem = entry.find('atom:link[@type="text/html"]', ns)
            
            if title_elem is not None and summary_elem is not None:
                title = title_elem.text.strip()
                summary = summary_elem.text.strip()
                url = link_elem.get('href') if link_elem is not None else ''
                
                articles.append({
                    'source': url,
                    'title': title,
                    'content': summary[:1500],
                    'published': None
                })
                print(f"   ✅ Found: {title[:50]}...")
                
    except Exception as e:
        print(f"   ⚠️ ArXiv scraping error: {e}")
    
    return articles

def get_article_content_safe(url):
    """Safely get article content with error handling"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to extract main content
        content_selectors = [
            'article p',
            '.entry-content p',
            '.post-content p',
            'main p',
            'p'
        ]
        
        for selector in content_selectors:
            paragraphs = soup.select(selector)
            if paragraphs:
                content_parts = []
                for p in paragraphs[:3]:  # First 3 paragraphs
                    text = p.get_text(strip=True)
                    if len(text) > 30:
                        content_parts.append(text)
                
                if content_parts:
                    return ' '.join(content_parts)
        
        # Fallback: get all text
        text = soup.get_text()
        if len(text) > 100:
            return text[:500]  # First 500 chars
        
    except Exception as e:
        print(f"     ⚠️ Error getting content from {url}: {e}")
    
    return ""

# Main function
def scrape_sources_working(category: str, max_articles=5):
    """Main function using working scraping approach"""
    return scrape_recent_news_working(category, max_articles)
