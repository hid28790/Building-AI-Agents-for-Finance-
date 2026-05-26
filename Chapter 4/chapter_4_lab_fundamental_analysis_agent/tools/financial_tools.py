"""
financial_tools.py
------------------
Tools for fetching and processing financial statements using yfinance.
All tools use the @function_tool decorator from the OpenAI Agents SDK.
"""

import json
import yfinance as yf
import pandas as pd
from agents import function_tool
from tools import cache as _cache


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _safe_float(value) -> float | None:
    """Convert a value to float, returning None if not possible."""
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _millions(value) -> float | None:
    """Convert a value to millions, rounded to 2 decimal places."""
    v = _safe_float(value)
    return round(v / 1_000_000, 2) if v is not None else None


def _extract_row(df: pd.DataFrame, *row_names: str, col) -> float | None:
    """Try multiple row name variants and return the first match."""
    for name in row_names:
        try:
            if name in df.index:
                return _millions(df.loc[name, col])
        except (KeyError, TypeError):
            continue
    return None


# ---------------------------------------------------------------------------
# Tool 1: Income Statement
# ---------------------------------------------------------------------------

@function_tool
def get_income_statement(ticker: str) -> str:
    """
    Fetch the annual income statement for a given stock ticker.

    Returns revenue, gross profit, operating income, EBITDA, net income,
    and EPS for the last 4 fiscal years. All monetary values are in millions USD.

    Args:
        ticker: The stock ticker symbol, e.g. 'AAPL', 'MSFT', 'GOOGL'.
    """
    _key = ("get_income_statement", ticker.upper())
    _hit = _cache.get(_key)
    if _hit is not None:
        return _hit
    try:
        stock = yf.Ticker(ticker.upper())
        fin = stock.financials  # columns = fiscal year end dates

        if fin is None or fin.empty:
            return json.dumps({"error": f"No income statement data found for {ticker}"})

        currency = stock.info.get("financialCurrency", "USD")
        result: dict = {
            "ticker": ticker.upper(),
            "company_name": stock.info.get("longName", ticker.upper()),
            "currency": currency,
            "unit": f"millions {currency}",
            "annual_data": {},
        }

        for col in fin.columns[:4]:
            year = str(col.year)
            result["annual_data"][year] = {
                "revenue":          _extract_row(fin, "Total Revenue", col=col),
                "gross_profit":     _extract_row(fin, "Gross Profit", col=col),
                "operating_income": _extract_row(fin, "Operating Income", "EBIT", col=col),
                "ebitda":           _extract_row(fin, "EBITDA", col=col),
                "net_income":       _extract_row(fin, "Net Income", col=col),
                "r_and_d":          _extract_row(fin, "Research And Development", col=col),
            }

        info = stock.info
        result["eps_ttm"]         = _safe_float(info.get("trailingEps"))
        result["eps_forward"]     = _safe_float(info.get("forwardEps"))
        result["revenue_ttm_M"]   = _millions(info.get("totalRevenue"))
        result["gross_margin_pct"] = _safe_float(info.get("grossMargins", 0)) and round(info.get("grossMargins", 0) * 100, 2)
        result["operating_margin_pct"] = round(info.get("operatingMargins", 0) * 100, 2) if info.get("operatingMargins") else None
        result["net_margin_pct"]  = round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else None

        output = json.dumps(result, indent=2, default=str)
        _cache.store(_key, output)
        return output

    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


# ---------------------------------------------------------------------------
# Tool 2: Balance Sheet
# ---------------------------------------------------------------------------

