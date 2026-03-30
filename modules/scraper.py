import requests
from bs4 import BeautifulSoup

def scrape_website_text(url):
    """
    Fetches HTML from a target company site and extracts raw readable text.
    Strips away boilerplate elements like navbars and footers to give clean context.
    """
    if not url.startswith('http'):
        url = 'https://' + url
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # 10 second timeout so we don't hang the whole UI
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove massive bloat elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.extract()
            
        # Extract text joining with space
        text = soup.get_text(separator=' ', strip=True)
        
        # Condense spacing to save on AI context tokens later
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Heavily cap at 5000 chars right now so we don't blow up the OpenAI token limit
        capped_text = text[:5000] + ("..." if len(text) > 5000 else "")
        return {"success": True, "text": capped_text}
        
    except requests.RequestException as e:
         return {"success": False, "error": f"Failed to reach {url}. Connection error: {str(e)}"}
