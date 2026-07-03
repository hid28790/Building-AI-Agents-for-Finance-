# Step 4 — Router query engine

_An LLMSingleSelector picks exactly one per-document tool per query._

## Q: What is the firm's minimum required quick ratio for a new long position?

### Retrieved context (1 chunk(s))

**Chunk 1** — source `firm_risk_policy.md`, score 0.511

> # Birchwood Asset Management — Counterparty & Liquidity Risk Policy (Excerpt)
> 
> > *Synthetic internal policy document created for the Agentic RAG lab. Birchwood
> > Asset Management is a fictional firm; thresholds are illustrative and not
> > investment advice.*
> 
> **Policy ID:** RISK-LIQ-007
> **Owner:** Office of the Chief Risk Officer
> **Last reviewed:** March 2025
> 
> ## 1. Purpose
> 
> This policy defines the minimum liquidity standards that an issuer must satisfy
> before the firm may hold a long position in its equity or unsecured debt. It applies
> to all actively managed portfolios.
> 
> ## 2. Liquidity thresholds
> 
> For any issuer classified as **non-financial corporate**, the analyst must verify,
> using the issuer's most recent annual report, that:
> 
> - **Current ratio ≥ 1.50.** Issuers with a current ratio below 1.50 require a
>   documented exception approved by the Risk Committee.
> - **Quick ratio ≥ 1.00.** A quick ratio below 1.00 is a **hard block**: no new long
>   position may be opened regardless of other factors.
> - **Net-debt-to-EBITDA ≤ 3.5x.**
> 
> ## 3. Covenant awareness
> 
> Where an issuer discloses financial covenants on its credit facilities, the analyst
> must record the covenant thresholds and confirm the issuer's current headroom.
> Approaching a covenant (within 10% of the threshold) must be flagged in the position
> memo even if the policy thresholds above are met.
> 
> ## 4. Concentration
> 
> No single issuer may exceed **5% of portfolio net asset value** at cost. Issuers
> whose own customer concentration exceeds 40% of revenue are flagged as
> **elevated single-name risk** and are capped at **3% of NAV**.
> 
> ## 5. Documentation
> 
> Every position memo must cite the specific figures used to evaluate Sections 2–4 and
> name the source document and reporting period. Unsupported assertions are not
> acceptable; if a required figure cannot be found in the issuer's disclosures, the
> analyst must state that explicitly rather than estimate.

### Answer

Based on the firm's risk policy, the minimum required quick ratio for a new long position is **1.00**. This is treated as a **hard block** — meaning that if an issuer's quick ratio falls below 1.00, no new long position may be opened, regardless of any other factors. There is no exception process available for this threshold, unlike the current ratio requirement of 1.50, which can be waived with Risk Committee approval.

---

## Q: What was Acme's Q3 quick ratio?

### Retrieved context (1 chunk(s))

**Chunk 1** — source `acme_earnings_call_q3.md`, score 0.500

