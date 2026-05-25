"""
common.py — Shared task setup for Chapter 3 framework labs.

Every framework lab in this chapter solves the same reference task:
compare Apple (AAPL) and JPMorgan (JPM) on P/E ratios, then write a
short memo. This file centralises the typed tool inputs, the finance
dataset, the two tools, and the system / user prompts so each lab
focuses on the framework-specific code, not on plumbing.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class TickerInput(BaseModel):
    ticker: str = Field(..., description="Ticker symbol like AAPL or JPM")


class PEInput(BaseModel):
    price: float = Field(..., description="Stock price")
    eps: float = Field(..., description="Earnings per share")


# Reproducible mini-dataset so the labs run without external data subscriptions.
finance_data: dict[str, dict[str, float]] = {
    "AAPL": {"price": 195.3, "eps": 6.67},
    "JPM":  {"price": 148.7, "eps": 12.61},
}


def get_stock_data(ticker: str) -> PEInput:
    """Get stock price and EPS for a given ticker symbol."""
    t = ticker.upper()
    if t not in finance_data:
        raise ValueError(f"Ticker {t!r} not found")
    return PEInput(price=finance_data[t]["price"], eps=finance_data[t]["eps"])


def compute_pe(price: float, eps: float) -> float:
    """Compute the P/E ratio: price / earnings per share."""
    return round(price / eps, 2)


system_message = "You are a helpful finance analyst."
input_message = (
    "Compare Apple (AAPL) and JPMorgan (JPM) on P/E ratios and "
    "summarize in a memo."
)
