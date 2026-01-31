"""
Damodaran Data Fetcher
Fetches real financial data from Prof. Aswath Damodaran's publicly available datasets
Source: https://pages.stern.nyu.edu/~adamodar/
"""

import logging
import requests
from typing import Dict, Any, Optional, List, Union
from io import BytesIO
import os
from datetime import datetime, timedelta
import json
import xlrd

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache_damodaran")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_EXPIRY_DAYS = 7  # Refresh data weekly

# Damodaran dataset URLs for India
DAMODARAN_URLS = {
    # Risk & Discount Rates
    "beta_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/betaIndia.xls",
    "wacc_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/waccIndia.xls",
    "total_beta_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/totalbetaIndia.xls",
    
    # Margins & Profitability
    "margin_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/marginIndia.xls",
    "roe_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/roeIndia.xls",
    "eva_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/EVAIndia.xls",
    
    # Capital Structure
    "capex_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/capexIndia.xls",
    "debt_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/dbtfundIndia.xls",
    "debt_details_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/debtdetailsIndia.xls",
    
    # Valuation Multiples
    "pe_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/peIndia.xls",
    "pbv_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/pbvIndia.xls",
    "evebitda_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/vebitdaIndia.xls",
    "evs_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/psIndia.xls",
    
    # Growth & Dividends
    "growth_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/histgrIndia.xls",
    "dividend_india": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/divfundIndia.xls",
    
    # Global data
    "country_erp": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/ctryprem.xls",
    "country_tax": "https://pages.stern.nyu.edu/~adamodar/pc/datasets/countrytaxrates.xls",
    "ratings_spreads": "https://pages.stern.nyu.edu/~adamodar/pc/ratings.xls",
}


def _get_cache_path(dataset_name: str) -> str:
    """Get cache file path for a dataset"""
    return os.path.join(CACHE_DIR, f"{dataset_name}.json")


def _is_cache_valid(cache_path: str) -> bool:
    """Check if cache is still valid"""
    if not os.path.exists(cache_path):
        return False
    
    mod_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
    return datetime.now() - mod_time < timedelta(days=CACHE_EXPIRY_DAYS)


