"""
main.py
-------
Entry point for the Fundamental Analysis Agent.

Usage (run from inside the fundamental_analysis_agent/ folder):
  python main.py AAPL
  python main.py MSFT --watchlist GOOGL TSLA NVDA
  python main.py AAPL --stream

The script loads environment variables from a .env file, then runs the
OrchestratorAgent with the given ticker(s) and prints the investment brief.
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv


class _Tee:
    """Mirror writes to stdout to both the terminal and a file."""

    def __init__(self, file_path: Path):
        self._terminal = sys.stdout
        self._file = open(file_path, "w", encoding="utf-8")

    def write(self, message: str) -> None:
        self._terminal.write(message)
        self._file.write(message)

    def flush(self) -> None:
        self._terminal.flush()
        self._file.flush()

    def close(self) -> None:
        self._file.close()

    # Proxy all other attribute access to the real stdout
    def __getattr__(self, name):
        return getattr(self._terminal, name)

# Ensure stdout can handle UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load .env from the package folder (same directory as main.py)
load_dotenv(Path(__file__).parent / ".env")

from agents import Runner
from agents.items import ToolCallItem, ToolCallOutputItem
from specialist_agents.orchestrator import orchestrator
from tools import cache as _cache


# ---------------------------------------------------------------------------
# Verbose helpers
# ---------------------------------------------------------------------------

_AGENT_LABELS = {
    "financial_data_analysis":    "Financial Data Agent",
    "news_and_sentiment_analysis": "News & Sentiment Agent",
    "risk_assessment":            "Risk Agent",
    "valuation_analysis":         "Valuation Agent",
    "write_investment_report":    "Report Writer Agent",
}



_AGENT_FILE_NAMES = {
    "financial_data_analysis":     "financial_data_agent",
    "news_and_sentiment_analysis": "news_sentiment_agent",
    "risk_assessment":             "risk_agent",
    "valuation_analysis":          "valuation_agent",
    "write_investment_report":     "report_writer_agent",
}


def _extract_intermediate_results(new_items: list) -> list[tuple[str, str, str]]:
    """Extract sub-agent results from the run's item list.

    Returns a list of (tool_name, label, output) tuples in call order.
    Pairs ToolCallItems with ToolCallOutputItems by call_id.
    """
    calls: list[tuple[str, str]] = []   # (call_id, tool_name)
    outputs: dict[str, str] = {}        # call_id -> output text

    for item in new_items:
        if isinstance(item, ToolCallItem):
            call_id = getattr(item.raw_item, "call_id", None)
            tool_name = getattr(item.raw_item, "name", None)
            if call_id and tool_name:
                calls.append((call_id, tool_name))
        elif isinstance(item, ToolCallOutputItem):
            raw = item.raw_item
            call_id = raw.get("call_id") if isinstance(raw, dict) else getattr(raw, "call_id", None)
            if call_id:
                outputs[call_id] = item.output

    return [
        (tool_name, _AGENT_LABELS.get(tool_name, tool_name), outputs.get(call_id, ""))
        for call_id, tool_name in calls
    ]


def _print_trace(new_items: list) -> None:
    """Print the raw tool call sequence to verify parallel vs sequential execution.

    Consecutive CALL entries with no OUTPUT in between means the LLM issued
    them as parallel tool calls in a single response turn.
    """
    print(f"\n{'='*60}")
    print("  TOOL CALL TRACE")
    print(f"{'='*60}")
    call_id_to_name: dict[str, str] = {}
    for i, item in enumerate(new_items, 1):
        if isinstance(item, ToolCallItem):
            call_id  = getattr(item.raw_item, "call_id", "?")
            tool_name = getattr(item.raw_item, "name", "?")
            call_id_to_name[call_id] = tool_name
            label = _AGENT_LABELS.get(tool_name, tool_name)
            print(f"[{i:02d}] CALL   {label} (id={call_id})")
        elif isinstance(item, ToolCallOutputItem):
            raw = item.raw_item
            call_id = raw.get("call_id") if isinstance(raw, dict) else getattr(raw, "call_id", "?")
            tool_name = call_id_to_name.get(call_id, "?")
            label = _AGENT_LABELS.get(tool_name, tool_name)
            print(f"[{i:02d}] OUTPUT {label} (id={call_id})")
    print(f"{'='*60}\n")


def _print_intermediate_results(new_items: list) -> None:
    """Print each sub-agent's output to stdout."""
    for _, label, output in _extract_intermediate_results(new_items):
        print(f"\n{'-'*60}")
        print(f"  [{label}]")
        print(f"{'-'*60}")
        if output:
            print(output)


def _save_intermediate_results(new_items: list, final_output: str, ticker: str, log_dir: Path) -> None:
    """Save each sub-agent's output to its own .txt file inside log_dir."""
    log_dir.mkdir(parents=True, exist_ok=True)
    for tool_name, label, output in _extract_intermediate_results(new_items):
        file_name = _AGENT_FILE_NAMES.get(tool_name, tool_name)
        path = log_dir / f"{ticker}_{file_name}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"[{label}]\n")
            f.write("-" * 60 + "\n")
            f.write(output)
        print(f"[LOG] {label} -> {path}")
    # Final report
    report_path = log_dir / f"{ticker}_final_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_output)
    print(f"[LOG] Final Report      -> {report_path}")


# ---------------------------------------------------------------------------
# Core analysis function
# ---------------------------------------------------------------------------

