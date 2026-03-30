import os
import json
import google.generativeai as genai

def evaluate_prospect(apollo_data, scraped_text, news_data, deep_research_text):
    """
    Feeds the completely automated raw data strings (from Apollo, Google News, and Tavily Deep Web)
    into the Gemini model. Demands a strict JSON evaluation against 6 core B2B parameters, extracting
    actionable talking points and precise deep research citations.
    """
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return {"success": False, "error": "GEMINI_API_KEY not configured in .env file."}
        
    try:
        genai.configure(api_key=api_key)
        
        # Dynamically discover which text-generation model the user's API Key has access to.
        # This completely dodges the 404 'Model Not Found' crashing bug that Plagued the previous static setup. 
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                
        # Preferred execution hierarchy
        target_model = None
        for preferred in ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro", "gemini-1.5-flash", "gemini-1.5-pro"]:
            if preferred in available_models:
                target_model = preferred
                break
                
        if not target_model and available_models:
            target_model = available_models[0]
        
        model = genai.GenerativeModel(model_name=target_model)
        
        system_prompt = f"""
        You are a cold, calculated analytical logic engine acting as a lead scorer for a premium B2B software/service pipeline.
        
        Your objective is to evaluate the provided raw data (from Apollo API, Website scrapes, News articles, and Deep Analyst Web text) 
        and score the prospect out of 100 based on the Ideal Customer Profile (ICP).
        
        CRITICAL FORMATTING RULE: Do not use the `$` symbol for currency, write out 'USD' or 'CAD' or 'dollars' instead. 
        Streamlit will interpret `$` as a math equation and break the font.
        
        IDEAL CUSTOMER PROFILE (ICP):
        1. **Size (30 points)**: Target range is 5 to 100 employees. Deduct points severely if they are >500 or <5.
        2. **Location (20 points)**: Operations must ideally be in Alberta (AB) or Ontario (ON). Deduct if neither.
        3. **Pain Signals (15 points)**: Are they struggling with scaling, retention, or legacy systems?
        4. **Growth (10 points)**: Evidence of rapid hiring, funding rounds, or expansion.
        5. **HR/Ops Setup (10 points)**: Do they have dedicated HR managers or structured operations teams? 
        6. **Culture (15 points)**: Do they care about employee wellness, proactive modern software, or innovation?
        
        ANTI-NOISE REQUIREMENT: 
        The Deep Analyst Web text will contain SEC filings or massive block reports that might occasionally mention COMPETING companies (like 'Home Capital' when searching 'Wealthsimple'). 
        Ensure you only extract data that is EXPLICITLY about the target company: {apollo_data.get('company_name', 'The target')}.
        Ignore massive dumps of banking data if it belongs to a competitor. Focus fiercely on the core target company.
        
        You must return a raw, parsable JSON block. DO NOT WRAP WITH MARKDOWN (No ```json).
        
        Required JSON Schema:
        {{
            "total_score": 85,
            "executive_summary": "In 3-4 sentences, summarize their state, any acquisitions, financial trajectory, and whether they fit the pipeline.",
            "historical_trend": "In 3-4 sentences, explicitly describe their YoY growth. Quote numbers from the Deep Web Analyst texts if you have them (e.g., 'Grew revenue by 93%'). State if unknown.",
            "score_justification": "Detailed bulleted explanation mapping how you distributed the 100 points.",
            "talking_points": [
                {{"title": "Angle 1", "content": "Detailed reasoning here..."}},
                {{"title": "Angle 2", "content": "Detailed reasoning here..."}},
                 {{"title": "Angle 3", "content": "Detailed reasoning here..."}}
            ],
            "citations": [
                {{"source": "WSJ or Apollo etc", "insight_extracted": "They raised exactly X dollars today...", "url": "extracted url from deep web/news here. Pass Empty string if none provided"}}
            ]
        }}
        """

        data_payload = f"""
        ---- TARGET METRICS ----
        APOLLO DATA: {json.dumps(apollo_data)}
        ---- GOOGLE RECENT HEADLINES ----
        {json.dumps(news_data)}
        ---- SCRAPED B2B WEB CONTENT ----
        {scraped_text}
        ---- DEEP WEB SEC/ANALYST REPORTS ----
        {deep_research_text}
        """

        response = model.generate_content(system_prompt + data_payload)
        output = response.text
        
        # Clean markdown wrappers if gemini decides to add them anyway
        if output.startswith("```json"):
            output = output[7:]
        if output.startswith("```"):
            output = output[3:]
        if output.endswith("```"):
            output = output[:-3]
            
        parsed_json = json.loads(output.strip())
        parsed_json["success"] = True
        return parsed_json
        
    except json.JSONDecodeError:
        return {"success": False, "error": f"Failed to parse JSON target payload. Raw Output: {output[:100]}"}
    except Exception as e:
         return {"success": False, "error": f"Scoring Engine Framework crash: {str(e)}"}
