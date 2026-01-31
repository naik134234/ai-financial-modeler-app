"""
Comprehensive Indian Stock Database
All NSE/BSE listed companies by sector
"""

INDIAN_STOCKS = {
    # POWER & UTILITIES
    "power": [
        {"symbol": "ADANIPOWER", "name": "Adani Power Ltd", "sector": "Power Generation"},
        {"symbol": "NTPC", "name": "NTPC Limited", "sector": "Power Generation"},
        {"symbol": "POWERGRID", "name": "Power Grid Corporation", "sector": "Power Transmission"},
        {"symbol": "TATAPOWER", "name": "Tata Power Company", "sector": "Power Generation"},
        {"symbol": "ADANIGREEN", "name": "Adani Green Energy", "sector": "Renewable Energy"},
        {"symbol": "NHPC", "name": "NHPC Limited", "sector": "Hydro Power"},
        {"symbol": "SJVN", "name": "SJVN Limited", "sector": "Hydro Power"},
        {"symbol": "TORNTPOWER", "name": "Torrent Power", "sector": "Power - Integrated"},
        {"symbol": "CESC", "name": "CESC Limited", "sector": "Power - Integrated"},
        {"symbol": "JPPOWER", "name": "Jaiprakash Power", "sector": "Power Generation"},
        {"symbol": "RPOWER", "name": "Reliance Power", "sector": "Power Generation"},
        {"symbol": "JSPL", "name": "JSW Energy", "sector": "Power Generation"},
        {"symbol": "IEX", "name": "Indian Energy Exchange", "sector": "Power Exchange"},
    ],
    
    # BANKING
    "banking": [
        {"symbol": "HDFCBANK", "name": "HDFC Bank", "sector": "Private Bank"},
        {"symbol": "ICICIBANK", "name": "ICICI Bank", "sector": "Private Bank"},
        {"symbol": "SBIN", "name": "State Bank of India", "sector": "Public Bank"},
        {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "sector": "Private Bank"},
        {"symbol": "AXISBANK", "name": "Axis Bank", "sector": "Private Bank"},
        {"symbol": "INDUSINDBK", "name": "IndusInd Bank", "sector": "Private Bank"},
        {"symbol": "BANKBARODA", "name": "Bank of Baroda", "sector": "Public Bank"},
        {"symbol": "PNB", "name": "Punjab National Bank", "sector": "Public Bank"},
        {"symbol": "CANBK", "name": "Canara Bank", "sector": "Public Bank"},
        {"symbol": "UNIONBANK", "name": "Union Bank of India", "sector": "Public Bank"},
        {"symbol": "IDFCFIRSTB", "name": "IDFC First Bank", "sector": "Private Bank"},
        {"symbol": "FEDERALBNK", "name": "Federal Bank", "sector": "Private Bank"},
        {"symbol": "BANDHANBNK", "name": "Bandhan Bank", "sector": "Private Bank"},
        {"symbol": "RBLBANK", "name": "RBL Bank", "sector": "Private Bank"},
        {"symbol": "YESBANK", "name": "Yes Bank", "sector": "Private Bank"},
    ],
    
    # IT & TECHNOLOGY
    "it": [
        {"symbol": "TCS", "name": "Tata Consultancy Services", "sector": "IT Services"},
        {"symbol": "INFY", "name": "Infosys", "sector": "IT Services"},
        {"symbol": "WIPRO", "name": "Wipro", "sector": "IT Services"},
        {"symbol": "HCLTECH", "name": "HCL Technologies", "sector": "IT Services"},
        {"symbol": "TECHM", "name": "Tech Mahindra", "sector": "IT Services"},
        {"symbol": "LTI", "name": "LTIMindtree", "sector": "IT Services"},
        {"symbol": "MPHASIS", "name": "Mphasis", "sector": "IT Services"},
        {"symbol": "COFORGE", "name": "Coforge", "sector": "IT Services"},
        {"symbol": "PERSISTENT", "name": "Persistent Systems", "sector": "IT Services"},
        {"symbol": "CYIENT", "name": "Cyient", "sector": "IT Services"},
        {"symbol": "LTTS", "name": "L&T Technology Services", "sector": "Engineering R&D"},
        {"symbol": "TATAELXSI", "name": "Tata Elxsi", "sector": "Design & Engineering"},
    ],
    
    # PHARMA & HEALTHCARE
    "pharma": [
        {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical", "sector": "Pharma"},
        {"symbol": "DRREDDY", "name": "Dr. Reddy's Laboratories", "sector": "Pharma"},
        {"symbol": "CIPLA", "name": "Cipla", "sector": "Pharma"},
        {"symbol": "DIVISLAB", "name": "Divi's Laboratories", "sector": "Pharma - API"},
        {"symbol": "LUPIN", "name": "Lupin", "sector": "Pharma"},
        {"symbol": "AUROPHARMA", "name": "Aurobindo Pharma", "sector": "Pharma"},
        {"symbol": "BIOCON", "name": "Biocon", "sector": "Biopharma"},
        {"symbol": "TORNTPHARM", "name": "Torrent Pharma", "sector": "Pharma"},
        {"symbol": "ALKEM", "name": "Alkem Laboratories", "sector": "Pharma"},
        {"symbol": "ZYDUSLIFE", "name": "Zydus Lifesciences", "sector": "Pharma"},
        {"symbol": "APOLLOHOSP", "name": "Apollo Hospitals", "sector": "Hospitals"},
        {"symbol": "MAXHEALTH", "name": "Max Healthcare", "sector": "Hospitals"},
        {"symbol": "FORTIS", "name": "Fortis Healthcare", "sector": "Hospitals"},
        {"symbol": "LALPATHLAB", "name": "Dr Lal PathLabs", "sector": "Diagnostics"},
        {"symbol": "METROPOLIS", "name": "Metropolis Healthcare", "sector": "Diagnostics"},
    ],
    
    # FMCG
    "fmcg": [
        {"symbol": "HINDUNILVR", "name": "Hindustan Unilever", "sector": "FMCG"},
        {"symbol": "ITC", "name": "ITC Limited", "sector": "FMCG - Diversified"},
        {"symbol": "NESTLEIND", "name": "Nestle India", "sector": "FMCG - Foods"},
        {"symbol": "BRITANNIA", "name": "Britannia Industries", "sector": "FMCG - Foods"},
        {"symbol": "DABUR", "name": "Dabur India", "sector": "FMCG - Personal Care"},
        {"symbol": "MARICO", "name": "Marico", "sector": "FMCG - Personal Care"},
        {"symbol": "GODREJCP", "name": "Godrej Consumer Products", "sector": "FMCG"},
        {"symbol": "COLPAL", "name": "Colgate-Palmolive India", "sector": "FMCG - Oral Care"},
        {"symbol": "TATACONSUM", "name": "Tata Consumer Products", "sector": "FMCG - Foods"},
        {"symbol": "VBL", "name": "Varun Beverages", "sector": "Beverages"},
        {"symbol": "UBL", "name": "United Breweries", "sector": "Beverages - Alcoholic"},
        {"symbol": "RADICO", "name": "Radico Khaitan", "sector": "Beverages - Alcoholic"},
        {"symbol": "MCDOWELL-N", "name": "United Spirits", "sector": "Beverages - Alcoholic"},
    ],
    
    # AUTOMOBILES
    "auto": [
        {"symbol": "TATAMOTORS", "name": "Tata Motors", "sector": "Auto - Passenger Vehicles"},
        {"symbol": "MARUTI", "name": "Maruti Suzuki India", "sector": "Auto - Passenger Vehicles"},
        {"symbol": "M&M", "name": "Mahindra & Mahindra", "sector": "Auto - Utility Vehicles"},
        {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto", "sector": "Auto - Two Wheeler"},
        {"symbol": "HEROMOTOCO", "name": "Hero MotoCorp", "sector": "Auto - Two Wheeler"},
        {"symbol": "EICHERMOT", "name": "Eicher Motors", "sector": "Auto - Two Wheeler"},
        {"symbol": "TVSMOTOR", "name": "TVS Motor Company", "sector": "Auto - Two Wheeler"},
        {"symbol": "ASHOKLEY", "name": "Ashok Leyland", "sector": "Auto - Commercial Vehicles"},
        {"symbol": "ESCORTS", "name": "Escorts Kubota", "sector": "Auto - Tractors"},
        {"symbol": "BALKRISIND", "name": "Balkrishna Industries", "sector": "Auto - Tyres"},
        {"symbol": "MRF", "name": "MRF Limited", "sector": "Auto - Tyres"},
        {"symbol": "APOLLOTYRE", "name": "Apollo Tyres", "sector": "Auto - Tyres"},
        {"symbol": "MOTHERSON", "name": "Samvardhana Motherson", "sector": "Auto Ancillary"},
        {"symbol": "BOSCHLTD", "name": "Bosch", "sector": "Auto Ancillary"},
    ],
    
    # METALS & MINING
    "metals": [
        {"symbol": "TATASTEEL", "name": "Tata Steel", "sector": "Steel"},
        {"symbol": "JSWSTEEL", "name": "JSW Steel", "sector": "Steel"},
        {"symbol": "HINDALCO", "name": "Hindalco Industries", "sector": "Aluminium"},
        {"symbol": "VEDL", "name": "Vedanta Limited", "sector": "Diversified Metals"},
        {"symbol": "COALINDIA", "name": "Coal India", "sector": "Coal Mining"},
        {"symbol": "NMDC", "name": "NMDC Limited", "sector": "Iron Ore Mining"},
        {"symbol": "SAIL", "name": "Steel Authority of India", "sector": "Steel"},
        {"symbol": "NATIONALUM", "name": "National Aluminium", "sector": "Aluminium"},
        {"symbol": "HINDZINC", "name": "Hindustan Zinc", "sector": "Zinc"},
        {"symbol": "JINDALSTEL", "name": "Jindal Steel & Power", "sector": "Steel"},
        {"symbol": "APLAPOLLO", "name": "APL Apollo Tubes", "sector": "Steel Tubes"},
    ],
    
    # OIL & GAS
    "oil_gas": [
        {"symbol": "RELIANCE", "name": "Reliance Industries", "sector": "Oil & Gas - Integrated"},
        {"symbol": "ONGC", "name": "Oil & Natural Gas Corporation", "sector": "Oil & Gas - Exploration"},
        {"symbol": "IOC", "name": "Indian Oil Corporation", "sector": "Oil & Gas - Refining"},
        {"symbol": "BPCL", "name": "Bharat Petroleum", "sector": "Oil & Gas - Refining"},
        {"symbol": "HINDPETRO", "name": "Hindustan Petroleum", "sector": "Oil & Gas - Refining"},
        {"symbol": "GAIL", "name": "GAIL (India)", "sector": "Gas Transmission"},
        {"symbol": "PETRONET", "name": "Petronet LNG", "sector": "LNG"},
        {"symbol": "OIL", "name": "Oil India", "sector": "Oil & Gas - Exploration"},
        {"symbol": "MGL", "name": "Mahanagar Gas", "sector": "City Gas Distribution"},
        {"symbol": "IGL", "name": "Indraprastha Gas", "sector": "City Gas Distribution"},
        {"symbol": "GUJGASLTD", "name": "Gujarat Gas", "sector": "City Gas Distribution"},
        {"symbol": "ATGL", "name": "Adani Total Gas", "sector": "City Gas Distribution"},
    ],
    
    # CEMENT & CONSTRUCTION
    "cement": [
        {"symbol": "ULTRACEMCO", "name": "UltraTech Cement", "sector": "Cement"},
        {"symbol": "SHREECEM", "name": "Shree Cement", "sector": "Cement"},
        {"symbol": "AMBUJACEM", "name": "Ambuja Cements", "sector": "Cement"},
        {"symbol": "ACC", "name": "ACC Limited", "sector": "Cement"},
        {"symbol": "DALMIACEM", "name": "Dalmia Bharat", "sector": "Cement"},
        {"symbol": "RAMCOCEM", "name": "The Ramco Cements", "sector": "Cement"},
        {"symbol": "JKCEMENT", "name": "JK Cement", "sector": "Cement"},
        {"symbol": "BIRLACORP", "name": "Birla Corporation", "sector": "Cement"},
        {"symbol": "INDIACEM", "name": "The India Cements", "sector": "Cement"},
    ],
    
    # INFRASTRUCTURE & REAL ESTATE
    "infra": [
        {"symbol": "LT", "name": "Larsen & Toubro", "sector": "Infrastructure Conglomerate"},
        {"symbol": "ADANIENT", "name": "Adani Enterprises", "sector": "Infrastructure Conglomerate"},
        {"symbol": "ADANIPORTS", "name": "Adani Ports & SEZ", "sector": "Ports"},
        {"symbol": "DLF", "name": "DLF Limited", "sector": "Real Estate"},
        {"symbol": "GODREJPROP", "name": "Godrej Properties", "sector": "Real Estate"},
        {"symbol": "OBEROIRLTY", "name": "Oberoi Realty", "sector": "Real Estate"},
        {"symbol": "PRESTIGE", "name": "Prestige Estates", "sector": "Real Estate"},
        {"symbol": "LODHA", "name": "Macrotech Developers", "sector": "Real Estate"},
        {"symbol": "IRB", "name": "IRB Infrastructure", "sector": "Roads & Highways"},
        {"symbol": "IRCON", "name": "Ircon International", "sector": "Construction"},
        {"symbol": "NBCC", "name": "NBCC (India)", "sector": "Construction"},
        {"symbol": "NCC", "name": "NCC Limited", "sector": "Construction"},
        {"symbol": "KEC", "name": "KEC International", "sector": "EPC"},
    ],
    
    # NBFC & FINANCIAL SERVICES
    "nbfc": [
        {"symbol": "BAJFINANCE", "name": "Bajaj Finance", "sector": "Consumer Finance"},
        {"symbol": "BAJAJFINSV", "name": "Bajaj Finserv", "sector": "Financial Services"},
        {"symbol": "HDFCLIFE", "name": "HDFC Life Insurance", "sector": "Life Insurance"},
        {"symbol": "SBILIFE", "name": "SBI Life Insurance", "sector": "Life Insurance"},
        {"symbol": "ICICIPRULI", "name": "ICICI Prudential Life", "sector": "Life Insurance"},
        {"symbol": "ICICIGI", "name": "ICICI Lombard GIC", "sector": "General Insurance"},
        {"symbol": "NIACL", "name": "New India Assurance", "sector": "General Insurance"},
        {"symbol": "CHOLAFIN", "name": "Cholamandalam Investment", "sector": "Vehicle Finance"},
        {"symbol": "MUTHOOTFIN", "name": "Muthoot Finance", "sector": "Gold Finance"},
        {"symbol": "MANAPPURAM", "name": "Manappuram Finance", "sector": "Gold Finance"},
        {"symbol": "SHRIRAMFIN", "name": "Shriram Finance", "sector": "Vehicle Finance"},
        {"symbol": "M&MFIN", "name": "Mahindra & Mahindra Financial", "sector": "Vehicle Finance"},
        {"symbol": "POONAWALLA", "name": "Poonawalla Fincorp", "sector": "Consumer Finance"},
        {"symbol": "LICHSGFIN", "name": "LIC Housing Finance", "sector": "Housing Finance"},
        {"symbol": "CANFINHOME", "name": "Can Fin Homes", "sector": "Housing Finance"},
    ],
    
    # TELECOM & MEDIA
    "telecom": [
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "sector": "Telecom"},
        {"symbol": "IDEA", "name": "Vodafone Idea", "sector": "Telecom"},
        {"symbol": "INDUSTOWER", "name": "Indus Towers", "sector": "Telecom Infrastructure"},
        {"symbol": "TATACOMM", "name": "Tata Communications", "sector": "Enterprise Telecom"},
        {"symbol": "ZEEL", "name": "Zee Entertainment", "sector": "Media & Entertainment"},
        {"symbol": "SUNTV", "name": "Sun TV Network", "sector": "Media & Entertainment"},
        {"symbol": "PVR", "name": "PVR INOX", "sector": "Media & Entertainment"},
    ],
    
    # CHEMICALS & FERTILIZERS
    "chemicals": [
        {"symbol": "PIDILITIND", "name": "Pidilite Industries", "sector": "Specialty Chemicals"},
        {"symbol": "UPL", "name": "UPL Limited", "sector": "Agrochemicals"},
        {"symbol": "SRF", "name": "SRF Limited", "sector": "Specialty Chemicals"},
        {"symbol": "AARTI", "name": "Aarti Industries", "sector": "Specialty Chemicals"},
        {"symbol": "DEEPAKNTR", "name": "Deepak Nitrite", "sector": "Specialty Chemicals"},
        {"symbol": "NAVINFLUOR", "name": "Navin Fluorine", "sector": "Fluorochemicals"},
        {"symbol": "ATUL", "name": "Atul Limited", "sector": "Specialty Chemicals"},
        {"symbol": "COROMANDEL", "name": "Coromandel International", "sector": "Fertilizers"},
        {"symbol": "GNFC", "name": "Gujarat Narmada Fertilizers", "sector": "Fertilizers"},
        {"symbol": "CHAMBAL", "name": "Chambal Fertilizers", "sector": "Fertilizers"},
        {"symbol": "TATACHEM", "name": "Tata Chemicals", "sector": "Chemicals"},
    ],
    
    # CONSUMER DURABLES
    "consumer": [
        {"symbol": "TITAN", "name": "Titan Company", "sector": "Jewellery & Watches"},
        {"symbol": "HAVELLS", "name": "Havells India", "sector": "Electrical Equipment"},
        {"symbol": "VOLTAS", "name": "Voltas", "sector": "Consumer Durables"},
        {"symbol": "BLUESTARCO", "name": "Blue Star", "sector": "Air Conditioning"},
        {"symbol": "WHIRLPOOL", "name": "Whirlpool of India", "sector": "Consumer Appliances"},
        {"symbol": "BATAINDIA", "name": "Bata India", "sector": "Footwear"},
        {"symbol": "RELAXO", "name": "Relaxo Footwears", "sector": "Footwear"},
        {"symbol": "PAGEIND", "name": "Page Industries", "sector": "Apparel"},
        {"symbol": "TRENT", "name": "Trent Limited", "sector": "Retail - Apparel"},
        {"symbol": "ABFRL", "name": "Aditya Birla Fashion", "sector": "Apparel"},
        {"symbol": "CROMPTON", "name": "Crompton Greaves Consumer", "sector": "Electrical Equipment"},
        {"symbol": "ORIENTELEC", "name": "Orient Electric", "sector": "Electrical Equipment"},
    ],

    # US / GLOBAL TECH
    "us_tech": [
        {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "country": "US"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "country": "US"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "country": "US"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "country": "US"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "country": "US"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Auto Manufacturers", "country": "US"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology", "country": "US"},
        {"symbol": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services", "country": "US"},
        {"symbol": "AMD", "name": "Advanced Micro Devices", "sector": "Technology", "country": "US"},
        {"symbol": "INTC", "name": "Intel Corporation", "sector": "Technology", "country": "US"},
    ],

    # US / GLOBAL FINANCE & OTHERS
    "us_general": [
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services", "country": "US"},
        {"symbol": "V", "name": "Visa Inc.", "sector": "Financial Services", "country": "US"},
        {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "country": "US"},
        {"symbol": "WMT", "name": "Walmart Inc.", "sector": "Consumer Defensive", "country": "US"},
        {"symbol": "PG", "name": "Procter & Gamble", "sector": "Consumer Defensive", "country": "US"},
        {"symbol": "XOM", "name": "Exxon Mobil", "sector": "Energy", "country": "US"},
        {"symbol": "KO", "name": "Coca-Cola Company", "sector": "Consumer Defensive", "country": "US"},
        {"symbol": "DIS", "name": "Walt Disney Company", "sector": "Communication Services", "country": "US"},
    ],
}

# ... (Keep existing INDIAN_STOCKS dictionary headers)

# [EXISTING INDIAN_STOCKS DICTIONARY REMAINS UNCHANGED, I WILL REFERENCE IT IN THE FULL FILE UPDATE]
# However, since I need to modify the code AFTER the dictionary to load the CSV, I will replace the end of the file.

# ... [Assume INDIAN_STOCKS ends at line 234]

import os
import csv
import logging

logger = logging.getLogger(__name__)

# Flatten all stocks into single list
ALL_STOCKS = []
seen_symbols = set()

# 1. Add hardcoded stocks first (they have better sector data)
for sector, stocks in INDIAN_STOCKS.items():
    for stock in stocks:
        stock['sector_code'] = sector
        stock['symbol'] = stock['symbol'].upper() # Ensure uppercase
        ALL_STOCKS.append(stock)
        seen_symbols.add(stock['symbol'])

def load_csv_stocks():
    """Load additional stocks from EQUITY_L.csv"""
    csv_path = os.path.join(os.path.dirname(__file__), 'EQUITY_L.csv')
    
    if not os.path.exists(csv_path):
        logger.warning(f"Stock CSV not found at {csv_path}")
        return

    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                symbol = row.get('SYMBOL', '').strip().upper()
                name = row.get('NAME OF COMPANY', '').strip()
                
                if symbol and symbol not in seen_symbols:
                    # Add to "Others" or "General" sector
                    stock_data = {
                        "symbol": symbol,
                        "name": name,
                        "sector": "General / Unclassified", # Default
                        "sector_code": "general"
                    }
                    
                    # Add to ALL_STOCKS
                    ALL_STOCKS.append(stock_data)
                    seen_symbols.add(symbol)
                    
                    # Also add to INDIAN_STOCKS under 'general'
                    if 'general' not in INDIAN_STOCKS:
                        INDIAN_STOCKS['general'] = []
                    INDIAN_STOCKS['general'].append(stock_data)
                    
                    count += 1
            
            logger.info(f"Loaded {count} additional stocks from CSV")
            
    except Exception as e:
        logger.error(f"Error loading stock CSV: {e}")

# Load stocks on module import
load_csv_stocks()

def get_all_stocks():
    """Return all stocks as flat list"""
    return ALL_STOCKS

def get_stocks_by_sector(sector: str):
    """Return stocks for specific sector"""
    return INDIAN_STOCKS.get(sector, [])

def search_stocks(query: str):
    """Search stocks by symbol or name"""
    query = query.upper()
    results = []
    
    # Priority search: Exact match first
    for stock in ALL_STOCKS:
        if stock['symbol'] == query:
            results.insert(0, stock)
    
    # Then partial matches
    for stock in ALL_STOCKS:
        if stock in results: continue # Skip if already added
        
        if query in stock['symbol'] or query in stock['name'].upper():
            results.append(stock)
            if len(results) >= 20: 
                break
                
    return results[:20]  # Limit to 20 results

def get_sectors():
    """Return list of all sectors"""
    return list(INDIAN_STOCKS.keys())

