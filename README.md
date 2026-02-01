---
title: AI Financial Modeler
emoji: 📈
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
---

# AI Financial Modeling Platform

An AI-powered platform for generating institutional-grade Excel financial models for Indian stocks. Built with FastAPI, Next.js, and Google Gemini AI.

![Financial Modeler Screenshot](screenshot.png)

[![Deploy on Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-on-spaces-sm.svg)](https://huggingface.co/spaces/new?template=docker)

## 🚀 Features

### Core Capabilities
- **AI-Powered Industry Classification**: Uses Google Gemini AI to classify companies and select appropriate model templates
- **Real Excel Formulas**: Generated models use linked formulas, not static values - fully editable
- **150+ Indian Stocks**: Comprehensive database covering Power, Banking, IT, Pharma, FMCG, Auto, and more
- **Raw Data Input**: Generate models from your own financial data without scraping

### Advanced Financial Modeling
- **Three-Statement Model**: Income Statement, Balance Sheet, Cash Flow - all linked
- **DCF Valuation**: WACC calculation, FCFF projections, terminal value, implied share price
- **Sensitivity Analysis**: WACC vs Terminal Growth, Revenue vs EBITDA Margin tables
- **Scenario Analysis**: Bear/Base/Bull case projections with IRR calculation
- **Dashboard with Charts**: Revenue & EBITDA bars, margin trends, net income charts

### Industry-Specific Templates
- **Power Sector**: PLF tracking, fuel costs, tariff analysis
- **Banking**: NIM analysis, credit costs, CASA ratios
- **IT Services**: Utilization, billing rates, offshore mix
- **Pharmaceuticals**: R&D intensity, ANDA filings
- **FMCG**: Distribution metrics, brand spending
- And more!

## 📋 Requirements

- Python 3.9+
- Node.js 18+
- Google Gemini API Key (optional, uses templates as fallback)

## 🛠️ Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## 🚀 Running the Application

### Start Backend
```bash
cd backend
python main.py
# Server starts at http://127.0.0.1:8000
```

### Start Frontend
```bash
cd frontend
npm run dev
# App opens at http://localhost:3000
```

## 📡 API Endpoints

### Company Information
```bash
GET /api/company/{symbol}?exchange=NSE
```
Returns company name, sector, market cap, and current price.

### Stock Database
```bash
GET /api/stocks              # All 172 stocks
GET /api/stocks?sector=power # Filter by sector
GET /api/stocks/search/TCS   # Search by symbol or name
GET /api/sectors             # List all 14 sectors
```

### Model Generation
```bash
POST /api/model/generate
{
    "symbol": "ADANIPOWER",
    "exchange": "NSE",
    "forecast_years": 5,
    "model_types": ["three_statement", "dcf"]
}
```

### Raw Data Model Generation
```bash
POST /api/model/generate-raw
{
    "company_name": "My Company Ltd",
    "industry": "general",
    "forecast_years": 5,
    "historical_data": {
        "income_statement": {
            "revenue": 10000,
            "ebitda": 2500,
            "net_income": 1500
        },
        "balance_sheet": {
            "total_assets": 20000,
            "total_liabilities": 8000
        }
    },
    "assumptions": {
        "revenue_growth": 0.10,
        "ebitda_margin": 0.25,
        "tax_rate": 0.25
    }
}
```

### Job Status
```bash
GET /api/job/{job_id}
```

### Download Model
```bash
GET /api/download/{job_id}
```

## 📊 Excel Model Structure

Each generated model contains:

| Sheet | Description |
|-------|-------------|
| Cover | Company summary, key metrics, model info |
| Summary | Navigation links, key outputs |
| Assumptions | Named ranges for all inputs (yellow cells) |
| Income_Statement | 5Y historical + 5Y forecast P&L |
| Balance_Sheet | Assets, liabilities, equity with balance check |
| Cash_Flow | Operating, investing, financing activities |
| Valuation | DCF model with WACC, terminal value, equity bridge |
| Sensitivity | WACC vs TGR, Revenue vs EBITDA sensitivity tables |
| Scenarios | Bear/Base/Bull case analysis with IRR |
| Dashboard | Charts for Revenue, EBITDA, Margins, Net Income |

## 🏭 Supported Sectors (14 Categories)

1. **Power & Utilities** - ADANIPOWER, NTPC, TATAPOWER, POWERGRID...
2. **Banking** - HDFCBANK, ICICIBANK, SBIN, KOTAKBANK...
3. **IT Services** - TCS, INFY, WIPRO, HCLTECH, TECHM...
4. **Pharmaceuticals** - SUNPHARMA, DRREDDY, CIPLA, LUPIN...
5. **FMCG** - HINDUNILVR, ITC, NESTLEIND, BRITANNIA...
6. **Automobiles** - MARUTI, TATAMOTORS, M&M, HEROMOTOCO...
7. **Metals & Mining** - TATASTEEL, HINDALCO, JSWSTEEL, VEDL...
8. **Oil & Gas** - RELIANCE, ONGC, IOC, BPCL...
9. **Cement** - ULTRACEMCO, SHREECEM, ACC, AMBUJACEM...
10. **Infrastructure** - L&T, ADANIENT, ADANIPORTS, GMRINFRA...
11. **NBFC** - BAJFINANCE, BAJAJFINSV, SBICARD, MUTHOOTFIN...
12. **Telecom** - BHARTIARTL, IDEA...
13. **Chemicals** - PIDILITIND, UPL, CLEAN...
14. **Consumer Durables** - TITAN, HAVELLS, VOLTAS, CROMPTON...

## 🎨 Frontend Features

- **Modern Dark Theme**: Glassmorphism effects, gradient accents
- **Stock Browser**: Search, filter by sector, click to select
- **Raw Data Input**: Enter your own financial data and assumptions
- **Real-time Progress**: Live status updates during generation
- **Model Preview**: See included features before downloading

## 🔧 Configuration

### Environment Variables

```env
# Required for AI features (optional - falls back to templates)
GEMINI_API_KEY=your_gemini_api_key

# Optional
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```

### Model Assumptions (Editable in Excel)

The Assumptions sheet contains named ranges for:
- Revenue Growth Rate
- EBITDA Margin
- Depreciation % of Revenue
- Tax Rate
- Working Capital Days
- CapEx % of Revenue
- WACC, Risk-Free Rate, Equity Risk Premium
- Terminal Growth Rate
- And more...

## 📁 Project Structure

```
ai-financial-modeler/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── requirements.txt     # Python dependencies
│   ├── data/
│   │   ├── yahoo_finance.py # Yahoo Finance data collector
│   │   ├── screener_scraper.py # Screener.in scraper
│   │   └── stock_database.py   # 172 Indian stocks database
│   ├── agents/
│   │   ├── industry_classifier.py # AI industry classification
│   │   ├── financial_modeler.py   # Model structure design
│   │   └── qa_validator.py        # Model validation
│   ├── excel/
│   │   └── generator.py     # Excel model generator
│   └── output/              # Generated Excel files
└── frontend/
    ├── app/
    │   ├── page.tsx         # Main page with stock selection
    │   ├── layout.tsx       # Root layout
    │   └── globals.css      # Dark theme styles
    ├── package.json
    └── tailwind.config.js   # Custom theme config
```

## 🤝 Contributing

Pull requests are welcome! Please ensure:
1. Code follows existing style patterns
2. New features include appropriate tests
3. Documentation is updated

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Yahoo Finance for financial data
- Screener.in for detailed Indian stock data
- Google Gemini AI for intelligent classification
- openpyxl for Excel generation
