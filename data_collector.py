import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

def collect_market_data(sector: str) -> dict:
    """
    Search DuckDuckGo for recent market news and trade data for the given sector.
    Returns a dict with news headlines and snippets.
    """
    results = {
        "sector": sector,
        "news": [],
        "trade_data": [],
        "errors": [],
    }


    try:
        with DDGS() as ddgs:
            news_query = f"{sector} sector India trade market 2024 2025 opportunities"
            news_results = list(ddgs.text(news_query, max_results=6))
            for item in news_results:
                results["news"].append({
                    "title": item.get("title", ""),
                    "snippet": item.get("body", ""),
                    "url": item.get("href", ""),
                })
            logger.info(f"✅ Collected {len(news_results)} news items for '{sector}'")
    except Exception as e:
        logger.error(f"❌ News search failed: {e}")
        results["errors"].append(f"News search failed: {str(e)}")

    try:
        with DDGS() as ddgs:
            trade_query = f"India {sector} export import trade statistics growth 2025"
            trade_results = list(ddgs.text(trade_query, max_results=4))
            for item in trade_results:
                results["trade_data"].append({
                    "title": item.get("title", ""),
                    "snippet": item.get("body", ""),
                    "url": item.get("href", ""),
                })
            logger.info(f"✅ Collected {len(trade_results)} trade data items for '{sector}'")
    except Exception as e:
        logger.error(f"❌ Trade data search failed: {e}")
        results["errors"].append(f"Trade data search failed: {str(e)}")

    return results


def format_data_for_prompt(data: dict) -> str:
    """
    Format the collected data into a clean string to send to Gemini.
    """
    sector = data["sector"]
    lines = [f"SECTOR: {sector.upper()}", ""]

    if data["news"]:
        lines.append("=== RECENT NEWS & MARKET UPDATES ===")
        for i, item in enumerate(data["news"], 1):
            lines.append(f"{i}. {item['title']}")
            lines.append(f"   {item['snippet']}")
            lines.append("")

    if data["trade_data"]:
        lines.append("=== TRADE & EXPORT DATA ===")
        for i, item in enumerate(data["trade_data"], 1):
            lines.append(f"{i}. {item['title']}")
            lines.append(f"   {item['snippet']}")
            lines.append("")

    if not data["news"] and not data["trade_data"]:
        lines.append("No live data collected. Please use general knowledge for this sector.")

    return "\n".join(lines)