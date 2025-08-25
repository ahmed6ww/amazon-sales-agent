MVP: Agentic Amazon Keyword Research Platform (Personal-use MVP with Helium 10)
One-page summary
An agentic MVP that runs automated research for a single Amazon product (ASIN / product URL), gathers competitor and marketplace signals from Helium 10 APIs, extracts and scores candidate keywords, and produces a prioritized SEO + PPC keyword report and suggested listing copy. Built with Next.js (frontend), FastAPI (backend), and OpenAI Agents SDK (agent orchestration).

Goals & success metrics
Produce a usable keyword list for a single ASIN with: top 50 keywords, top 10 high-priority recommended keywords, and 3 suggested title/bullet text options.
Actionable SEO changes that can be A/B tested (improvement signal: CTR or listing sessions — measured later).
Delivery time for MVP: 7–10 calendar days using Helium 10 API data.
Assumptions
Client sells on Amazon and will provide at least one ASIN and Helium 10 API access (Diamond plan or above) or CSV exports from Cerebro/Magnet tools.
Data is pulled primarily from Helium 10, eliminating the need for scraping or Amazon API access for MVP.

MVP scope (what's included for a fixed-price MVP)
Core features (must-have)
Input screen (frontend): enter ASIN or product URL + marketplace selection.
Research orchestration (agentic flow): controller agent triggers workers to fetch data from Helium 10 APIs.
Data collection (Helium 10 powered):
Cerebro API: reverse ASIN lookup for organic + sponsored keywords.
Magnet API: expand keyword set with related, high-volume keywords.
Keyword aggregation & deduplication: combine Cerebro + Magnet results.
Keyword scoring: based on Helium 10 search volume, relevancy, and competition data.
Report output: downloadable CSV + simple UI table showing top keywords, scores, and 3 suggested title/bullet variants.
Basic logging, simple DB (Postgres or SQLite for MVP), and minimal auth for client access.
Out of scope for MVP (can be upsold):
Continuous monitoring & scheduled scans
Full multi-ASIN/bulk uploads
Rank tracking

Architecture (high level)
Frontend: Next.js single-page app. One product input page + report UI.
Backend: FastAPI exposing endpoints to trigger research and fetch reports.
Agent Layer: OpenAI Agents SDK orchestrates these steps (Research Agent → Keyword Agent → Scoring Agent → SEO Agent).
Database: Postgres (preferred) or SQLite for MVP.
Queue: FastAPI background tasks.
Data Source: Helium 10 APIs.

Data sources (Helium 10)
Cerebro — reverse ASIN keyword lookup.
Magnet — keyword discovery from seed keywords.
Helium 10 keyword metrics — search volume, CPR, relevancy score, competing products.

Agentic workflow (detailed)
Trigger: user submits ASIN/product URL.
Research Agent: sends API requests to Helium 10’s Cerebro & Magnet endpoints.
Keyword Agent: merges and cleans the combined keyword list.
Scoring Agent: ranks keywords by Helium 10’s search volume, relevancy, and competition.
SEO Agent: outputs top-K ranked keywords, suggested title + 3 bullet variants.
Report Generator: create CSV + UI table.

Acceptance criteria / Deliverables
Single-product research run returning: top 50 candidate keywords, top 10 prioritized, CSV export, and 3 title/bullet suggestions.
Working demo of input → Helium 10 API calls → scored keyword output.
Deployed backend (staging) and README.



How to get reliable stats (with Helium 10)
Reverse ASIN (Cerebro): shows all organic + sponsored keywords the product ranks for.
Keyword Discovery (Magnet): expands keyword list with high-volume terms.
Metrics: search volume, relevancy, competing products for scoring.

Next meeting checklist
Confirm client Helium 10 plan & API access.
Confirm marketplaces.
Risks & mitigations
API limits: Ensure plan covers needed calls.
Data scope: Limited to what Helium 10 returns.

Handoff
1-week bugfix support.
Optional maintenance plan.

MVP Specification – Agentic Amazon Keyword Research Platform
(Personal-use MVP with Helium 10)

1. Objective
Build an autonomous keyword research MVP that:
Accepts a single Amazon product (ASIN or product URL) and marketplace selection.


Accepts the Helium10 cerebro reverse ASIN sheets.

a) Top 10 competitors with high revenue
b) Top 10 relevant design competitors


Scores and categorizes keywords using predefined logic.


Produces:


SEO Comparison (current vs improved listing).


Full categorized keyword dataset with Helium 10 metrics and root-level search volume analysis.



2. MVP Scope (In-Scope for v1)
Core Features
Input Screen


User inputs ASIN or product URL.


Select the marketplace.


Inputs Helium10 cerebro reverse ASIN files. 
a) Top 10 revenue generating competitors (either provide first ASIN manually as input or no need to provide that if your product URL is used as first input ASIN as Helium10 does not give first ASIN)
b) Top 10 relevant design competitors (either provide first ASIN manually as input or no need to provide that if your product URL is used as first input ASIN as Helium10 does not give first ASIN)


Competitor Selection Logic


Apply a couple of filters on the keyword data CSV file
On the given URL, we need to fetch attributes from the listing and make a list of that. The source will be title, images, A+ content, reviews, Question Answer section.  


We need to filter out the position of a given product URL in the market as compared to other offers. Does it come under budget products or premium products?

https://sharing.clickup.com/clip/p/t9018080885/5db0c195-89fa-464e-affd-c8c2ec6ff0f5/5db0c195-89fa-464e-affd-c8c2ec6ff0f5.webm?filename=screen-recording-2025-08-21-15%3A01.webm

 
We need to define main keyword (or we can also take it as input)

