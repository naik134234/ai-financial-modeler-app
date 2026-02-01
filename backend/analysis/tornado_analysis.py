"""
Sensitivity Analysis & Tornado Chart
Calculates valuation impact of each assumption change
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


def calculate_sensitivity(
    base_valuation: Dict[str, Any],
    assumptions: Dict[str, float],
    variation_pct: float = 0.10
) -> Dict[str, Any]:
    """
    Calculate sensitivity of valuation to each assumption.
    
    Args:
        base_valuation: Base case valuation metrics
        assumptions: Current assumptions
        variation_pct: Percentage to vary each assumption (default 10%)
    
    Returns:
        Sensitivity data for tornado chart
    """
    base_ev = base_valuation.get('enterprise_value', 0)
    base_equity = base_valuation.get('equity_value', 0)
    base_share_price = base_valuation.get('share_price', 0)
    
    if base_ev == 0:
        base_ev = 10000  # Default for calculation
    if base_equity == 0:
        base_equity = 8000
    if base_share_price == 0:
        base_share_price = 100
    
    sensitivities = []
    
    # Define sensitivity factors for each assumption
    sensitivity_factors = {
        'revenue_growth': {
            'name': 'Revenue Growth',
            'base': assumptions.get('revenue_growth', 0.10),
            'ev_impact': 3.0,  # 3x impact on EV
            'direction': 1
        },
        'ebitda_margin': {
            'name': 'EBITDA Margin',
            'base': assumptions.get('ebitda_margin', 0.18),
            'ev_impact': 2.5,
            'direction': 1
        },
        'wacc': {
            'name': 'WACC',
            'base': assumptions.get('wacc', 0.12),
            'ev_impact': -4.0,  # Inverse relationship
            'direction': -1
        },
        'terminal_growth': {
            'name': 'Terminal Growth',
            'base': assumptions.get('terminal_growth', 0.04),
            'ev_impact': 2.0,
            'direction': 1
        },
        'tax_rate': {
            'name': 'Tax Rate',
            'base': assumptions.get('tax_rate', 0.25),
            'ev_impact': -1.5,
            'direction': -1
        },
        'capex_percent': {
            'name': 'Capex % of Revenue',
            'base': assumptions.get('capex_percent', 0.05),
            'ev_impact': -1.0,
            'direction': -1
        }
    }
    
    for key, config in sensitivity_factors.items():
        base_value = config['base']
        if base_value == 0:
            continue
            
        # Calculate upside and downside
        up_value = base_value * (1 + variation_pct)
        down_value = base_value * (1 - variation_pct)
        
        # Calculate EV impact
        ev_impact_pct = variation_pct * config['ev_impact']
        
        up_ev = base_ev * (1 + ev_impact_pct * config['direction'])
        down_ev = base_ev * (1 - ev_impact_pct * config['direction'])
        
        # Calculate share price impact (proportional to equity)
        net_debt = base_ev - base_equity
        up_equity = up_ev - net_debt
        down_equity = down_ev - net_debt
        
        up_share = base_share_price * (up_equity / base_equity) if base_equity > 0 else base_share_price
        down_share = base_share_price * (down_equity / base_equity) if base_equity > 0 else base_share_price
        
        sensitivities.append({
            'assumption': config['name'],
            'base_value': base_value,
            'up_value': up_value,
            'down_value': down_value,
            'up_ev': up_ev,
            'down_ev': down_ev,
            'up_share_price': up_share,
            'down_share_price': down_share,
            'ev_range': abs(up_ev - down_ev),
            'share_price_range': abs(up_share - down_share),
            'impact_rank': abs(ev_impact_pct)
        })
    
    # Sort by impact (highest first)
    sensitivities.sort(key=lambda x: x['ev_range'], reverse=True)
    
    return {
        'base_ev': base_ev,
        'base_equity': base_equity,
        'base_share_price': base_share_price,
        'variation_pct': variation_pct,
        'sensitivities': sensitivities,
        'tornado_data': _format_tornado_data(sensitivities, base_share_price)
    }


def _format_tornado_data(sensitivities: List[Dict], base_price: float) -> List[Dict]:
    """Format data specifically for tornado chart visualization"""
    tornado = []
    
    for s in sensitivities:
        # Calculate bars relative to base
        low_bar = min(s['up_share_price'], s['down_share_price']) - base_price
        high_bar = max(s['up_share_price'], s['down_share_price']) - base_price
        
        tornado.append({
            'name': s['assumption'],
            'low': round(s['down_share_price'], 2),
            'high': round(s['up_share_price'], 2),
            'base': round(base_price, 2),
            'low_delta': round(low_bar, 2),
            'high_delta': round(high_bar, 2),
            'range': round(s['share_price_range'], 2)
        })
    
    return tornado


def calculate_data_table(
    sensitivities: List[Dict],
    wacc_range: Tuple[float, float] = (0.08, 0.16),
    growth_range: Tuple[float, float] = (0.02, 0.06)
) -> Dict[str, Any]:
    """
    Create sensitivity data table (WACC vs Terminal Growth)
    """
    wacc_values = [round(wacc_range[0] + i * 0.02, 2) for i in range(5)]
    growth_values = [round(growth_range[0] + i * 0.01, 2) for i in range(5)]
    
    # This would normally use actual DCF calculation
    # For now, return template structure
    table = {
        'wacc_values': wacc_values,
        'growth_values': growth_values,
        'values': []
    }
    
    base_ev = 10000  # Placeholder
    for wacc in wacc_values:
        row = []
        for growth in growth_values:
            # Simplified Gordon Growth model sensitivity
            if wacc > growth:
                ev = base_ev * (0.12 / wacc) * ((0.12 - 0.04) / (wacc - growth))
                ev = min(max(ev, base_ev * 0.3), base_ev * 3)  # Cap extremes
            else:
                ev = base_ev * 3
            row.append(round(ev, 0))
        table['values'].append(row)
    
    return table
