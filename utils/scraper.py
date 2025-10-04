from firecrawl import FirecrawlApp
import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

def scrape_sources(category: str, max_articles=5):
    """Scrape recent articles using working methods"""
    print(f"🔍 Scraping recent {category} articles...")
    
    articles = []
    
    # Method 1: Try working API-based scraping (most reliable)
    try:
        print("📰 Trying working API scraping...")
        from utils.working_news_scraper import scrape_sources_working
        working_articles = scrape_sources_working(category, max_articles)
        if working_articles:
            articles.extend(working_articles)
            print(f"   ✅ Found {len(working_articles)} real articles via API scraping")
    except Exception as e:
        print(f"   ⚠️ Working scraping failed: {e}")
    
    # Method 2: Try RSS feeds if we don't have enough articles
    if len(articles) < max_articles:
        try:
            print("📰 Trying RSS feeds for additional content...")
            rss_articles = scrape_rss_feeds(category, max_articles - len(articles))
            if rss_articles:
                articles.extend(rss_articles)
                print(f"   ✅ Found {len(rss_articles)} additional articles via RSS")
        except Exception as e:
            print(f"   ⚠️ RSS scraping failed: {e}")
    
    # Method 3: Try Firecrawl if we still don't have enough articles
    if len(articles) < max_articles:
        try:
            print("📰 Trying Firecrawl for additional content...")
            firecrawl_articles = scrape_with_firecrawl(category, max_articles - len(articles))
            articles.extend(firecrawl_articles)
        except Exception as e:
            print(f"   ⚠️ Firecrawl scraping failed: {e}")
    
    # Method 4: Use fallback only as absolute last resort
    if len(articles) < 2:
        print(f"⚠️ Using fallback content for {category}...")
        fallback_articles = get_fallback_articles(category)
        articles.extend(fallback_articles)
    
    print(f"\n📰 Total articles found: {len(articles)}")
    return articles

def scrape_rss_feeds(category: str, max_articles=5):
    """Scrape RSS feeds for additional content"""
    from config.sources import NEWS_SOURCES
    import feedparser
    import ssl
    
    articles = []
    
    # Create SSL context that doesn't verify certificates (for development)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    category_data = NEWS_SOURCES.get(category, {})
    rss_sources = category_data.get('rss_sources', [])
    
    for feed_url in rss_sources:
        try:
            print(f"   📡 Checking RSS: {feed_url}")
            
            # Parse RSS feed with custom SSL context
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                print(f"     ⚠️ RSS parsing issues: {feed.bozo_exception}")
            
            for entry in feed.entries[:3]:  # Get latest 3 entries
                try:
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    summary = entry.get('summary', '')
                    
                    if title and link:
                        # Clean HTML from summary
                        import re
                        clean_summary = re.sub(r'<[^>]+>', ' ', summary).strip()
                        
                        if clean_summary and len(clean_summary) > 50:
                            articles.append({
                                'source': link,
                                'title': title,
                                'content': clean_summary[:1500],
                                'published': entry.get('published', None)
                            })
                            print(f"     ✅ Found: {title[:50]}...")
                            
                except Exception as e:
                    print(f"     ⚠️ Error parsing entry: {e}")
                    
        except Exception as e:
            print(f"   ⚠️ Failed to parse RSS feed: {e}")
    
    return articles

def scrape_with_firecrawl(category: str, max_articles=5):
    """Scrape using Firecrawl (original method as fallback)"""
    from config.sources import NEWS_SOURCES
    
    firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    articles = []
    
    category_data = NEWS_SOURCES.get(category, {})
    sources = category_data.get('web_sources', [])[:2]  # Only 2 sources for MVP
    
    for source_url in sources:
        try:
            print(f"   Processing: {source_url}")
            
            # Try to find recent articles using search
            recent_articles = find_recent_articles_via_search(firecrawl, source_url, category)
            
            if recent_articles:
                for article_url in recent_articles[:max_articles]:
                    try:
                        article_content = scrape_article_content(firecrawl, article_url)
                        if article_content and len(article_content.strip()) > 100:
                            articles.append({
                                'source': article_url,
                                'content': article_content[:1500],
                                'title': extract_title_from_url(article_url)
                            })
                            print(f"     ✅ Scraped: {extract_title_from_url(article_url)}")
                    except Exception as e:
                        print(f"     ⚠️ Failed to scrape article: {e}")
            else:
                # Try direct homepage scraping
                result = firecrawl.scrape(source_url)
                content = extract_content_from_result(result)
                
                if content and len(content.strip()) > 100:
                    recent_content = extract_recent_content_from_homepage(content)
                    if recent_content:
                        articles.append({
                            'source': source_url,
                            'content': recent_content[:1500],
                            'title': f"Latest from {extract_domain_name(source_url)}"
                        })
                        print(f"     ✅ Extracted homepage content")
                        
        except Exception as e:
            print(f"     ❌ Error processing {source_url}: {e}")
    
    return articles