def _fetch_excel_data(url: str, dataset_name: str) -> List[List[Any]]:
    """Fetch Excel data from Damodaran's website using xlrd"""
    cache_path = _get_cache_path(dataset_name)
    
    # Try cache first
    if _is_cache_valid(cache_path):
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    
    # Fetch from web
    try:
        logger.info(f"Fetching Damodaran data: {dataset_name}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Read Excel file using xlrd
        workbook = xlrd.open_workbook(file_contents=response.content)
        sheet = workbook.sheet_by_index(0)
        
        data = []
        for row_idx in range(sheet.nrows):
            row = []
            for col_idx in range(sheet.ncols):
                row.append(sheet.cell_value(row_idx, col_idx))
            data.append(row)
        
        # Cache the data
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Could not cache {dataset_name}: {e}")
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching {dataset_name}: {e}")
        return []


def get_industry_beta(industry: str) -> Dict[str, float]:
    """
    Get industry beta data from Damodaran
    """
    rows = _fetch_excel_data(DAMODARAN_URLS["beta_india"], "beta_india")
    
    if not rows:
        # Fallback defaults
        return {
            "unlevered_beta": 0.85,
            "levered_beta": 1.0,
            "correlation": 0.25,
            "std_dev": 0.40,
        }
    
    # Find matching industry
    industry_lower = industry.lower()
    matched = None
    
    # Skip potential header rows (check if first cell looks like an industry)
    for row in rows:
        if not row or len(row) < 1: continue
        row_industry = str(row[0]).lower() if row[0] is not None else ""
        if industry_lower in row_industry or row_industry in industry_lower:
            matched = row
            break
    
    if matched is None:
        # Use market average (typically the last or second to last row)
        matched = rows[-1] if rows else None
    
    if matched is not None:
        try:
            # Indices for betaIndia.xls:
            # 0: Industry, 1: Number of firms, 2: Average beta, 3: Correlation with market, 
            # 5: Unlevered beta, 7: Levered beta
            return {
                "unlevered_beta": float(matched[5]) if len(matched) > 5 and matched[5] != '' else 0.85,
                "levered_beta": float(matched[7]) if len(matched) > 7 and matched[7] != '' else 1.0,
                "correlation": float(matched[3]) if len(matched) > 3 and matched[3] != '' else 0.25,
                "std_dev": float(matched[2]) if len(matched) > 2 and matched[2] != '' else 0.40,
            }
        except (IndexError, ValueError):
            pass
    
    return {
        "unlevered_beta": 0.85,
        "levered_beta": 1.0,
        "correlation": 0.25,
        "std_dev": 0.40,
    }


def get_industry_wacc(industry: str) -> Dict[str, float]:
    """
    Get industry WACC components from Damodaran
    """
    rows = _fetch_excel_data(DAMODARAN_URLS["wacc_india"], "wacc_india")
    
    if not rows:
        return {
            "cost_of_equity": 0.14,
            "cost_of_debt": 0.09,
            "wacc": 0.11,
            "debt_ratio": 0.25,
        }
    
    industry_lower = industry.lower()
    matched = None
    
    for row in rows:
        if not row or len(row) < 1: continue
        row_industry = str(row[0]).lower() if row[0] is not None else ""
        if industry_lower in row_industry or row_industry in industry_lower:
            matched = row
            break
    
    if matched is None:
        matched = rows[-1] if rows else None
    
    if matched is not None:
        try:
            return {
                "cost_of_equity": float(matched[6]) if len(matched) > 6 and matched[6] != '' else 0.14,
                "cost_of_debt": float(matched[7]) if len(matched) > 7 and matched[7] != '' else 0.09,
                "wacc": float(matched[8]) if len(matched) > 8 and matched[8] != '' else 0.11,
                "debt_ratio": float(matched[4]) if len(matched) > 4 and matched[4] != '' else 0.25,
            }
        except (IndexError, ValueError):
            pass
    
    return {
        "cost_of_equity": 0.14,
        "cost_of_debt": 0.09,
        "wacc": 0.11,
        "debt_ratio": 0.25,
    }


def get_industry_margins(industry: str) -> Dict[str, float]:
    """
    Get industry profit margins from Damodaran
    """
    rows = _fetch_excel_data(DAMODARAN_URLS["margin_india"], "margin_india")
    
    if not rows:
        return {
            "gross_margin": 0.35,
            "ebitda_margin": 0.18,
            "operating_margin": 0.15,
            "net_margin": 0.10,
            "pre_tax_margin": 0.12,
        }
    
    industry_lower = industry.lower()
    matched = None
    
    for row in rows:
        if not row or len(row) < 1: continue
        row_industry = str(row[0]).lower() if row[0] is not None else ""
        if industry_lower in row_industry or row_industry in industry_lower:
            matched = row
            break
    
    if matched is None:
        matched = rows[-1] if rows else None
    
    if matched is not None:
        try:
            return {
                "gross_margin": float(matched[1]) if len(matched) > 1 and matched[1] != '' else 0.35,
                "ebitda_margin": float(matched[3]) if len(matched) > 3 and matched[3] != '' else 0.18,
                "operating_margin": float(matched[4]) if len(matched) > 4 and matched[4] != '' else 0.15,
                "net_margin": float(matched[6]) if len(matched) > 6 and matched[6] != '' else 0.10,
                "pre_tax_margin": float(matched[5]) if len(matched) > 5 and matched[5] != '' else 0.12,
            }
        except (IndexError, ValueError):
            pass
    
    return {
        "gross_margin": 0.35,
        "ebitda_margin": 0.18,
        "operating_margin": 0.15,
        "net_margin": 0.10,
        "pre_tax_margin": 0.12,
    }


def get_industry_capex(industry: str) -> Dict[str, float]:
    """
    Get industry capex and reinvestment data from Damodaran
    """
    rows = _fetch_excel_data(DAMODARAN_URLS["capex_india"], "capex_india")
    
    if not rows:
        return {
            "capex_to_sales": 0.06,
            "capex_to_depreciation": 1.5,
            "reinvestment_rate": 0.40,
            "sales_to_capital": 1.2,
        }
    
    industry_lower = industry.lower()
    matched = None
    
    for row in rows:
        if not row or len(row) < 1: continue
        row_industry = str(row[0]).lower() if row[0] is not None else ""
        if industry_lower in row_industry or row_industry in industry_lower:
            matched = row
            break
    
    if matched is None:
        matched = rows[-1] if rows else None
    
    if matched is not None:
        try:
            return {
                "capex_to_sales": float(matched[2]) if len(matched) > 2 and matched[2] != '' else 0.06,
                "capex_to_depreciation": float(matched[3]) if len(matched) > 3 and matched[3] != '' else 1.5,
                "reinvestment_rate": float(matched[5]) if len(matched) > 5 and matched[5] != '' else 0.40,
                "sales_to_capital": float(matched[6]) if len(matched) > 6 and matched[6] != '' else 1.2,
            }
        except (IndexError, ValueError):
            pass
    
    return {
        "capex_to_sales": 0.06,
        "capex_to_depreciation": 1.5,
        "reinvestment_rate": 0.40,
        "sales_to_capital": 1.2,
    }


def get_industry_multiples(industry: str) -> Dict[str, float]:
    """
    Get industry valuation multiples from Damodaran
    """
    pe_rows = _fetch_excel_data(DAMODARAN_URLS["pe_india"], "pe_india")
    pbv_rows = _fetch_excel_data(DAMODARAN_URLS["pbv_india"], "pbv_india")
    evebitda_rows = _fetch_excel_data(DAMODARAN_URLS["evebitda_india"], "evebitda_india")
    
    result = {
        "pe_ratio": 20.0,
        "pb_ratio": 2.5,
        "ev_ebitda": 12.0,
        "ev_sales": 2.0,
    }
    
    industry_lower = industry.lower()
    
    # P/E Ratio
    if pe_rows:
        for row in pe_rows:
            if not row or len(row) < 1: continue
            row_industry = str(row[0]).lower() if row[0] is not None else ""
            if industry_lower in row_industry or row_industry in industry_lower:
                try:
                    result["pe_ratio"] = float(row[3]) if len(row) > 3 and row[3] != '' else 20.0
                except (IndexError, ValueError):
                    pass
                break
    
    # P/B Ratio
    if pbv_rows:
        for row in pbv_rows:
            if not row or len(row) < 1: continue
            row_industry = str(row[0]).lower() if row[0] is not None else ""
            if industry_lower in row_industry or row_industry in industry_lower:
                try:
                    result["pb_ratio"] = float(row[1]) if len(row) > 1 and row[1] != '' else 2.5
                except (IndexError, ValueError):
                    pass
                break
    
    # EV/EBITDA
    if evebitda_rows:
        for row in evebitda_rows:
            if not row or len(row) < 1: continue
            row_industry = str(row[0]).lower() if row[0] is not None else ""
            if industry_lower in row_industry or row_industry in industry_lower:
                try:
                    result["ev_ebitda"] = float(row[1]) if len(row) > 1 and row[1] != '' else 12.0
                except (IndexError, ValueError):
                    pass
                break
    
    return result


def get_industry_growth(industry: str) -> Dict[str, float]:
    """
    Get industry historical growth rates from Damodaran
    """
    rows = _fetch_excel_data(DAMODARAN_URLS["growth_india"], "growth_india")
    
    if not rows:
        return {
            "revenue_growth_1y": 0.10,
            "revenue_growth_5y": 0.12,
            "eps_growth_5y": 0.15,
            "expected_growth": 0.12,
        }
    
    industry_lower = industry.lower()
    matched = None
    
    for row in rows:
        if not row or len(row) < 1: continue
        row_industry = str(row[0]).lower() if row[0] is not None else ""
        if industry_lower in row_industry or row_industry in industry_lower:
            matched = row
            break
    
    if matched is None:
        matched = rows[-1] if rows else None
    
    if matched is not None:
        try:
            return {
                "revenue_growth_1y": float(matched[1]) if len(matched) > 1 and matched[1] != '' else 0.10,
                "revenue_growth_5y": float(matched[3]) if len(matched) > 3 and matched[3] != '' else 0.12,
                "eps_growth_5y": float(matched[5]) if len(matched) > 5 and matched[5] != '' else 0.15,
                "expected_growth": float(matched[6]) if len(matched) > 6 and matched[6] != '' else 0.12,
            }
        except (IndexError, ValueError):
            pass
    
    return {
        "revenue_growth_1y": 0.10,
        "revenue_growth_5y": 0.12,
        "eps_growth_5y": 0.15,
        "expected_growth": 0.12,
    }


def get_india_erp() -> Dict[str, float]:
    """
    Get India-specific equity risk premium from Damodaran
    """
    rows = _fetch_excel_data(DAMODARAN_URLS["country_erp"], "country_erp")
    
    # India-specific defaults based on Damodaran's typical estimates
    result = {
        "risk_free_rate": 0.07,  # India 10Y G-Sec
        "equity_risk_premium": 0.0473,  # Mature market ERP
        "country_risk_premium": 0.0228,  # India CRP
        "total_erp": 0.07,  # Total ERP for India
    }
    
    if rows:
        for row in rows:
            if not row or len(row) < 1: continue
            country = str(row[0]).lower() if row[0] is not None else ""
            if "india" in country:
                try:
                    # Country risk premium
                    if len(row) > 4 and row[4] != '':
                        result["country_risk_premium"] = float(row[4])
                    # Total ERP
                    if len(row) > 5 and row[5] != '':
                        result["total_erp"] = float(row[5])
                except (IndexError, ValueError):
                    pass
                break
    
    return result


def get_india_tax_rate() -> float:
    """Get India corporate tax rate from Damodaran"""
    rows = _fetch_excel_data(DAMODARAN_URLS["country_tax"], "country_tax")
    
    if rows:
        for row in rows:
            if not row or len(row) < 1: continue
            country = str(row[0]).lower() if row[0] is not None else ""
            if "india" in country:
                try:
                    return float(row[1]) if len(row) > 1 and row[1] != '' else 0.25
                except (IndexError, ValueError):
                    pass
    
    return 0.25  # Default India corporate tax


def get_all_industry_data(industry: str) -> Dict[str, Any]:
    """
    Get all Damodaran data for an industry in one call
    """
    beta = get_industry_beta(industry)
    wacc = get_industry_wacc(industry)
    margins = get_industry_margins(industry)
    capex = get_industry_capex(industry)
    multiples = get_industry_multiples(industry)
    growth = get_industry_growth(industry)
    erp = get_india_erp()
    tax_rate = get_india_tax_rate()
    
    return {
        "industry": industry,
        "source": "Damodaran Online (pages.stern.nyu.edu/~adamodar/)",
        "last_updated": datetime.now().isoformat(),
        
        # Risk parameters
        "beta": beta,
        
        # Cost of capital
        "wacc": wacc,
        
        # Margins
        "margins": margins,
        
        # Capex & Reinvestment
        "capex": capex,
        
        # Valuation multiples
        "multiples": multiples,
        
        # Growth rates
        "growth": growth,
        
        # Country-specific
        "erp": erp,
        "tax_rate": tax_rate,
        
        # Consolidated assumptions for model
        "model_assumptions": {
            "revenue_growth": growth.get("expected_growth", 0.10),
            "gross_margin": margins.get("gross_margin", 0.35),
            "ebitda_margin": margins.get("ebitda_margin", 0.18),
            "operating_margin": margins.get("operating_margin", 0.15),
            "net_margin": margins.get("net_margin", 0.10),
            "capex_pct": capex.get("capex_to_sales", 0.06),
            "da_pct": capex.get("capex_to_sales", 0.06) / capex.get("capex_to_depreciation", 1.5),
            "beta": beta.get("levered_beta", 1.0),
            "cost_of_equity": wacc.get("cost_of_equity", 0.14),
            "cost_of_debt": wacc.get("cost_of_debt", 0.09),
            "wacc": wacc.get("wacc", 0.11),
            "debt_ratio": wacc.get("debt_ratio", 0.25),
            "tax_rate": tax_rate,
            "risk_free_rate": erp.get("risk_free_rate", 0.07),
            "equity_risk_premium": erp.get("total_erp", 0.07),
            "terminal_growth": 0.04,  # Conservative terminal growth
            "pe_ratio": multiples.get("pe_ratio", 20.0),
            "ev_ebitda": multiples.get("ev_ebitda", 12.0),
        }
    }


def list_available_industries() -> List[str]:
    """
    Get list of industries available in Damodaran's data
    """
    rows = _fetch_excel_data(DAMODARAN_URLS["beta_india"], "beta_india")
    
    if not rows:
        # Return common industries
        return [
            "Oil/Gas (Production and Exploration)",
            "Computer Software",
            "Banks (Regional)",
            "Auto Parts",
            "Telecom Services",
            "Steel",
            "Pharmaceuticals",
            "Real Estate (Development)",
            "Power",
            "Chemical (Basic)",
        ]
    
    industries = []
    for row in rows:
        if not row or len(row) < 1: continue
        industry = row[0]
        if industry and isinstance(industry, str) and len(industry) > 2:
            industries.append(industry)
    
    return industries[1:-1] if len(industries) > 2 else industries  # Skip header/total rows


# Industry name mapping from Yahoo Finance to Damodaran
INDUSTRY_MAPPING = {
    # Technology
    "software": "Computers/Peripherals",
    "information technology services": "Computer Services",
    "internet content & information": "Entertainment",
    "semiconductors": "Semiconductor",
    "electronic components": "Electronics (Consumer & Office)",
    
    # Financial
    "banks": "Banks (Regional)",
    "banking": "Banks (Regional)",
    "insurance": "Insurance (General)",
    "asset management": "Financial Svcs. (Non-bank & Insurance)",
    
    # Energy
    "oil & gas": "Oil/Gas (Production and Exploration)",
    "renewable energy": "Power",
    "utilities": "Utility (General)",
    
    # Consumer
    "automobiles": "Auto Parts",
    "auto manufacturers": "Auto Parts",
    "consumer electronics": "Electronics (Consumer & Office)",
    "retail": "Retail (General)",
    
    # Healthcare
    "pharmaceuticals": "Drugs (Pharmaceutical)",
    "drug manufacturers": "Drugs (Pharmaceutical)",
    "biotechnology": "Drugs (Biotechnology)",
    "healthcare": "Healthcare Products",
    
    # Industrial
    "steel": "Steel",
    "metals & mining": "Metals & Mining",
    "aerospace": "Aerospace/Defense",
    "construction": "Construction Supplies",
    "chemicals": "Chemical (Basic)",
    
    # Telecom
    "telecom services": "Telecom Services",
    "telecommunications": "Telecom Services",
    
    # Real Estate
    "real estate": "Real Estate (Development)",
    "reits": "R.E.I.T.",
}


def map_yahoo_industry(yahoo_industry: str) -> str:
    """Map Yahoo Finance industry to Damodaran industry classification"""
    yahoo_lower = yahoo_industry.lower()
    
    for key, damodaran_industry in INDUSTRY_MAPPING.items():
        if key in yahoo_lower:
            return damodaran_industry
    
    # If no match, return as-is
    return yahoo_industry