> # Acme Robotics, Inc. — Q3 Fiscal 2024 Earnings Call Transcript (Excerpt)
> 
> > *Synthetic transcript created for the Agentic RAG lab. Acme Robotics, Inc. is a
> > fictional company; quotes are illustrative.*
> 
> **Date:** October 24, 2024
> **Participants:** Jordan Ellis (Chief Executive Officer), Priya Nair (Chief
> Financial Officer), and analysts.
> 
> ---
> 
> **Operator:** Good afternoon, and welcome to Acme Robotics' third-quarter fiscal
> 2024 earnings call. I will now turn the call over to CEO Jordan Ellis.
> 
> **Jordan Ellis (CEO):** Thank you. We had a strong quarter. Revenue came in at
> **$162 million**, up 21% year over year, and we are especially pleased that
> Software & Services reached an all-time high of **$52 million**, now a third of the
> business. Customer demand for warehouse automation remains robust heading into the
> holiday peak.
> 
> **Priya Nair (CFO):** Thanks, Jordan. A few financial highlights. Gross margin in
> the quarter was **43.5%**, up roughly 300 basis points year over year, again driven
> by software mix. We ended the quarter with **$121 million** in cash. I want to
> flag that our **quick ratio dipped to 1.18 at the end of Q3**, down from about 1.25
> at the start of the year, as we deliberately built inventory ahead of the holiday
> season and ahead of a planned LiDAR supplier transition. We expect inventories to
> normalize by year end, bringing the quick ratio back above 1.2.
> 
> ---
> 
> ### Q&A
> 
> **Analyst (Morgan Healy, Cedar Capital):** Priya, can you talk about the inventory
> build and what it means for your liquidity covenants?
> 
> **Priya Nair (CFO):** Sure. The covenant that matters here is the **current ratio
> floor of 1.25** on our revolving facility. Our current ratio remains well above
> that — it was about **1.6** at the end of Q3. The quick-ratio softness is a timing
> issue tied to inventory; it is not a covenant metric, and we have ample headroom.
> 
> **Analyst (Sam Okafor, Birchwood Research):** On guidance — are you raising the
> full-year outlook?
> 
> **Jordan Ellis (CEO):** We are nudging the top end up. We now expect full-year
> revenue of **$605 million to $615 million**. The Software & Services momentum gives
> us confidence.
> 
> **Analyst (Morgan Healy, Cedar Capital):** And the LiDAR supplier transition — any
> risk to Q4 shipments?
> 
> **Jordan Ellis (CEO):** We have dual-sourced the next-generation module and built a
> buffer stock, which is part of why inventory is elevated. We do not expect a
> material shipment impact in Q4.
> 
> **Operator:** That concludes today's call. Thank you for joining.

### Answer

Acme Robotics' quick ratio dipped to **1.18** at the end of Q3 fiscal 2024, down from approximately 1.25 at the start of the year. This decline was attributed to a deliberate inventory build ahead of the holiday season and a planned LiDAR supplier transition. The company expects inventories to normalize by year end, which should bring the quick ratio back above 1.2.

---

## Q: What credit-facility covenants does Acme disclose in its 10-K?

### Retrieved context (1 chunk(s))

**Chunk 1** — source `acme_10k_excerpt.md`, score 0.524

> # Acme Robotics, Inc. — Form 10-K (Excerpt)
> 
> **Fiscal Year Ended December 31, 2024**
> 
> > *This is a synthetic, illustrative excerpt created for the Agentic RAG lab. Acme
> > Robotics, Inc. is a fictional company. None of the figures below represent a real
> > filing.*
> 
> ## Item 1. Business
> 
> Acme Robotics, Inc. ("Acme," "we," or "the Company") designs, manufactures, and
> sells industrial warehouse-automation robots and the accompanying fleet-management
> software. Our two reportable segments are **Hardware** (autonomous mobile robots,
> or AMRs) and **Software & Services** (the AcmeFleet subscription platform). We sell
> primarily to large third-party logistics providers and e-commerce fulfillment
> operators in North America and Western Europe.
> 
> ## Item 1A. Risk Factors (Selected)
> 
> - **Customer concentration.** Our three largest customers accounted for 41% of
>   total revenue in fiscal 2024. The loss of any one of them would materially harm
>   our results.
> - **Supply chain.** We source high-precision LiDAR modules from a single supplier
>   in Taiwan. A disruption would delay hardware shipments.
> - **Liquidity and covenants.** Our revolving credit facility requires us to
>   maintain a current ratio of at least 1.25 and a maximum net-debt-to-EBITDA ratio
>   of 3.0. A breach could accelerate repayment.
> 
> ## Item 7. Management's Discussion and Analysis (MD&A)
> 
> ### Results of operations
> 
> Total revenue for fiscal 2024 was **$612.4 million**, up 18% from $519.0 million in
> fiscal 2023. Software & Services revenue grew 34% year over year and reached
> **$188.7 million**, or 31% of total revenue, reflecting continued adoption of the
> AcmeFleet platform. Gross margin expanded to **43.1%** from 40.2%, driven by the
> higher software mix.
> 
> Operating income was **$71.3 million** (11.6% operating margin), and net income was
> **$48.9 million**, or **$1.92 per diluted share**.
> 
> ### Liquidity and capital resources
> 
> As of December 31, 2024, we held **$132.0 million** in cash and cash equivalents.
> Selected balance-sheet items (in millions):
> 
> | Item                     | FY2024 | FY2023 |
> |--------------------------|-------:|-------:|
> | Current assets           |  410.0 |  351.0 |
> | Inventories              |   96.0 |   72.0 |
> | Current liabilities      |  255.0 |  240.0 |
> | Total debt               |  180.0 |  165.0 |
> | Shareholders' equity     |  402.0 |  351.0 |
> 
> The Company's **current ratio** at fiscal year-end 2024 was **1.61** (410.0 / 255.0),
> comfortably above the 1.25 covenant threshold. Our **quick ratio**, which excludes
> inventories, was **1.23** ((410.0 − 96.0) / 255.0).
> 
> We believe existing cash, cash flow from operations, and availability under our
> revolving credit facility are sufficient to meet our liquidity needs for at least
> the next twelve months.
> 
> ### Outlook
> 
> For fiscal 2025, management expects total revenue between **$700 million and $730
> million**, with Software & Services growing faster than Hardware. We expect capital
> expenditures of approximately $40 million, primarily for expansion of our Ohio
> manufacturing facility.

