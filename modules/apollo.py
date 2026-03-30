import requests
import os

def get_company_data(domain):
    """
    Connects to the Apollo Organization Enrichment API to fetch core demographics and deep financial metrics.
    """
    api_key = os.getenv("APOLLO_API_KEY")
    if not api_key or api_key == "your_apollo_api_key_here":
        return {"success": False, "error": "APOLLO_API_KEY not found in .env. Please configure it."}
        
    url = "https://api.apollo.io/v1/organizations/enrich"
    params = {"domain": domain}
    headers = {
        "X-Api-Key": api_key,
        "Cache-Control": "no-cache"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        org = data.get("organization")
        
        if not org:
            return {"success": False, "error": "Domain not found in Apollo database."}
            
        # BUG FIX: Fallback logic for headcount moving targets
        headcount = org.get("estimated_num_employees")
        if not headcount:
            headcount = org.get("num_employees", "Unknown")
            
        return {
            "success": True,
            "company_name": org.get("name"),
            "domain": org.get("domain"),
            "employee_count": headcount,
            "location": f"{org.get('city', '')}, {org.get('state', '')}, {org.get('country', '')}".strip(" ,"),
            "industry": org.get("industry", "Unknown"),
            "short_description": org.get("short_description", "No description provided."),
            # Newly Added Deep Financials
            "annual_revenue": org.get("annual_revenue_printed", "Not Disclosed"),
            "total_funding": org.get("total_funding_printed", "None/Not Disclosed"),
            "latest_funding_stage": org.get("latest_funding_stage", "Unknown"),
            "founded_year": org.get("founded_year", "Unknown")
        }
        
    except requests.exceptions.RequestException as e:
        if response is not None and response.status_code == 422:
             return {"success": False, "error": f"Apollo API Error: 422 - Invalid API Key or Location. Verify your .env setup."}
        return {"success": False, "error": f"Network Error: {str(e)}"}