async def analyze_ticker(
    ticker: str,
    stream: bool = False,
    verbose: bool = False,
    trace: bool = False,
    log_dir: Path | None = None,
) -> str:
    """
    Run the full fundamental analysis pipeline for a single ticker.

    Args:
        ticker:   Stock ticker symbol (e.g., 'AAPL').
        stream:   If True, print streamed output tokens as they arrive.
        verbose:  If True, print each sub-agent's output after the run.
        trace:    If True, print the raw tool call sequence (CALL/OUTPUT per agent).
        log_dir:  If set, save each sub-agent's output to its own .txt file.

    Returns:
        The final investment brief as a string.
    """
    ticker = ticker.upper().strip()
    _cache.clear()
    print(f"\n{'='*60}")
    print(f"  Starting analysis for: {ticker}")
    print(f"{'='*60}\n")
    print("Running pipeline: Financial Data -> News/Sentiment + Risk -> Valuation -> Report\n")

    prompt = (
        f"Perform a complete fundamental analysis for the stock ticker: {ticker}\n"
        f"Follow the full workflow: gather financial data, news sentiment, and risk "
        f"assessment, then run valuation, and finally produce the investment brief."
    )

    if stream:
        # Streaming mode: print tokens as they arrive
        result = Runner.run_streamed(orchestrator, input=prompt)
        async for event in result.stream_events():
            if event.type == "raw_response_event":
                pass
            elif event.type == "run_item_stream_event":
                if hasattr(event.item, "text_delta"):
                    print(event.item.text_delta, end="", flush=True)
        final_output = result.final_output
    else:
        result = await Runner.run(orchestrator, input=prompt)
        final_output = result.final_output

    if trace:
        _print_trace(result.new_items)

    if verbose:
        _print_intermediate_results(result.new_items)

    if log_dir is not None:
        _save_intermediate_results(result.new_items, final_output, ticker, log_dir)

    return final_output


async def analyze_watchlist(
    tickers: list[str],
    verbose: bool = False,
    log_dir: Path | None = None,
) -> dict[str, str]:
    """
    Analyze a list of tickers sequentially and return a dict of results.

    Note: We run sequentially (not in parallel) to respect API rate limits.
    For parallel execution, remove the await and use asyncio.gather().
    """
    results = {}
    for ticker in tickers:
        try:
            results[ticker] = await analyze_ticker(ticker, verbose=verbose, log_dir=log_dir)
        except Exception as e:
            results[ticker] = f"ERROR: {str(e)}"
            print(f"\n[ERROR] Analysis failed for {ticker}: {e}")
    return results


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fundamental-analysis-agent",
        description="AI-powered fundamental stock analysis using multi-agent pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples (run from inside this folder):
  python main.py AAPL
  python main.py MSFT --stream
  python main.py AAPL --verbose
  python main.py AAPL --trace
  python main.py AAPL --verbose --log-dir logs/
  python main.py AAPL --trace --verbose --log-dir logs/
  python main.py AAPL --watchlist GOOGL TSLA NVDA MSFT
""",
    )
    parser.add_argument(
        "ticker",
        type=str,
        help="Primary stock ticker to analyze (e.g., AAPL, MSFT, GOOGL).",
    )
    parser.add_argument(
        "--watchlist",
        nargs="+",
        metavar="TICKER",
        help="Additional tickers to analyze after the primary ticker.",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream the output tokens as they are generated.",
    )
    parser.add_argument(
        "--output",
        type=str,
        metavar="FILE",
        help="Save the report(s) to a text file.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each sub-agent's output after it completes.",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Print the raw tool call sequence to verify parallel vs sequential execution.",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        metavar="DIR",
        help="Save each sub-agent's output to its own .txt file in DIR.",
    )
    parser.add_argument(
        "--working-memory",
        type=str,
        nargs="?",
        const="working_memory.txt",
        metavar="FILE",
        help="Mirror all terminal output to a file (default: working_memory.txt).",
    )
    return parser


def check_api_key() -> None:
    """Verify OPENAI_API_KEY is set before running."""
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY is not set.")
        print("Please create a .env file with your key or set the environment variable:")
        print("  export OPENAI_API_KEY=sk-your-key-here")
        sys.exit(1)


async def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    check_api_key()

    tee = None
    if args.working_memory:
        tee = _Tee(Path(args.working_memory))
        sys.stdout = tee

    all_tickers = [args.ticker]
    if args.watchlist:
        all_tickers += args.watchlist

    log_dir = Path(args.log_dir) if args.log_dir else None
    all_reports: dict[str, str] = {}

    if len(all_tickers) == 1:
        # Single ticker — run directly
        report = await analyze_ticker(all_tickers[0], stream=args.stream, verbose=args.verbose, trace=args.trace, log_dir=log_dir)
        all_reports[all_tickers[0]] = report
        print(report)
    else:
        # Watchlist — run sequentially
        print(f"Analyzing watchlist: {', '.join(all_tickers)}\n")
        all_reports = await analyze_watchlist(all_tickers, verbose=args.verbose, log_dir=log_dir)
        for ticker, report in all_reports.items():
            print(report)
            print("\n" + "-" * 60 + "\n")

    if tee:
        sys.stdout = tee._terminal
        tee.close()
        print(f"\n[INFO] Terminal output saved to: {Path(args.working_memory).resolve()}")

    # Optional: save to file
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            for ticker, report in all_reports.items():
                f.write(report)
                f.write("\n\n" + "-" * 60 + "\n\n")
        print(f"\n[INFO] Report(s) saved to: {output_path.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