@function_tool
def get_balance_sheet(ticker: str) -> str:
    """
    Fetch the annual balance sheet for a given stock ticker.

    Returns total assets, total liabilities, shareholders' equity, cash,
    total debt, and working capital for the last 4 fiscal years.
    All monetary values are in millions USD.

    Args:
        ticker: The stock ticker symbol, e.g. 'AAPL', 'MSFT', 'GOOGL'.
    """
    _key = ("get_balance_sheet", ticker.upper())
    _hit = _cache.get(_key)
    if _hit is not None:
        return _hit
    try:
        stock = yf.Ticker(ticker.upper())
        bs = stock.balance_sheet

        if bs is None or bs.empty:
            return json.dumps({"error": f"No balance sheet data found for {ticker}"})

        currency = stock.info.get("financialCurrency", "USD")
        result: dict = {
            "ticker": ticker.upper(),
            "currency": currency,
            "unit": f"millions {currency}",
            "annual_data": {},
        }

        for col in bs.columns[:4]:
            year = str(col.year)
            total_assets = _extract_row(bs, "Total Assets", col=col)
            total_liab   = _extract_row(bs, "Total Liabilities Net Minority Interest", "Total Liab", col=col)
            current_assets = _extract_row(bs, "Current Assets", col=col)
            current_liab   = _extract_row(bs, "Current Liabilities", col=col)
            working_capital = (
                round(current_assets - current_liab, 2)
                if current_assets is not None and current_liab is not None
                else None
            )

            result["annual_data"][year] = {
                "total_assets":             total_assets,
                "total_liabilities":        total_liab,
                "shareholders_equity":      _extract_row(bs, "Stockholders Equity", col=col),
                "cash_and_equivalents":     _extract_row(bs, "Cash And Cash Equivalents", "Cash", col=col),
                "total_debt":               _extract_row(bs, "Total Debt", col=col),
                "long_term_debt":           _extract_row(bs, "Long Term Debt", col=col),
                "current_assets":           current_assets,
                "current_liabilities":      current_liab,
                "working_capital":          working_capital,
                "goodwill_and_intangibles": _extract_row(bs, "Goodwill And Other Intangible Assets", "Goodwill", col=col),
            }

        info = stock.info
        result["market_cap_M"]   = _millions(info.get("marketCap"))
        result["book_value_per_share"] = _safe_float(info.get("bookValue"))

        output = json.dumps(result, indent=2, default=str)
        _cache.store(_key, output)
        return output

    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


# ---------------------------------------------------------------------------
# Tool 3: Cash Flow Statement
# ---------------------------------------------------------------------------

@function_tool
def get_cash_flow_statement(ticker: str) -> str:
    """
    Fetch the annual cash flow statement for a given stock ticker.

    Returns operating cash flow, capital expenditures, free cash flow,
    and financing activities for the last 4 fiscal years.
    All monetary values are in millions USD.

    Args:
        ticker: The stock ticker symbol, e.g. 'AAPL', 'MSFT', 'GOOGL'.
    """
    _key = ("get_cash_flow_statement", ticker.upper())
    _hit = _cache.get(_key)
    if _hit is not None:
        return _hit
    try:
        stock = yf.Ticker(ticker.upper())
        cf = stock.cashflow

        if cf is None or cf.empty:
            return json.dumps({"error": f"No cash flow data found for {ticker}"})

        currency = stock.info.get("financialCurrency", "USD")
        result: dict = {
            "ticker": ticker.upper(),
            "currency": currency,
            "unit": f"millions {currency}",
            "annual_data": {},
        }

        for col in cf.columns[:4]:
            year = str(col.year)
            op_cf  = _extract_row(cf, "Operating Cash Flow", "Total Cash From Operating Activities", col=col)
            capex  = _extract_row(cf, "Capital Expenditure", "Capital Expenditures", col=col)

            # Free cash flow = operating cash flow - capex
            # capex in financial statements is typically negative
            if op_cf is not None and capex is not None:
                fcf = round(op_cf + capex, 2)  # capex already negative
            else:
                fcf = None

            result["annual_data"][year] = {
                "operating_cash_flow":    op_cf,
                "capital_expenditure":    capex,
                "free_cash_flow":         fcf,
                "investing_cash_flow":    _extract_row(cf, "Investing Cash Flow", "Total Cashflows From Investing Activities", col=col),
                "financing_cash_flow":    _extract_row(cf, "Financing Cash Flow", "Total Cash From Financing Activities", col=col),
                "dividends_paid":         _extract_row(cf, "Common Stock Dividend Paid", "Dividends Paid", col=col),
                "share_repurchases":      _extract_row(cf, "Repurchase Of Capital Stock", "Repurchase Of Common Stock", col=col),
            }

        output = json.dumps(result, indent=2, default=str)
        _cache.store(_key, output)
        return output

    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


# ---------------------------------------------------------------------------
# Tool 4: Key Ratios
# ---------------------------------------------------------------------------

