# Alan Canada Sales Research Tool: System Blueprint

## Overview
This document serves as the authoritative blueprint for building the locally hosted Sales Research Tool for the Alan Canada sales team. The tool automates the process of evaluating potential B2B clients for Alan Canada's premium health insurance products.

## 1. Product Context & Target Market (Alan Canada)
- **Product:** Premium health insurance that supplements public healthcare. It features a digital-first experience, 48-hour reimbursements, flexibility in choosing licensed providers (no restricted networks), and includes mental health support and virtual care.
- **Ideal Customer Profile (ICP):**
  - **Company Size:** 5 to 100 employees.
  - **Location:** Alberta (AB) or Ontario (ON).

## 2. Evaluation Metrics & Scoring Strategy
Each researched company is evaluated against 6 key metrics by an AI (OpenAI API). The AI scores the company out of 100 points, assigning weights roughly as follows:

1. **Company Size (Critical - 30%):** Must be exactly between 5 and 100 employees. Outside this range is an automatic severe penalty.
2. **Location (Critical - 20%):** Operations or HQ must be in Alberta or Ontario.
3. **News & Pain Points (15%):** Evidence of recent challenges the company faces, ideally around employee retention, benefits administration, or general scaling pains.
4. **Growth trajectory (10%):** Increase in headcount or recent funding/expansion signals.
5. **HR Signals (10%):** Recent hiring of People Ops, HR Managers, or Benefit Coordinators indicating a scaling team that might need modern benefits.
6. **Benefit Status & Culture (15%):** Mentions of employee wellness, or evidence that they are currently using a clunky legacy provider ("XYZ Insurance") which Alan Canada can replace.

## 3. Technology Stack
The application is built to run entirely locally on the sales rep's machine (macOS/Windows) to keep proprietary sales strategies and prospect lists private.
- **Frontend / UI:** `Streamlit` (A Python framework that generates a beautiful, browser-based UI, running from localhost).
- **Backend / Logic:** `Python 3`
- **Scraping / APIs:**
  - `BeautifulSoup4` & `Requests` (for scraping target websites)
  - `Apollo.io API` (for accurate employee headcount, location, and HR contact presence—bypassing LinkedIn's anti-scraping walls)
  - `DuckDuckGo Search` (or `Tavily`) (to find recent news articles regarding the company)
- **AI Analysis:** `OpenAI Python SDK` (using an API key to evaluate the scraped data against the 6 metrics).
- **Data Export:** `Pandas` and `Openpyxl` (for managing the Master Rankings Excel file).

## 4. System Architecture & Information Flow
When a sales rep inputs a company name and clicks "Research" on the Streamlit dashboard, the following pipeline executes:

### Step 1: Ingestion & Enrichment
- The Python backend accepts the company name/domain.
- Pings the **Apollo.io API** to extract definitive employee size and office locations.
- Pings a search API to find 2-3 recent news events about the company.
- Scrapes the company's "About" and "Careers" pages for cultural and benefits signals.

### Step 2: AI Scoring & Synthesis
- The aggregated text and data points are structured into a prompt and sent to **OpenAI**.
- The AI evaluates the 6 metrics, calculates a score (0-100), and generates 3 strategic sales "Talking Points".

### Step 3: Local File Generation
- **Excel Logging:** The system opens the local `Master_Rankings.xlsx` file, appends the new company's score, employee count, and location. It automatically updates embedded charts (e.g., Score Distribution).
- **The "Claude.md" File:** The absolute raw text scraped, the exact Apollo data, the AI's scoring breakdown, and the suggested talking points are combined into one long markdown document localized at `leads/<CompanyName>/Claude_Context.md`.

### Step 4: AI Sandbox Handoff
- The sales rep takes the generated `Claude_Context.md` file and uploads it into standard Web Claude or ChatGPT.
- The rep prompts the AI: *"Using the attached context, help me write a personalized cold email to their new VP of People Ops regarding their recent expansion in Ontario."*

## 5. Directory Structure
```text
sales_research_tool/
├── app.py                  # The main Streamlit dashboard UI
├── requirements.txt        # Python package dependencies
├── .env                    # Hidden file containing OPENAI_API_KEY and APOLLO_API_KEY
├── modules/
│   ├── scraper.py          # Handles web scraping & news search
│   ├── apollo.py           # Handles communication with the Apollo.io API
│   ├── scorer.py           # Handles sending the data to OpenAI and parsing the score
│   └── reporter.py         # Handles Excel manipulation and Markdown generation
├── data/
│   └── Master_Rankings.xlsx # The central Excel database
└── leads/
    ├── [Company A]/
    │   └── Claude_Context.md
    └── [Company B]/
        └── Claude_Context.md
```

## 6. Execution Phases (For the Developer)
- [ ] **Phase 1: Foundation.** Setup the repository, initialize Streamlit, create `.env.example`, and write the placeholder modules.
- [ ] **Phase 2: Data Hooks.** Implement the Apollo API fetcher and basic web text scraper.
- [ ] **Phase 3: AI Brain.** Craft the precise OpenAI prompt that heavily weights the 5-100 employee rule and AB/ON location requirement.
- [ ] **Phase 4: Output Engine.** Wire up the Pandas Excel exporter and write the template for the `Claude_Context.md` output.
- [ ] **Phase 5: UX Polish.** Connect the Streamlit UI to display spinners, real-time logging, and final results nicely.

---
*Created by Antigravity for Alan Canada Sales Operations.*