https://sharing.clickup.com/clip/p/t9018080885/1658fac3-7d6f-4213-8588-c369d2ad9e23/1658fac3-7d6f-4213-8588-c369d2ad9e23.webm?filename=screen-recording-2025-08-21-15%3A20.webm


Relevancy formula. =countif(range, filter). (It helps to give relevancy to the keywords. The formula shows that for a keyword, how many competitors are ranked in less than 10 ranks or top 10 organic ranks. If relevant competitors are ranked on a keyword, it means they are generating sales from that keyword so the keyword must be relevant.)

https://sharing.clickup.com/clip/p/t9018080885/6e9e7712-e329-49d4-a8a1-ed2522005568/6e9e7712-e329-49d4-a8a1-ed2522005568.webm?filename=screen-recording-2025-08-21-15%3A44.webm


Rules for relevancy.

1. Literal meaning of the keywords is the first criteria to see if a keyword is relevant or not.
2. The second rule is to see relevancy (as explained in above video). If many relevant designs are ranked on a keyword but literal meaning does not make it relevant for us then we will incline towards relevancy. Eg, changing table for dresser does not look like a relevant keyword for changing pad from literal meaning but from relevancy score, 7-8 relevant design competitors are ranked so we will be inclined towards the decision that this keyword is relevant. Final confirmation is always when we search that keyword in amazon search result. If it shows 6 out of 10 or more than that relevant designs on the keyword in organic positions then it is a relevant keyword.

Note: We always need to change the zip code of location on amazon website according to the relevant country. Otherwise, it will show irrelevant results.  




Keyword Processing


Categorize keywords into:


Relevant - License Plate Frame


Design-Specific - Silicone License Plate Frame  


Irrelevant - Stainless Steel , License Plate


Branded (own & competitors) - Sunplus Trade, Levis

https://sharing.clickup.com/clip/p/t9018080885/fe5333ad-6fc8-4644-aac8-c882249c3542/fe5333ad-6fc8-4644-aac8-c882249c3542.webm?filename=screen-recording-2025-08-21-16%3A06.webm


Keywords sorted by intent (0–3)


Sort within categories by title density (from Helium 10).




Scoring & Prioritization


Intent scoring:


0 = Irrelevant intent


1 = One relevant intent


2 = Two relevant intents


3 = Three relevant intents


Broad search volume calculation by root word (sum of all relevant keywords with the same root).

https://sharing.clickup.com/clip/p/t9018080885/c89253f2-4889-43fa-855c-9029180bf285/c89253f2-4889-43fa-855c-9029180bf285.webm?filename=screen-recording-2025-08-21-16%3A19.webm



Include title density, search volume, relevancy score, CPR, and competition data from Helium 10.


Zero title density indicates 2 things. Either the keyword is not relevant, that's why no one has used that keyword in the title. Or that keyword is singular / plural or misspel of a main high search volume keyword. We ignore keywords from both of these categories. But if keywords are not derivative or similar to any main keyword, has its own root word (like mattress we saw in last video) and is not used in the title then that is a decent opportunity. 

https://sharing.clickup.com/clip/p/t9018080885/e76c667e-eeb4-4716-8b88-88cd7faeee51/e76c667e-eeb4-4716-8b88-88cd7faeee51.webm?filename=screen-recording-2025-08-21-16%3A15.webm



Gap Analysis


Highlight relevant keywords not covered in current listing copy.


Identify features/attributes with low keyword coverage.


Clarification Flow


If product attributes are unclear from listing/images, prompt the user with targeted questions.



3. Output
A. SEO Comparison Table
Left Side: Existing SEO of listing (title, bullets, backend keywords) + keyword coverage metrics.


Right Side: Suggested SEO improvements that:


Cover all relevant keyword roots.


Use higher-intent keywords where possible.


Replace lower-volume terms with better search volume options.


B. Categorized Keyword Dataset
Delivered as a separate tab in UI and downloadable CSV.


Categories:


Relevant Keywords


Irrelevant Keywords


Design-Specific Keywords


Branded Keywords


Keywords sorted by intent


Broad Search Volume for its root keyword (aggregated)


Each keyword entry includes:
Search Volume


Relevancy Score


Title Density


CPR (Cerebro Product Rank)


Competition metrics (if available)






4. Out of Scope (v1)
Bulk/multi-ASIN research.


Continuous monitoring/scheduled scans.


Rank tracking.


Full POE/bid cost estimation from SP-API (possible v1.1 extension).


Magnet API integration.



5. Technical Requirements
Frontend: Next.js (single-page app – input + report).


Backend: FastAPI.


Agent Orchestration: OpenAI Agents SDK (Research Agent → Keyword Agent → Scoring Agent → SEO Agent).


Database: Postgres (preferred) or SQLite for MVP.


Hosting: Developer’s choice (must support background tasks).


Queue: FastAPI background tasks or equivalent.


Data Source: Helium 10 Cerebro API.


Auth: Minimal login for client.



6. Acceptance Criteria
User inputs ASIN → system produces full keyword list (up to 500 finalized keywords).


Keywords categorized & scored per defined rules.


CSV download works without data loss.


SEO Comparison table clearly shows existing vs improved listing.


Categorized keyword dataset includes all required Helium 10 metrics plus broad search volume for each keyword root.


Works for at least one marketplace in Helium 10.


Processing time: <2 minutes per run.



7. Risks & Mitigation
API Limits: Confirm Helium 10 plan covers daily call volume.


Data Scope: Limited to Helium 10 dataset accuracy.


Logic Complexity: Attribute extraction from listing may require manual fallback questions to user.



8. Handoff & Support
Code in shared GitHub repo with README.


1-week bug-fix support post-delivery.


Optional maintenance plan to be discussed.

