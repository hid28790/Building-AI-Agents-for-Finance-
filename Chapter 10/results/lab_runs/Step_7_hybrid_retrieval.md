# Step 7 — Hybrid dense + sparse retrieval

_A dense vector retriever and a BM25 sparse retriever over the same nodes, fused with reciprocal rank fusion._

## Q: Does Acme's Q3 quick ratio satisfy the firm's risk policy?

### Retrieved context (3 chunk(s))

**Chunk 1** — source `firm_risk_policy.md`, score 0.033

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

**Chunk 2** — source `acme_10k_excerpt.md`, score 0.033

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

**Chunk 3** — source `acme_earnings_call_q3.md`, score 0.033

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

## Analysis: Acme's Q3 Quick Ratio vs. Firm Risk Policy

**Short answer: Yes, the Q3 quick ratio satisfies the policy minimum — but it warrants monitoring.**

---

### The Relevant Figures

| Metric | Value | Source |
|---|---|---|
| Acme Q3 2024 quick ratio | **1.18** | Q3 Earnings Call (Oct 24, 2024) |
| Firm policy hard block threshold | **< 1.00** | RISK-LIQ-007, Section 2 |
| Firm policy exception threshold | **< 1.00** (hard block only for quick ratio) | RISK-LIQ-007, Section 2 |

---

### Assessment

The firm's risk policy sets a **hard block at a quick ratio below 1.00** — meaning no new long position may be opened if the quick ratio falls under that level. Acme's Q3 quick ratio of **1.18 clears this hard block threshold**, so it does not trigger an automatic prohibition.

However, two additional considerations are relevant:

1. **Directional trend:** The quick ratio declined from approximately 1.25 at the start of the year to 1.18 at Q3-end, driven by a deliberate inventory build. CFO Priya Nair indicated this is a timing issue and expected normalization by year-end — which the FY2024 10-K confirms, with the year-end quick ratio recovering to **1.23**.

2. **Covenant awareness (Policy Section 3):** While the quick ratio is not itself a covenant metric for Acme's credit facility, the analyst should confirm headroom on the covenants that *are* in place (current ratio ≥ 1.25 and net-debt-to-EBITDA ≤ 3.0x) and document them in the position memo accordingly.

---

### Conclusion

The Q3 quick ratio of 1.18 **does not trigger the hard block**, but the position memo must cite this specific figure, its source (Q3 earnings call, October 24, 2024), and note the downward trend as a matter of diligence under the policy's documentation requirements.

---