def find_recent_articles_via_search(firecrawl, base_url, category):
    """Find recent articles using search functionality"""
    try:
        # Create search queries for recent content
        search_queries = [
            f"site:{extract_domain_name(base_url)} {category} 2025",
            f"site:{extract_domain_name(base_url)} {category} 2024",
            f"site:{extract_domain_name(base_url)} latest {category}",
            f"site:{extract_domain_name(base_url)} recent {category}"
        ]
        
        recent_articles = []
        
        for query in search_queries[:2]:  # Limit to 2 queries to avoid API limits
            try:
                # Use Firecrawl's search functionality if available
                if hasattr(firecrawl, 'search'):
                    search_results = firecrawl.search(query)
                    if search_results and hasattr(search_results, 'results'):
                        for result in search_results.results[:3]:  # Limit to 3 results
                            if hasattr(result, 'url'):
                                recent_articles.append(result.url)
                else:
                    # Fallback: try to construct recent article URLs
                    recent_urls = construct_recent_urls(base_url)
                    recent_articles.extend(recent_urls)
                    
            except Exception as e:
                print(f"   ⚠️ Search failed for '{query}': {e}")
                continue
        
        return list(set(recent_articles))  # Remove duplicates
        
    except Exception as e:
        print(f"   ⚠️ Search approach failed: {e}")
        return []

def construct_recent_urls(base_url):
    """Construct likely recent article URLs based on common patterns"""
    from datetime import datetime
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    recent_urls = []
    
    # Common recent URL patterns
    patterns = [
        f"{base_url.rstrip('/')}/2025/{current_month:02d}/",
        f"{base_url.rstrip('/')}/blog/",
        f"{base_url.rstrip('/')}/news/",
    ]
    
    # For specific domains, add known recent paths
    domain = extract_domain_name(base_url)
    
    if 'openai.com' in domain:
        recent_urls.extend([
            f"{base_url.rstrip('/')}/gpt-4o",
            f"{base_url.rstrip('/')}/gpt-4",
            f"{base_url.rstrip('/')}/chatgpt"
        ])
    elif 'anthropic.com' in domain:
        recent_urls.extend([
            f"{base_url.rstrip('/')}/claude",
            f"{base_url.rstrip('/')}/safety"
        ])
    elif 'deepmind.com' in domain:
        recent_urls.extend([
            f"{base_url.rstrip('/')}/gemini",
            f"{base_url.rstrip('/')}/research"
        ])
    
    return recent_urls[:5]  # Limit to 5 URLs

def extract_recent_content_from_homepage(content):
    """Extract recent content from homepage by looking for recent indicators"""
    import re
    
    if not content:
        return None
    
    # Look for recent date patterns and content
    recent_patterns = [
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+202[4-5]',
        r'\b202[4-5]\b',
        r'(?:yesterday|today|this week|this month|recently|latest|new|announced|released)',
    ]
    
    # Split content into sentences and find recent ones
    sentences = re.split(r'[.!?]+', content)
    recent_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 50:  # Only consider substantial sentences
            for pattern in recent_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    recent_sentences.append(sentence)
                    break
    
    if recent_sentences:
        # Take the first few recent sentences
        recent_content = '. '.join(recent_sentences[:5]) + '.'
        return recent_content
    
    return None

