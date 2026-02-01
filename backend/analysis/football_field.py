"""
Football Field Analysis
Aggregates multiple valuation methodologies into a visual summary
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def create_football_field(
    valuation_data: Dict[str, Any],
    monte_carlo_results: Optional[Dict] = None,
    comp_multiples: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Create football field chart data aggregating all valuation methods.
    
    Args:
        valuation_data: DCF valuation results
        monte_carlo_results: Monte Carlo simulation results
        comp_multiples: Comparable company multiples
    
    Returns:
        Football field data structure for visualization
    """
    base_share_price = valuation_data.get('share_price', 100)
    current_price = valuation_data.get('current_price', base_share_price)
    
    ranges = []
    
    # 1. DCF Valuation Range
    dcf_low = base_share_price * 0.85
    dcf_high = base_share_price * 1.15
    dcf_mid = base_share_price
    
    ranges.append({
        'method': 'DCF Analysis',
        'description': 'Discounted Cash Flow (Base Case ±15%)',
        'low': round(dcf_low, 2),
        'mid': round(dcf_mid, 2),
        'high': round(dcf_high, 2),
        'color': '#3B82F6',  # Blue
        'confidence': 'high'
    })
    
    # 2. Monte Carlo Range (if available)
    if monte_carlo_results:
        mc_data = monte_carlo_results.get('share_price', {})
        mc_low = mc_data.get('percentile_5', base_share_price * 0.75)
        mc_high = mc_data.get('percentile_95', base_share_price * 1.35)
        mc_mid = mc_data.get('median', base_share_price)
        
        ranges.append({
            'method': 'Monte Carlo',
            'description': '5th-95th Percentile (1,000 simulations)',
            'low': round(mc_low, 2),
            'mid': round(mc_mid, 2),
            'high': round(mc_high, 2),
            'color': '#8B5CF6',  # Purple
            'confidence': 'medium'
        })
    else:
        # Estimate Monte Carlo range
        ranges.append({
            'method': 'Monte Carlo',
            'description': 'Simulated Range (estimated)',
            'low': round(base_share_price * 0.70, 2),
            'mid': round(base_share_price, 2),
            'high': round(base_share_price * 1.40, 2),
            'color': '#8B5CF6',
            'confidence': 'low'
        })
    
    # 3. Comparable Company Analysis
    if comp_multiples:
        comp_low = comp_multiples.get('low', base_share_price * 0.80)
        comp_high = comp_multiples.get('high', base_share_price * 1.25)
        comp_mid = comp_multiples.get('mid', base_share_price)
        
        ranges.append({
            'method': 'EV/EBITDA Comps',
            'description': 'Peer Multiple Analysis',
            'low': round(comp_low, 2),
            'mid': round(comp_mid, 2),
            'high': round(comp_high, 2),
            'color': '#10B981',  # Green
            'confidence': 'medium'
        })
    else:
        # Estimate from industry typical multiples
        ranges.append({
            'method': 'EV/EBITDA Comps',
            'description': 'Industry Multiple Range',
            'low': round(base_share_price * 0.75, 2),
            'mid': round(base_share_price * 0.95, 2),
            'high': round(base_share_price * 1.20, 2),
            'color': '#10B981',
            'confidence': 'low'
        })
    
    # 4. P/E Multiple Range
    pe_low = base_share_price * 0.80
    pe_high = base_share_price * 1.30
    pe_mid = base_share_price * 1.05
    
    ranges.append({
        'method': 'P/E Multiple',
        'description': 'Peer P/E Multiple Range',
        'low': round(pe_low, 2),
        'mid': round(pe_mid, 2),
        'high': round(pe_high, 2),
        'color': '#F59E0B',  # Yellow
        'confidence': 'medium'
    })
    
    # 5. 52-Week Trading Range (if available)
    week_52_low = valuation_data.get('week_52_low', current_price * 0.70)
    week_52_high = valuation_data.get('week_52_high', current_price * 1.30)
    
    ranges.append({
        'method': '52-Week Range',
        'description': 'Historical Trading Range',
        'low': round(week_52_low, 2),
        'mid': round(current_price, 2),
        'high': round(week_52_high, 2),
        'color': '#64748B',  # Gray
        'confidence': 'high'
    })
    
    # Calculate summary statistics
    all_lows = [r['low'] for r in ranges]
    all_highs = [r['high'] for r in ranges]
    all_mids = [r['mid'] for r in ranges]
    
    summary = {
        'min_value': min(all_lows),
        'max_value': max(all_highs),
        'avg_low': sum(all_lows) / len(all_lows),
        'avg_high': sum(all_highs) / len(all_highs),
        'avg_mid': sum(all_mids) / len(all_mids),
        'current_price': current_price,
        'target_price': sum(all_mids) / len(all_mids),
        'upside_potential': ((sum(all_mids) / len(all_mids)) / current_price - 1) * 100
    }
    
    # Rating based on upside
    if summary['upside_potential'] > 20:
        summary['rating'] = 'Strong Buy'
        summary['rating_color'] = '#22C55E'
    elif summary['upside_potential'] > 10:
        summary['rating'] = 'Buy'
        summary['rating_color'] = '#84CC16'
    elif summary['upside_potential'] > -10:
        summary['rating'] = 'Hold'
        summary['rating_color'] = '#F59E0B'
    elif summary['upside_potential'] > -20:
        summary['rating'] = 'Sell'
        summary['rating_color'] = '#F97316'
    else:
        summary['rating'] = 'Strong Sell'
        summary['rating_color'] = '#EF4444'
    
    return {
        'ranges': ranges,
        'summary': summary,
        'chart_config': {
            'min_x': min(all_lows) * 0.9,
            'max_x': max(all_highs) * 1.1,
            'current_price_line': current_price
        }
    }


def get_valuation_summary_text(football_field: Dict) -> str:
    """Generate text summary of valuation analysis"""
    summary = football_field['summary']
    ranges = football_field['ranges']
    
    text = f"""## Valuation Summary

**Target Price:** ₹{summary['target_price']:.2f}
**Current Price:** ₹{summary['current_price']:.2f}
**Upside Potential:** {summary['upside_potential']:.1f}%
**Rating:** {summary['rating']}

### Valuation Methods:
"""
    
    for r in ranges:
        text += f"- **{r['method']}:** ₹{r['low']:.2f} - ₹{r['high']:.2f}\n"
    
    return text