@function_tool
def compute_key_ratios(ticker: str) -> str:
    """
    Compute key fundamental ratios for a given stock ticker.

    Calculates valuation ratios (P/E, P/B, P/S, EV/EBITDA), profitability
    ratios (ROE, ROIC, net margin), leverage ratios (Debt/Equity, interest
    coverage), and growth metrics (revenue YoY, EPS YoY).

    Args:
        ticker: The stock ticker symbol, e.g. 'AAPL', 'MSFT', 'GOOGL'.
    """
    _key = ("compute_key_ratios", ticker.upper())
    _hit = _cache.get(_key)
    if _hit is not None:
        return _hit
    try:
        stock = yf.Ticker(ticker.upper())
        info  = stock.info

        def pct(v):
            return round(v * 100, 2) if v is not None else None

        # --- Valuation Ratios ---
        pe_trailing  = _safe_float(info.get("trailingPE"))
        pe_forward   = _safe_float(info.get("forwardPE"))
        pb_ratio     = _safe_float(info.get("priceToBook"))
        ps_ratio     = _safe_float(info.get("priceToSalesTrailing12Months"))
        ev_ebitda    = _safe_float(info.get("enterpriseToEbitda"))
        ev_revenue   = _safe_float(info.get("enterpriseToRevenue"))

        # --- Profitability ---
        roe          = pct(info.get("returnOnEquity"))
        roa          = pct(info.get("returnOnAssets"))
        net_margin   = pct(info.get("profitMargins"))
        gross_margin = pct(info.get("grossMargins"))
        op_margin    = pct(info.get("operatingMargins"))

        # --- Liquidity & Leverage ---
        current_ratio = _safe_float(info.get("currentRatio"))
        quick_ratio   = _safe_float(info.get("quickRatio"))
        debt_to_eq    = _safe_float(info.get("debtToEquity"))  # already in %
        interest_cov  = None  # calculated manually below

        # --- Growth (from financials) ---
        fin = stock.financials
        revenue_growth = None
        eps_growth     = None
        if fin is not None and not fin.empty and len(fin.columns) >= 2:
            rev_rows = [r for r in ["Total Revenue"] if r in fin.index]
            if rev_rows:
                rev_now  = fin.loc[rev_rows[0], fin.columns[0]]
                rev_prev = fin.loc[rev_rows[0], fin.columns[1]]
                if rev_prev and float(rev_prev) != 0:
                    revenue_growth = round(((float(rev_now) - float(rev_prev)) / abs(float(rev_prev))) * 100, 2)

        # --- FCF Yield ---
        market_cap = info.get("marketCap")
        fcf        = info.get("freeCashflow")
        fcf_yield  = None
        if market_cap and fcf and float(market_cap) > 0:
            fcf_yield = round((float(fcf) / float(market_cap)) * 100, 2)

        # --- Dividend ---
        div_yield  = pct(info.get("dividendYield"))
        payout_rat = pct(info.get("payoutRatio"))

        result = {
            "ticker":          ticker.upper(),
            "company_name":    info.get("longName", ticker.upper()),
            "current_price":   _safe_float(info.get("currentPrice") or info.get("regularMarketPrice")),
            "market_cap_M":    _millions(info.get("marketCap")),
            "52_week_high":    _safe_float(info.get("fiftyTwoWeekHigh")),
            "52_week_low":     _safe_float(info.get("fiftyTwoWeekLow")),

            "valuation": {
                "pe_trailing":  pe_trailing,
                "pe_forward":   pe_forward,
                "pb_ratio":     pb_ratio,
                "ps_ratio":     ps_ratio,
                "ev_ebitda":    ev_ebitda,
                "ev_revenue":   ev_revenue,
            },

            "profitability": {
                "roe_pct":          roe,
                "roa_pct":          roa,
                "net_margin_pct":   net_margin,
                "gross_margin_pct": gross_margin,
                "op_margin_pct":    op_margin,
            },

            "leverage": {
                "current_ratio":    current_ratio,
                "quick_ratio":      quick_ratio,
                "debt_to_equity":   debt_to_eq,
            },

            "growth": {
                "revenue_yoy_pct":      revenue_growth,
                "revenue_growth_3y":    pct(info.get("revenueGrowth")),
                "earnings_growth_yoy":  pct(info.get("earningsGrowth")),
                "earnings_quarterly":   pct(info.get("earningsQuarterlyGrowth")),
            },

            "cash_flow": {
                "fcf_yield_pct":     fcf_yield,
                "free_cash_flow_M":  _millions(info.get("freeCashflow")),
                "operating_cf_M":    _millions(info.get("operatingCashflow")),
            },

            "dividend": {
                "yield_pct":     div_yield,
                "payout_ratio":  payout_rat,
                "annual_div":    _safe_float(info.get("dividendRate")),
            },
        }

        output = json.dumps(result, indent=2, default=str)
        _cache.store(_key, output)
        return output

    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})