### Answer

## Acme Robotics Credit Facility Covenants

Acme Robotics discloses **two specific financial covenants** associated with its revolving credit facility:

1. **Minimum Current Ratio of 1.25** — The company must maintain a current ratio of at least 1.25 at all times. A breach of this threshold could trigger accelerated repayment of the facility.

2. **Maximum Net-Debt-to-EBITDA Ratio of 3.0** — The company's net debt relative to EBITDA must not exceed 3.0x. Similarly, a breach could accelerate repayment obligations.

### Acme's Compliance Status (as of December 31, 2024)
As of fiscal year-end 2024, Acme was **comfortably in compliance** with the current ratio covenant, reporting a current ratio of **1.61** (calculated as $410.0M current assets ÷ $255.0M current liabilities), which is well above the 1.25 minimum threshold.

The filing does not explicitly state the company's net-debt-to-EBITDA ratio for the period, though no covenant breach is indicated.

> **Note:** The company flags these covenants as a liquidity risk factor, warning that a breach of either threshold could result in accelerated repayment of the revolving credit facility.

---

## Q: Does Acme's Q3 quick ratio satisfy the firm's risk policy?

### Retrieved context (2 chunk(s))

**Chunk 1** — source `acme_earnings_call_q3.md`, score 0.443

> # Acme Robotics, Inc. — Q3 Fiscal 2024 Earnings Call Transcript (Excerpt)
> 
> > *Synthetic transcript created for the Agentic RAG lab. Acme Robotics, Inc. is a
> > fictional company; quotes are illustrative.*
> 
> **Date:** October 24, 2024
> **Participants:** Jordan Ellis (Chief Executive Officer), Priya Nair (Chief
> Financial Officer), and analysts.
> 
> ---
> 
> **Operator:** Good afternoon, and welcome to Acme Robotics' third-quarter fiscal
> 2024 earnings call. I will now turn the call over to CEO Jordan Ellis.
> 
> **Jordan Ellis (CEO):** Thank you. We had a strong quarter. Revenue came in at
> **$162 million**, up 21% year over year, and we are especially pleased that
> Software & Services reached an all-time high of **$52 million**, now a third of the
> business. Customer demand for warehouse automation remains robust heading into the
> holiday peak.
> 
> **Priya Nair (CFO):** Thanks, Jordan. A few financial highlights. Gross margin in
> the quarter was **43.5%**, up roughly 300 basis points year over year, again driven
> by software mix. We ended the quarter with **$121 million** in cash. I want to
> flag that our **quick ratio dipped to 1.18 at the end of Q3**, down from about 1.25
> at the start of the year, as we deliberately built inventory ahead of the holiday
> season and ahead of a planned LiDAR supplier transition. We expect inventories to
> normalize by year end, bringing the quick ratio back above 1.2.
> 
> ---
> 
> ### Q&A
> 
> **Analyst (Morgan Healy, Cedar Capital):** Priya, can you talk about the inventory
> build and what it means for your liquidity covenants?
> 
> **Priya Nair (CFO):** Sure. The covenant that matters here is the **current ratio
> floor of 1.25** on our revolving facility. Our current ratio remains well above
> that — it was about **1.6** at the end of Q3. The quick-ratio softness is a timing
> issue tied to inventory; it is not a covenant metric, and we have ample headroom.
> 
> **Analyst (Sam Okafor, Birchwood Research):** On guidance — are you raising the
> full-year outlook?
> 
> **Jordan Ellis (CEO):** We are nudging the top end up. We now expect full-year
> revenue of **$605 million to $615 million**. The Software & Services momentum gives
> us confidence.
> 
> **Analyst (Morgan Healy, Cedar Capital):** And the LiDAR supplier transition — any
> risk to Q4 shipments?
> 
> **Jordan Ellis (CEO):** We have dual-sourced the next-generation module and built a
> buffer stock, which is part of why inventory is elevated. We do not expect a
> material shipment impact in Q4.
> 
> **Operator:** That concludes today's call. Thank you for joining.

