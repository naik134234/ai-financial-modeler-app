import logging
import requests
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

# Constants for Yahoo Finance API
BASE_URL = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/"
CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"

# List of user agents to avoid rate limiting
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
]

def _get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

class YahooFinanceCollector:
    """Class to fetch data from Yahoo Finance without yfinance"""
    
    def __init__(self, symbol: str, exchange: str = "NSE"):
        self.symbol = symbol
        self.exchange = exchange
        self.ticker_symbol = f"{symbol}.NS" if exchange == "NSE" else f"{symbol}.BO"
        if '.' in symbol: # Already formatted
            self.ticker_symbol = symbol
            
    def get_data(self) -> Dict[str, Any]:
        """Get all available data for the symbol"""
        info = get_stock_info(self.ticker_symbol)
        financials = get_historical_financials(self.ticker_symbol)
        price_history = get_price_history(self.ticker_symbol)
        
        return {
            "company_info": info if info else {},
            "info": info if info else {}, 
            "financials": financials if financials else {},
            "price_history": price_history if price_history else {},
            "income_statement": financials.get('income_statement', {}) if financials else {},
            "balance_sheet": financials.get('balance_sheet', {}) if financials else {},
            "cash_flow": financials.get('cash_flow', {}) if financials else {},
        }

async def fetch_stock_data(symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
    collector = YahooFinanceCollector(symbol, exchange)
    return collector.get_data()

def get_stock_info(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch basic stock info directly from Yahoo API"""
    try:
        if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
            symbol = f"{symbol}.NS"
            
        modules = "financialData,quoteType,summaryDetail,price,defaultKeyStatistics,summaryProfile"
        url = f"{BASE_URL}{symbol}?modules={modules}"
        
        response = requests.get(url, headers=_get_headers(), timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if 'quoteSummary' not in data or not data['quoteSummary']['result']:
            return None
            
        result = data['quoteSummary']['result'][0]
        
        # Helper to safely get nested values
        def get_v(module, key, default=0):
            return result.get(module, {}).get(key, {}).get('raw', default)

        # Map to common structure
        info = {
            "symbol": symbol.replace('.NS', '').replace('.BO', ''),
            "name": result.get('price', {}).get('longName', symbol),
            "sector": result.get('summaryProfile', {}).get('sector', 'Unknown'),
            "industry": result.get('summaryProfile', {}).get('industry', 'Unknown'),
            "website": result.get('summaryProfile', {}).get('website', ''),
            "description": result.get('summaryProfile', {}).get('longBusinessSummary', ''),
            
            "market_cap": get_v('price', 'marketCap') / 10000000,
            "enterprise_value": get_v('defaultKeyStatistics', 'enterpriseValue') / 10000000,
            "current_price": get_v('financialData', 'currentPrice'),
            "52_week_high": get_v('summaryDetail', 'fiftyTwoWeekHigh'),
            "52_week_low": get_v('summaryDetail', 'fiftyTwoWeekLow'),
            "avg_volume": get_v('summaryDetail', 'averageVolume'),
            
            "shares_outstanding": get_v('defaultKeyStatistics', 'sharesOutstanding') / 10000000,
            "held_percent_insiders": get_v('defaultKeyStatistics', 'heldPercentInsiders'),
            "held_percent_institutions": get_v('defaultKeyStatistics', 'heldPercentInstitutions'),
            
            "pe_ratio": get_v('summaryDetail', 'trailingPE'),
            "forward_pe": get_v('summaryDetail', 'forwardPE'),
            "pb_ratio": get_v('defaultKeyStatistics', 'priceToBook'),
            "ps_ratio": get_v('summaryDetail', 'priceToSalesTrailing12Months'),
            
            "beta": get_v('defaultKeyStatistics', 'beta', 1.0),
            
            "profit_margin": get_v('financialData', 'profitMargins'),
            "operating_margin": get_v('financialData', 'operatingMargins'),
            "return_on_equity": get_v('financialData', 'returnOnEquity'),
            "return_on_assets": get_v('financialData', 'returnOnAssets'),
            
            "total_revenue": get_v('financialData', 'totalRevenue') / 10000000,
            "revenue_growth": get_v('financialData', 'revenueGrowth'),
            "ebitda": get_v('financialData', 'ebitda') / 10000000,
            "total_debt": get_v('financialData', 'totalDebt') / 10000000,
            "total_cash": get_v('financialData', 'totalCash') / 10000000,
            "free_cash_flow": get_v('financialData', 'freeCashflow') / 10000000,
            "earnings_per_share": get_v('defaultKeyStatistics', 'trailingEps'),
            
            "dividend_yield": get_v('summaryDetail', 'dividendYield'),
            "dividend_rate": get_v('summaryDetail', 'dividendRate'),
            "debt_to_equity": get_v('financialData', 'debtToEquity'),
            "current_ratio": get_v('financialData', 'currentRatio'),
        }
        return info
    except Exception as e:
        logger.error(f"Error in get_stock_info for {symbol}: {e}")
        return None

def get_historical_financials(symbol: str, years: int = 5) -> Optional[Dict[str, Any]]:
    """Fetch historical financials from Yahoo API"""
    try:
        if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
            symbol = f"{symbol}.NS"

        modules = "incomeStatementHistory,balanceSheetHistory,cashflowStatementHistory"
        url = f"{BASE_URL}{symbol}?modules={modules}"
        
        response = requests.get(url, headers=_get_headers(), timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if 'quoteSummary' not in data or not data['quoteSummary']['result']:
            return None
            
        result = data['quoteSummary']['result'][0]
        
        def parse_statement(module_name):
            stmt_data = {}
            history = result.get(module_name, {}).get(module_name.replace('History', 'Statements'), [])
            for item in history:
                date = item.get('endDate', {}).get('fmt', '')[:4]
                if not date: continue
                
                vals = {}
                for k, v in item.items():
                    if isinstance(v, dict) and 'raw' in v:
                        vals[k] = v['raw'] / 10000000 # To Crores
                stmt_data[date] = vals
            return stmt_data

        income_stmt = parse_statement('incomeStatementHistory')
        balance_sheet = parse_statement('balanceSheetHistory')
        cash_flow = parse_statement('cashflowStatementHistory')
        
        # Normalize keys for the engine
        normalized_income = {}
        for yr, vals in income_stmt.items():
            normalized_income[yr] = {
                "revenue": vals.get('totalRevenue', 0),
                "gross_profit": vals.get('grossProfit', 0),
                "ebitda": vals.get('ebitda', 0),
                "operating_income": vals.get('operatingIncome', 0),
                "net_income": vals.get('netIncome', 0),
                "interest_expense": vals.get('interestExpense', 0),
                "tax_expense": vals.get('incomeTaxExpense', 0),
            }

        normalized_balance = {}
        for yr, vals in balance_sheet.items():
            normalized_balance[yr] = {
                "total_assets": vals.get('totalAssets', 0),
                "total_liabilities": vals.get('totalLiab', 0),
                "total_equity": vals.get('totalStockholderEquity', 0),
                "cash": vals.get('cash', 0),
                "total_debt": vals.get('longTermDebt', 0) + vals.get('shortLongTermDebt', 0),
                "current_assets": vals.get('totalCurrentAssets', 0),
                "current_liabilities": vals.get('totalCurrentLiabilities', 0),
            }

        normalized_cash = {}
        for yr, vals in cash_flow.items():
            normalized_cash[yr] = {
                "operating_cash_flow": vals.get('totalCashFromOperatingActivities', 0),
                "capex": abs(vals.get('capitalExpenditures', 0)),
                "depreciation": vals.get('depreciation', 0),
                "free_cash_flow": vals.get('totalCashFromOperatingActivities', 0) + vals.get('capitalExpenditures', 0),
            }

        return {
            "income_statement": normalized_income,
            "balance_sheet": normalized_balance,
            "cash_flow": normalized_cash,
            "years_available": len(normalized_income),
        }
    except Exception as e:
        logger.error(f"Error in get_historical_financials for {symbol}: {e}")
        return None

def get_price_history(symbol: str, period: str = "5y") -> Optional[Dict[str, Any]]:
    """Fetch price history using Chart API"""
    try:
        if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
            symbol = f"{symbol}.NS"
            
        # Map period to YF range
        range_map = {"1y": "1y", "2y": "2y", "5y": "5y", "10y": "10y", "max": "max"}
        r = range_map.get(period, "5y")
        
        url = f"{CHART_URL}{symbol}?range={r}&interval=1d"
        response = requests.get(url, headers=_get_headers(), timeout=15)
        response.raise_for_status()
        data = response.json()
        
        chart = data.get('chart', {}).get('result', [{}])[0]
        if not chart: return None
        
        closes = chart.get('indicators', {}).get('quote', [{}])[0].get('close', [])
        closes = [c for c in closes if c is not None]
        
        if not closes: return None
        
        returns = [(closes[i] / closes[i-1]) - 1 for i in range(1, len(closes))]
        avg_ret = sum(returns) / len(returns) if returns else 0
        std_ret = (sum([(x - avg_ret)**2 for x in returns]) / len(returns))**0.5 if returns else 0
        
        return {
            "current_price": closes[-1],
            "start_price": closes[0],
            "high": max(closes),
            "low": min(closes),
            "total_return": (closes[-1] / closes[0]) - 1,
            "annualized_return": avg_ret * 252,
            "volatility": std_ret * (252 ** 0.5),
            "sharpe_ratio": (avg_ret * 252 - 0.07) / (std_ret * (252 ** 0.5)) if std_ret > 0 else 0,
        }
    except Exception as e:
        logger.error(f"Error in get_price_history for {symbol}: {e}")
        return None

def get_peer_comparison(symbol: str, peers: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
    """Fetch peer data using multiple API calls"""
    if not peers:
        peers = []
    
    results = []
    # Add main company
    main_info = get_stock_info(symbol)
    if main_info:
        results.append({
            "symbol": main_info["symbol"],
            "name": main_info["name"],
            "market_cap": main_info["market_cap"],
            "pe_ratio": main_info["pe_ratio"],
            "pb_ratio": main_info["pb_ratio"],
            "roe": main_info["return_on_equity"] * 100,
            "is_main": True,
        })
    
    for p in peers:
        p_info = get_stock_info(p)
        if p_info:
            results.append({
                "symbol": p_info["symbol"],
                "name": p_info["name"],
                "market_cap": p_info["market_cap"],
                "pe_ratio": p_info["pe_ratio"],
                "pb_ratio": p_info["pb_ratio"],
                "roe": p_info["return_on_equity"] * 100,
                "is_main": False,
            })
    return results

def search_stocks(query: str, limit: int = 10) -> List[Dict[str, str]]:
    """Simple offline search for common Indian stocks"""
    common_stocks = [
        {"symbol": "RELIANCE", "name": "Reliance Industries Ltd"},
        {"symbol": "TCS", "name": "Tata Consultancy Services"},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd"},
        {"symbol": "INFY", "name": "Infosys Ltd"},
        {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd"},
        {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd"},
        {"symbol": "SBIN", "name": "State Bank of India"},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd"},
        {"symbol": "ITC", "name": "ITC Ltd"},
        {"symbol": "WIPRO", "name": "Wipro Ltd"},
        {"symbol": "ADANIPOWER", "name": "Adani Power"},
    ]
    query_lower = query.lower()
    return [s for s in common_stocks if query_lower in s["symbol"].lower() or query_lower in s["name"].lower()][:limit]


def _get_value(df, col, possible_keys: List[str]) -> float:
    """Helper to get value from dataframe with multiple possible keys"""
    for key in possible_keys:
        if key in df.index:
            val = df.loc[key, col]
            if val is not None and not (hasattr(val, '__iter__') and not isinstance(val, str)):
                return float(val) / 10000000  # Convert to Crores
    return 0.0


def search_stocks(query: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Search for stocks by name or symbol
    
    Args:
        query: Search query
        limit: Maximum results
    
    Returns:
        List of matching stocks
    """
    # For Yahoo Finance, we'd need a separate search API
    # This is a placeholder that returns common Indian stocks
    common_stocks = [
        {"symbol": "RELIANCE", "name": "Reliance Industries Ltd"},
        {"symbol": "TCS", "name": "Tata Consultancy Services"},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd"},
        {"symbol": "INFY", "name": "Infosys Ltd"},
        {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd"},
        {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd"},
        {"symbol": "SBIN", "name": "State Bank of India"},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd"},
        {"symbol": "ITC", "name": "ITC Ltd"},
        {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank"},
        {"symbol": "LT", "name": "Larsen & Toubro Ltd"},
        {"symbol": "AXISBANK", "name": "Axis Bank Ltd"},
        {"symbol": "WIPRO", "name": "Wipro Ltd"},
        {"symbol": "ASIANPAINT", "name": "Asian Paints Ltd"},
        {"symbol": "MARUTI", "name": "Maruti Suzuki India Ltd"},
        {"symbol": "TITAN", "name": "Titan Company Ltd"},
        {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical"},
        {"symbol": "ULTRACEMCO", "name": "UltraTech Cement Ltd"},
        {"symbol": "TATAMOTORS", "name": "Tata Motors Ltd"},
        {"symbol": "POWERGRID", "name": "Power Grid Corporation"},
    ]
    
    query_lower = query.lower()
    results = [
        stock for stock in common_stocks
        if query_lower in stock["symbol"].lower() or query_lower in stock["name"].lower()
    ]
    
    return results[:limit]
