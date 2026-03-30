import requests
import urllib.parse
import xml.etree.ElementTree as ET

def get_recent_news(company_name, max_results=5):
    """
    Fetches recent news articles using Google News RSS.
    Does not require a paid API key and taps into global aggregated news.
    """
    try:
        # Wrap company name in quotes for exact match search semantics
        query = urllib.parse.quote(f'"{company_name}"')
        
        # Searching news from the past year, localized to Canada
        url = f"https://news.google.com/rss/search?q={query}+when:1y&hl=en-CA&gl=CA&ceid=CA:en"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse XML RSS feed
        root = ET.fromstring(response.content)
        
        news_items = []
        # Find all news item nodes
        for item in root.findall('.//item'):
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text
            
            # Google often appends " - Source Name" at the end of the title. Let's clean it up.
            clean_title = title.rsplit(' - ', 1)[0] if ' - ' in title else title
            
            news_items.append({
                "title": clean_title,
                "url": link,
                "date": pub_date
            })
            
            if len(news_items) >= max_results:
                break
                
        return {"success": True, "articles": news_items}
        
    except Exception as e:
        return {"success": False, "error": f"Failed to fetch news: {str(e)}"}
