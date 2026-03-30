# 🍁 Alan Canada | AI Sales Intelligence Engine

An automated, locally-hosted Intelligence engine built to aggressively scout, score, and evaluate B2B prospects for **Alan Canada's** digital-first health insurance products.

## 🧠 How It Works
The system ingests a target company domain and simultaneously fires across multiple API vectors:
1. **Apollo.io Foundation**: Scrapes deterministic demographics, headcounts, and verified annual revenue logic.
2. **Tavily AI Deep Web Scraper**: Hunts the public web for premium WSJ/Reuters news and SEC/SEDAR filings highlighting YoY growth.
3. **Google News RSS Engine**: Pulls immediate pain-point signals and PR releases.
4. **Gemini 1.5 Flash Synthesizer**: Ingests all data points and evaluates the company strictly against the **Alan Canada ICP** (5-100 employees, AB/ON locus, proactive HR culture).

Every scan natively generates a comprehensive CRM log tracking the target metrics into a local `Master_Rankings.xlsx` database, while outputting a clean `exports/Claude_Context.md` markdown script ready to be fed into ChatGPT/Claude to automate cold email drafting.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/alan-sales-intel.git
   cd alan-sales-intel
   ```

2. **Initialize the Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure the Environment Array:**
   Rename `.env.example` to `.env` and inject your exact proprietary API keys:
   ```env
   # .env
   GEMINI_API_KEY="your_api_key"
   APOLLO_API_KEY="your_api_key"
   TAVILY_API_KEY="your_api_key"
   ```

4. **Boot the Analytics Server:**
   ```bash
   streamlit run app.py
   ```

## 📊 Sample Reporting Output
We have included a populated `Master_Rankings.xlsx` and `exports/` folder natively inside the repository so you can instantly view exactly what the automated data extraction and target pipeline generates in a production environment.

---
*Built by Antigravity exclusively for Alan Canada Sales Operations.*
