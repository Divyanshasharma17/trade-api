import logging
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)


def build_prompt(sector: str, market_data: str) -> str:
    """Build the prompt we send to Gemini."""
    return f"""
You are a professional trade analyst specializing in Indian markets.
Based on the following real-time market data, generate a comprehensive trade opportunities report.

{market_data}

Generate a detailed markdown report with EXACTLY this structure:

# 🇮🇳 India Trade Opportunities Report: {sector.title()} Sector

## 📊 Executive Summary
[2-3 sentence overview of the sector's current state in India]

## 📈 Current Market Overview
[Current market size, growth rate, key players, recent trends]

## 🚀 Top Trade Opportunities
[List 4-5 specific trade opportunities with details on each]

## 🌍 Export Opportunities
[Key export markets, products in demand, competitive advantages India has]

## 📥 Import Opportunities  
[Key imports needed, sourcing opportunities, cost advantages]

## ⚠️ Risks & Challenges
[3-4 key risks or challenges in this sector]

## 💡 Strategic Recommendations
[3-4 actionable recommendations for businesses]

## 📅 Report Generated
- **Sector**: {sector.title()}
- **Market**: India
- **Data Sources**: Live web search + AI analysis

---
*This report is AI-generated for informational purposes only.*
"""


def analyze_sector(sector: str, market_data: str) -> str:
    """
    Send market data to Gemini and get back a markdown analysis report.
    Falls back gracefully if API fails.
    """
    prompt = build_prompt(sector, market_data)

   
    models_to_try = [
        "models/gemini-2.0-flash-lite",
        "models/gemini-2.0-flash",
        "models/gemini-2.5-flash",
    ]

    for model in models_to_try:
        try:
            logger.info(f"Trying model: {model}")
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            logger.info(f"✅ Analysis complete using {model}")
            return response.text

        except Exception as e:
            error_msg = str(e)
            logger.warning(f"⚠️ Model {model} failed: {error_msg[:100]}")

           
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                continue
            
            continue

    
    logger.error("❌ All Gemini models failed. Returning fallback report.")
    return generate_fallback_report(sector)


def generate_fallback_report(sector: str) -> str:
    """Return a basic report when Gemini API is unavailable."""
    return f"""
# 🇮🇳 India Trade Opportunities Report: {sector.title()} Sector

## ⚠️ Notice
Live AI analysis is temporarily unavailable due to API rate limits. 
Please try again in a few minutes.

## 📊 General Overview
The {sector} sector in India is one of the key contributors to the nation's GDP 
and trade balance. India has been actively pursuing trade partnerships globally 
to boost this sector.

## 🚀 General Trade Opportunities
- Growing domestic demand presents import opportunities
- Government export incentives available under various schemes
- FDI opportunities in manufacturing and services
- Technology collaboration with global players

## 💡 Recommendation
For detailed real-time analysis, please retry this endpoint after 60 seconds.

---
*Fallback report — AI analysis temporarily unavailable.*
"""