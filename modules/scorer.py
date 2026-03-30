import os
import json
import google.generativeai as genai

def evaluate_prospect(apollo_data, scraped_text, news_data, deep_research_text=""):
    """
    Passes extracted company data along with Deep Web Research to Gemini for strict ICP scoring.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return {"success": False, "error": "GEMINI_API_KEY not configured. Add it to .env."}

    genai.configure(api_key=api_key)

    system_prompt = """
    You are an expert Sales Intelligence AI for Alan Canada.
    Alan Canada sells premium digital-first health insurance to B2B clients. It supplements public healthcare, offers 48-hour reimbursements, virtual care, mental health support, and allows patients to choose any licensed provider without restricted networks.

    Your goal is to evaluate a potential prospect company based on the provided data and return a JSON object scoring them out of 100 on how good of a fit they are.

    CRITICAL RULES FOR SCORING AND PARSING (100 points total):
    1. Size (30 points): The ideal size is 5-100 employees. If they are in this range, award full points. If they are >200 or 1-2 people, severely penalize the score.
    2. Location (20 points): Operations or HQ MUST be in Alberta (AB) or Ontario (ON). Award full points if true. If definitively outside, award 0 for this section. If it is unknown, award 10 points.
    3. News & Pain Signals (15 points): Look at recent headlines. Do they mention scaling, rapid hirings, layoffs, or HR news?
    4. HR / People Ops Signals (10 points): Does their website or data mention hiring HR/People Ops roles, or expanding rapidly?
    5. Culture & Wellness Signals (25 points): Does their website mention caring for employees, remote work flexibility, modern wellness, or highlight how they treat their team?
    6. IRRELEVANT NOISE ISOLATION: The Deep Web Text may erroneously mention massive partner or competitor companies (like 'Home Capital' or 'Power Corp' when researching 'Wealthsimple'). DO NOT draw talking points or revenue data from these side-companies. Only write about the prime target!

    Your output MUST be a precise JSON object matching this schema exactly with no other text:
    {
        "total_score": 85,
        "executive_summary": "A 3-5 sentence strategic breakdown explicitly analyzing their Revenue, Funding Stage (from Demographics), and ANY acquisitions, new market entries, or user growth detected in the News and Scraped text.",
        "historical_trend": "A 2-4 sentence analysis explicitly outlining their Year-over-Year (YoY) revenue growth, funding history progression, or headcount trajectories found in the deep Web Analyst Reports. Give the numbers/years explicitly. If none exist, state 'Insufficient historical financial reporting available.'",
        "score_justification": "A 2-3 sentence summary explaining exactly why they got this score based on the 5 rules.",
        "talking_points": [
            {
                "title": "Short Punchy Angle Name",
                "content": "Detailed strategic angle explaining what facts the sales rep should bring up and how to position Alan as the exact solution to this company's specific situation."
            }
        ],
        "citations": [
            {
                "source": "Name of News Outlet or SEC Filing Report",
                "url": "https://...",
                "insight_extracted": "A 1 sentence note on what specific stat/quote was pulled from this link."
            }
        ]
    }
    """

    bulletproof_prompt = f"""
    {system_prompt}

    --- DATA TO EVALUATE ---
    APOLLO DEMOGRAPHICS:
    {json.dumps(apollo_data, indent=2)}

    RECENT NEWS:
    {json.dumps(news_data, indent=2)}

    SCRAPED WEBSITE HIGHLIGHTS:
    {scraped_text}

    DEEP WEB RESEARCH (Filings, WSJ, Reuters, Analyst Reports):
    {deep_research_text}
    """

    try:
        # Dynamically find a valid model attached to the user's specific API key
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                
        # Try to select the best available model, falling back gracefully
        target_model = None
        for preferred in ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]:
            if preferred in available_models:
                target_model = preferred
                break
                
        # If none of the preferred models match, just take the first one available
        if not target_model and available_models:
            target_model = available_models[0]
            
        if not target_model:
            return {"success": False, "error": "No valid Gemini models found for your API key. Check your Google AI Studio account."}

        # Initialize the dynamically selected model
        model = genai.GenerativeModel(model_name=target_model)
        
        # Fire standard content generation (highly stable across all v1 and v1beta API versions)
        response = model.generate_content(bulletproof_prompt)
        
        result = response.text
        
        # Wipe out markdown blocks if the AI wraps the JSON (since we disabled strict mime_type format for stability)
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
            
        parsed_json = json.loads(result)
        parsed_json["success"] = True
        return parsed_json
        
    except Exception as e:
        return {"success": False, "error": str(e)}
