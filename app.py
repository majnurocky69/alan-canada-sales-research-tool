import streamlit as st
import os
import time
from dotenv import load_dotenv

# Import Modules
from modules import apollo
from modules import scraper
from modules import news
from modules import scorer
from modules import researcher
from modules import reporter

# Load environment variables
load_dotenv()

# --- HELPER FUNCTION: PREVENT LATEX BUGS ---
def safe_md(text):
    """
    Escapes dollar signs in strings so Streamlit's Markdown engine 
    doesn't accidentally convert currency values into KaTeX math equations.
    """
    if not text:
        return ""
    return str(text).replace('$', '\\$')

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Alan Canada | Sales Intelligence",
    page_icon="🍁",
    layout="wide"
)

# --- CUSTOM CSS (Alan Branding) ---
st.markdown("""
<style>
    /* Clean Typography & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #FAFAFA !important;
        color: #302929;
    }
    
    /* Sleek Primary Button */
    .stButton>button {
        background-color: #32E3A0 !important;
        color: #302929 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #26c489 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        color: #32E3A0 !important;
        font-weight: 700 !important;
        font-size: 3rem !important;
    }
    
    /* Clean headers */
    h1, h2, h3 {
        color: #302929 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Soften the text input */
    .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid #EAEAEA !important;
        background-color: #FFFFFF !important;
        color: #302929 !important;
    }
    
    .news-card {
        padding: 12px;
        margin-bottom: 10px;
        background-color: white;
        border-radius: 6px;
        border: 1px solid #EAEAEA;
    }
    
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("Alan Lead Intelligence")
st.markdown("Automated scouting and scoring for B2B health insurance prospects.")
st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    apollo_key = os.getenv("APOLLO_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        st.warning("GEMINI_API_KEY missing from .env")
    else:
        st.success("Gemini configured")
        
    if not apollo_key or apollo_key == "your_apollo_api_key_here":
        st.warning("APOLLO_API_KEY missing from .env")
    else:
        st.success("Apollo configured")
        
    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        st.warning("TAVILY_API_KEY missing from .env")
    else:
        st.success("Tavily Deep Search configured")

# --- MAIN INPUT ---
st.header("Target Prospect")

col1, col2 = st.columns([2, 1])

with col1:
    company_name = st.text_input("Company Name", placeholder="e.g., Apple Inc.")
    company_url = st.text_input("Company Domain/Website (Required for Apollo Search)", placeholder="e.g., apple.com")

with col2:
    st.write("") 
    st.write("") 
    run_button = st.button("Run Intelligence Scan", type="primary", use_container_width=True)

# --- RESULTS LOGIC ---
if run_button:
    if not company_name or not company_url:
        st.error("Please enter both a company name and their website domain (e.g., 'acmecorp.com') to begin the scan.")
    else:
        # Clean the domain
        raw_url = company_url.replace("https://", "").replace("http://", "").replace("www.", "")
        domain = raw_url.split("/")[0].strip()
        
        with st.status(f"Scanning target signals for **{company_name}**...", expanded=True) as status:
            
            st.write(f"Querying Apollo.io for validated `{domain}` demographics & financials...")
            apollo_result = apollo.get_company_data(domain)
            if not apollo_result.get("success"):
                st.error(f"Apollo Fetch Warning: {apollo_result.get('error')}")
                apollo_result = {"success": False, "error": apollo_result.get('error')}
                
            st.write(f"Scraping digital footprint from `{company_url}`...")
            scrape_result = scraper.scrape_website_text(company_url)
            if not scrape_result.get("success"):
                st.warning(f"Web Scrape Warning: {scrape_result.get('error')}")
                
            st.write(f"Hunting global news feeds for exact mentions of `{company_name}`...")
            news_result = news.get_recent_news(company_name)
            
            st.write(f"Executing Deep Web Agent for public SEC filings and Premium News...")
            research_result = researcher.run_deep_research(company_name)
            if not research_result.get("success"):
                st.warning(f"Deep Search Warning: {research_result.get('error')}")
            
            st.write("🧠 Synthesizing data through Gemini Intelligence Engine...")
            ai_evaluation = scorer.evaluate_prospect(
                apollo_data=apollo_result,
                scraped_text=scrape_result.get("text", "No readable text scraped due to error."),
                news_data=news_result.get("articles", []),
                deep_research_text=research_result.get("compiled_text", "")
            )
            
            if not ai_evaluation.get("success"):
                st.error(f"AI Engine Error: {ai_evaluation.get('error')}")
                ai_evaluation = {"total_score": "Error", "talking_points": [], "score_justification": "Failed to generate.", "executive_summary": "Failed to generate.", "historical_trend": "Failed to generate."}
            
            status.update(label="Data Synthesis Complete", state="complete", expanded=False)
            
        st.subheader("Intelligence Report")
        
        exec_summary = ai_evaluation.get("executive_summary", "")
        if exec_summary and isinstance(exec_summary, str) and not exec_summary.startswith("Failed"):
            # Wrapped in safe_md
            st.info(f"**AI Executive Summary (Growth & Markets):** {safe_md(exec_summary)}")
        
        score_col, metrics_col = st.columns([1, 2])
        
        with score_col:
            score = ai_evaluation.get("total_score", "--")
            
            if isinstance(score, int) or str(score).isdigit():
                score_int = int(score)
                delta = "Perfect Match" if score_int >= 85 else ("Moderate Fit" if score_int >= 50 else "Poor Fit")
                delta_color = "normal" if score_int >= 50 else "inverse"
            else:
                score_int = 0
                delta = "Error"
                delta_color = "off"
                
            st.metric(label="Propensity Score", value=score, delta=delta, delta_color=delta_color)
            st.progress(score_int / 100.0 if score_int <= 100 else 1.0)
            st.caption("Score based on size (30%), location (20%), pain signals (15%), HR structure (10%), and culture (25%).")
            
        with metrics_col:
            st.markdown("### Strategic Talking Points")
            talking_points = ai_evaluation.get("talking_points", [])
            if not talking_points:
                st.write("No talking points generated.")
            else:
                for tp in talking_points:
                    st.markdown(f"**{safe_md(tp.get('title', 'Point'))}**  \n{safe_md(tp.get('content', ''))}")
                    
            st.markdown("### 🔗 Cited Sources")
            citations = ai_evaluation.get("citations", [])
            if not citations:
                st.write("No deep research citations mapped.")
            else:
                for c in citations:
                    st.markdown(f"- **[{safe_md(c.get('source', 'Unknown Source'))}]({c.get('url', '#')})**: {safe_md(c.get('insight_extracted', ''))}")
        
        st.divider()
        st.subheader("Deep Dive Context & Raw Notes")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Recent News", 
            "Apollo Demographics", 
            "Financials & Growth",
            "Scraped Web Highlights",
            "AI Evaluation Notes"
        ])
        
        with tab1:
            st.markdown("### Latest Headlines")
            if news_result.get("success"):
                articles = news_result.get("articles", [])
                if not articles:
                    st.info(f"No major recent news events detected for '{company_name}'.")
                else:
                    for art in articles:
                        st.markdown(f"- [{safe_md(art['title'])}]({art['url']})  \n  *(Published: {art['date']})*")
            else:
                st.error(f"Unable to fetch news: {news_result.get('error')}")
                
        with tab2:
            st.markdown(f"**Name:** {safe_md(apollo_result.get('company_name', 'Unknown'))}")
            st.markdown(f"**Employees:** {safe_md(apollo_result.get('employee_count', 'Unknown'))}")
            st.markdown(f"**Location:** {safe_md(apollo_result.get('location', 'Unknown'))}")
            st.markdown(f"**Industry:** {safe_md(apollo_result.get('industry', 'Unknown'))}")
            st.markdown(f"**Description:** {safe_md(apollo_result.get('short_description', 'None provided'))}")
            
        with tab3:
            st.markdown(f"**Founded Year:** {safe_md(apollo_result.get('founded_year', 'Unknown'))}")
            st.markdown(f"**Annual Revenue (Static):** {safe_md(apollo_result.get('annual_revenue', 'Not Disclosed'))}")
            st.markdown(f"**Total Funding:** {safe_md(apollo_result.get('total_funding', 'None/Not Disclosed'))}")
            st.markdown(f"**Latest Funding Stage:** {safe_md(apollo_result.get('latest_funding_stage', 'Unknown'))}")
            
            st.divider()
            st.markdown("### 📊 Historical YoY Growth Trend")
            hist_trend = ai_evaluation.get("historical_trend", "")
            if hist_trend and not hist_trend.startswith("Failed"):
                 st.write(safe_md(hist_trend))
            else:
                 st.write("No historical trend extracted from the deep web.")
                 
            st.caption("*Note: Funding and revenue data is validated by the Apollo.io B2B network. Deep strategic actions (like acquisitions and new markets) are processed dynamically by the AI Engine via live Google News / Web scraping and highlighted in the Executive Summary above.*")
            
        with tab4:
            if scrape_result.get("success"):
                with st.container(height=300):
                    st.write(safe_md(scrape_result.get("text")))
            else:
                st.write("No website scraped text to display.")
                
        with tab5:
            st.markdown("### Evaluator Justification")
            st.write(safe_md(ai_evaluation.get("score_justification", "No justification provided.")))
            
        # --- EXPORT REPORT PIPELINE ---
        if ai_evaluation.get("success"):
            st.divider()
            with st.status("Packaging Reports for Output Suite...", expanded=True) as output_status:
                
                # Excel
                excel_resp = reporter.export_to_excel(
                    company_name=company_name,
                    apollo_data=apollo_result,
                    ai_evaluation=ai_evaluation
                )
                if excel_resp.get("success"):
                    st.success(f"💾 Master Scan tracked natively into `{excel_resp.get('filepath')}`")
                else:
                    st.error(f"Excel Export Error: {excel_resp.get('error')}")
                    
                # Claude / MD Content
                md_resp = reporter.export_to_markdown(
                    company_name=company_name,
                    ai_evaluation=ai_evaluation
                )
                if md_resp.get("success"):
                    st.success(f"📄 Sales Rep generation script saved into `{md_resp.get('filepath')}`")
                else:
                    st.error(f"Markdown Context Error: {md_resp.get('error')}")
                    
                output_status.update(label="Automated Offline Storage Complete", state="complete", expanded=False)
else:
    st.info("👆 Enter a Target Prospect's Name and Domain above to begin the Deep Web Intelligence Sweep.")