def get_fallback_articles(category):
    """Get fallback articles when scraping fails"""
    fallback_content = {
        'AI': [
            {
                'source': 'https://openai.com/blog/',
                'content': 'OpenAI continues to advance AI safety and alignment research with new developments in large language models and multimodal AI systems. Recent announcements include improvements to model reasoning capabilities and enhanced safety measures.',
                'title': 'OpenAI AI Safety Research Update'
            },
            {
                'source': 'https://www.anthropic.com/news',
                'content': 'Anthropic has been focusing on constitutional AI and safety-first approaches to AI development. Recent work includes advances in AI alignment and responsible AI deployment practices.',
                'title': 'Anthropic Constitutional AI Progress'
            }
        ],
        'Technology': [
            {
                'source': 'https://techcrunch.com/',
                'content': 'Technology companies continue to push boundaries in AI, cloud computing, and digital transformation. Recent trends include enterprise AI adoption and sustainable technology solutions.',
                'title': 'Latest Technology Trends'
            }
        ]
    }
    
    return fallback_content.get(category, [])

def get_recent_article_links(base_url):
    """Get recent article links from a news source homepage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Common patterns for article links
        article_links = []
        
        # Look for common article link patterns
        link_selectors = [
            'a[href*="/blog/"]',
            'a[href*="/news/"]', 
            'a[href*="/article/"]',
            'a[href*="/post/"]',
            'a[href*="/2024/"]',
            'a[href*="/2025/"]',
            '.post-title a',
            '.article-title a',
            '.blog-post a',
            'h1 a',
            'h2 a',
            'h3 a'
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = base_url.rstrip('/') + href
                    elif not href.startswith('http'):
                        href = base_url.rstrip('/') + '/' + href
                    
                    # Filter for likely article URLs
                    if is_likely_article_url(href, base_url):
                        article_links.append(href)
        
        # Remove duplicates and return recent ones
        unique_links = list(dict.fromkeys(article_links))
        return unique_links[:10]  # Return up to 10 recent articles
        
    except Exception as e:
        print(f"   ⚠️ Could not get article links from {base_url}: {e}")
        return []

def is_likely_article_url(url, base_url):
    """Check if URL is likely an article URL"""
    domain = extract_domain_name(base_url)
    
    # Skip certain patterns
    skip_patterns = [
        '/tag/', '/category/', '/author/', '/search', '/contact', 
        '/about', '/privacy', '/terms', '/subscribe', '/newsletter',
        '#', 'mailto:', 'javascript:', '/feed', '/rss'
    ]
    
    for pattern in skip_patterns:
        if pattern in url.lower():
            return False
    
    # Must be from the same domain
    if domain not in url:
        return False
        
    # Look for article indicators
    article_indicators = [
        '/blog/', '/news/', '/article/', '/post/', 
        '/2024/', '/2025/', '/ai/', '/machine-learning/',
        '.html', '.php'
    ]
    
    return any(indicator in url.lower() for indicator in article_indicators)

def scrape_article_content(firecrawl, article_url):
    """Scrape content from a specific article URL"""
    try:
        result = firecrawl.scrape(article_url)
        return extract_content_from_result(result)
    except Exception as e:
        print(f"   ⚠️ Failed to scrape article content: {e}")
        return None

def extract_content_from_result(result):
    """Extract content from Firecrawl result object"""
    content = ""
    
    if hasattr(result, 'content'):
        content = result.content
    elif hasattr(result, 'data') and hasattr(result.data, 'content'):
        content = result.data.content
    elif isinstance(result, dict):
        content = result.get('content', '')
    
    # Clean up the content
    if content:
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        # Remove common navigation elements
        content = re.sub(r'(Home|About|Contact|Subscribe|Newsletter).*?(?=\w)', '', content, flags=re.IGNORECASE)
    
    return content

def extract_title_from_url(url):
    """Extract a title from URL"""
    # Extract the last meaningful part of the URL
    parts = url.rstrip('/').split('/')
    if parts:
        last_part = parts[-1]
        # Clean up the title
        title = last_part.replace('-', ' ').replace('_', ' ')
        title = re.sub(r'\.(html|php|aspx?)$', '', title, flags=re.IGNORECASE)
        return title.title()
    return "Article"

def extract_domain_name(url):
    """Extract domain name from URL"""
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc