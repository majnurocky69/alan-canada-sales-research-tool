import os
import requests
import json
import google.generativeai as genai

def run_deep_research(company_name):
    """
    Connects to the Tavily AI Search API to scrape deep web insights, focusing on SEC filings,
    analyst reports, and premium news sources.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key or api_key == "your_tavily_api_key_here":
        return {"success": False, "error": "TAVILY_API_KEY not configured in .env. Get one free at tavily.com"}
        
    url = "https://api.tavily.com/search"
    
    # BUG FIX: Explicitly appending the word 'ONLY' and adding Year-Over-Year prompts to restrict irrelevant scraping
    query = f'"{company_name}" ONLY (Historical YoY Revenue growth OR Historical headcount OR Public SEC filings OR recent analyst opinions OR Reuters WSJ news)'
    
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced", # Forces Tavily to run a full browser scrape of the top 5 URLs
        "max_results": 5,           # Keep fast but comprehensive
        "include_raw_content": True # Pulls the massive raw text blocks from the websites
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
             
        if not results:
            return {"success": False, "error": "Tavily returned exactly 0 search results."}

        compiled_text = ""
        citations = []
        
        for r in results:
            url_str = r.get('url', '')
            title = r.get('title', 'Unknown Title')
            
            # Prefer the massive raw content scrape over the short snippet
            content = r.get('raw_content', '')
            if not content:
                content = r.get('content', '')
                
            # Limit massive PDF strings so we don't blow up the Gemini context window
            if len(content) > 2500:
                 content = content[:2500] + "... [truncated due to length]"
                 
            compiled_text += f"\n\n--- Source: {title} ({url_str}) ---\n{content}\n"
            citations.append({"title": title, "url": url_str})
            
        return {"success": True, "compiled_text": compiled_text, "citations": citations}
        
    except Exception as e:
        return {"success": False, "error": f"Tavily Deep Web Engine Error: {str(e)}"}