**Chunk 2** — source `firm_risk_policy.md`, score 0.562

> # Birchwood Asset Management — Counterparty & Liquidity Risk Policy (Excerpt)
> 
> > *Synthetic internal policy document created for the Agentic RAG lab. Birchwood
> > Asset Management is a fictional firm; thresholds are illustrative and not
> > investment advice.*
> 
> **Policy ID:** RISK-LIQ-007
> **Owner:** Office of the Chief Risk Officer
> **Last reviewed:** March 2025
> 
> ## 1. Purpose
> 
> This policy defines the minimum liquidity standards that an issuer must satisfy
> before the firm may hold a long position in its equity or unsecured debt. It applies
> to all actively managed portfolios.
> 
> ## 2. Liquidity thresholds
> 
> For any issuer classified as **non-financial corporate**, the analyst must verify,
> using the issuer's most recent annual report, that:
> 
> - **Current ratio ≥ 1.50.** Issuers with a current ratio below 1.50 require a
>   documented exception approved by the Risk Committee.
> - **Quick ratio ≥ 1.00.** A quick ratio below 1.00 is a **hard block**: no new long
>   position may be opened regardless of other factors.
> - **Net-debt-to-EBITDA ≤ 3.5x.**
> 
> ## 3. Covenant awareness
> 
> Where an issuer discloses financial covenants on its credit facilities, the analyst
> must record the covenant thresholds and confirm the issuer's current headroom.
> Approaching a covenant (within 10% of the threshold) must be flagged in the position
> memo even if the policy thresholds above are met.
> 
> ## 4. Concentration
> 
> No single issuer may exceed **5% of portfolio net asset value** at cost. Issuers
> whose own customer concentration exceeds 40% of revenue are flagged as
> **elevated single-name risk** and are capped at **3% of NAV**.
> 
> ## 5. Documentation
> 
> Every position memo must cite the specific figures used to evaluate Sections 2–4 and
> name the source document and reporting period. Unsupported assertions are not
> acceptable; if a required figure cannot be found in the issuer's disclosures, the
> analyst must state that explicitly rather than estimate.

### Answer

## Acme's Q3 Quick Ratio vs. Firm Risk Policy

Based on the available information, here is the assessment:

### Key Figures
- **Q3 Quick Ratio:** 1.18
- **Hard Block Threshold:** Quick ratio < 1.00
- **Exception Threshold:** Quick ratio between 1.00–1.50 requires a documented Risk Committee exception if current ratio falls below 1.50
- **Q3 Current Ratio:** ~1.60

### Policy Compliance Assessment

**The Q3 quick ratio of 1.18 does satisfy the hard block requirement**, as it remains above the 1.00 floor. No automatic block on new long positions is triggered.

However, since the quick ratio of 1.18 falls within the **1.00–1.50 range**, this would ordinarily require a **documented exception approved by the Risk Committee** — *unless* the current ratio is at or above 1.50. Given that Acme's Q3 current ratio is approximately **1.60**, which exceeds the 1.50 threshold, this exception requirement may not be triggered.

### Important Caveats
1. The firm's risk policy specifies that figures must be sourced from the issuer's **most recent annual report**, not necessarily a quarterly filing. The 1.18 figure comes from a quarterly disclosure, which may not satisfy the policy's documentation standard.
2. Analysts are required to **explicitly cite the source document, figure, and reporting period** in the position memo.

### Bottom Line
The Q3 quick ratio of 1.18 **does not trigger a hard block**, and the current ratio of ~1.60 appears to preclude the need for a Risk Committee exception. However, **source documentation compliance must be verified** before a final determination can be made.

---
