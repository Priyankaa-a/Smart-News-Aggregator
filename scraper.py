import feedparser
import requests
from urllib.parse import urlparse
import re
import time
from bs4 import BeautifulSoup

# Category-wise RSS feeds (INDIAN NEWS SOURCES)
NEWS_SOURCES = {
    "Political": [
        "https://feeds.indianexpress.com/politics",
        "https://www.thehindu.com/news/national/?service=rss",
    ],
    "Sports": [
        "https://feeds.indianexpress.com/sports",
        "https://www.thehindu.com/sport/?service=rss",
    ],
    "Economic": [
        "https://feeds.indianexpress.com/business",
        "https://www.thehindu.com/business/?service=rss",
    ],
    "Education": [
        "https://feeds.indianexpress.com/education",
        "https://www.thehindu.com/education/?service=rss",
    ],
    "Tech": [
        "https://feeds.indianexpress.com/technology",
        "https://www.thehindu.com/sci-tech/?service=rss",
    ],
    "Major headlines of the day": [
        "https://www.thehindu.com/news/?service=rss",
        "https://feeds.indianexpress.com/",
    ]
}

def clean_html(text):
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    
    # Remove HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    
    # Decode entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&apos;', "'")
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def extract_content_from_url(url):
    """Try to scrape full article content from URL if RSS content is too short."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=5, headers=headers)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'ads']):
            element.decompose()
        
        # Try to find article body
        article_text = ""
        
        # Try common article selectors
        selectors = [
            'article', 'main', '[role="main"]',
            '.article-content', '.story', '.content',
            '.post-content', '#content'
        ]
        
        for selector in selectors:
            article = soup.select_one(selector)
            if article:
                # Get paragraphs
                paragraphs = article.find_all('p')
                article_text = ' '.join([p.get_text() for p in paragraphs])
                if len(article_text) > 200:
                    break
        
        # If no selector matched, get all paragraphs
        if len(article_text) < 200:
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text() for p in paragraphs])
        
        # Clean the text
        article_text = clean_html(article_text)
        
        # Return if substantial content found
        if len(article_text) > 300:
            return article_text[:5000]  # Limit to 5000 chars
        
        return None
    except Exception as e:
        print(f"Could not extract from {url}: {e}")
        return None

def fetch_rss_feed(feed_url, category):
    """Fetch articles from an RSS feed with better content extraction."""
    try:
        print(f"   📡 Fetching: {get_domain(feed_url)}")
        
        feed = feedparser.parse(feed_url)
        
        if not feed.entries:
            print(f"   ⚠️  No entries found")
            return []
        
        print(f"   ✅ Found {len(feed.entries)} entries")
        
        articles = []
        
        for idx, entry in enumerate(feed.entries[:20]):
            try:
                # Get headline
                headline = entry.get('title', 'No title')
                headline = clean_html(headline)
                
                # Get URL
                url = entry.get('link', '')
                
                # Get content from RSS first
                content = entry.get('summary', '')
                if not content:
                    content = entry.get('description', '')
                if not content and 'content' in entry:
                    content = entry.get('content', [{}])[0].get('value', '')
                
                content = clean_html(content)
                
                # If RSS content is too short, try to scrape full article
                if len(content) < 300 and url:
                    print(f"      📰 Content too short, scraping full article...")
                    full_content = extract_content_from_url(url)
                    if full_content:
                        content = full_content
                
                # Get author
                author = entry.get('author', 'Unknown')
                if author:
                    author = clean_html(author)
                
                # Skip if missing critical data
                if not url or not headline or len(content) < 50:
                    continue
                
                article = {
                    "headline": headline[:200],
                    "content": content[:5000],  # Limit to 5000 chars
                    "url": url,
                    "source": get_domain(feed_url),
                    "category": category,
                    "image": None,
                    "authors": author
                }
                
                articles.append(article)
                print(f"      ✓ Article {len(articles)}: {headline[:60]}... ({len(content)} chars)")
                
            except Exception as e:
                print(f"      Error parsing entry {idx}: {str(e)[:50]}")
                continue
        
        print(f"   📰 Extracted {len(articles)} valid articles\n")
        return articles
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return []

def get_domain(url):
    """Extract domain name from URL."""
    try:
        domain = urlparse(url).netloc
        domain = domain.replace('www.', '').replace('feeds.', '')
        parts = domain.split('.')
        if len(parts) > 1:
            domain = parts[-2] + '.' + parts[-1]
        return domain.upper()
    except:
        return "UNKNOWN"

def scrape_news_by_category(category):
    """Scrape news articles for a specific category."""
    print(f"\n{'='*60}")
    print(f"🔍 SCRAPING: {category}")
    print(f"{'='*60}")
    
    articles = []
    sources = NEWS_SOURCES.get(category, [])
    
    print(f"📌 Found {len(sources)} news source(s) for {category}\n")
    
    for source in sources:
        rss_articles = fetch_rss_feed(source, category)
        articles.extend(rss_articles)
        time.sleep(2)
    
    print(f"{'='*60}")
    print(f"✅ TOTAL for {category}: {len(articles)} articles")
    print(f"{'='*60}\n")
    
    return articles

def scrape_all_categories():
    """Scrape news from all categories."""
    all_articles = {}
    for category in NEWS_SOURCES.keys():
        all_articles[category] = scrape_news_by_category(category)
    return all_articles