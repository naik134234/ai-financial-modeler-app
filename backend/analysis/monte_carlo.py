"""
Monte Carlo Simulation Module
Runs probability simulations for DCF valuations
"""

import logging
from typing import Dict, Any, List, Tuple
import random
import math

logger = logging.getLogger(__name__)

# Try to import numpy for faster calculations
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("numpy not installed. Using pure Python for Monte Carlo. Run: pip install numpy")


def run_monte_carlo_simulation(
    base_assumptions: Dict[str, float],
    base_valuation: Dict[str, float],
    num_simulations: int = 10000,
    variation_ranges: Dict[str, Tuple[float, float]] = None
) -> Dict[str, Any]:
    """
    Run Monte Carlo simulation on DCF valuation
    
    Args:
        base_assumptions: Base case assumptions
        base_valuation: Base case valuation metrics
        num_simulations: Number of simulations to run
        variation_ranges: Custom variation ranges for each assumption
    
    Returns:
        Dictionary with simulation results
    """
    # Default variation ranges (as % of base value)
    default_ranges = {
        'revenue_growth': (-0.30, 0.30),  # +/- 30% of base
        'ebitda_margin': (-0.20, 0.20),   # +/- 20% of base
        'terminal_growth': (-0.25, 0.25), # +/- 25% of base
        'wacc': (-0.15, 0.15),            # +/- 15% of base
    }
    
    ranges = variation_ranges or default_ranges
    
    # Base values
    base_ev = base_valuation.get('enterprise_value', 0)
    base_equity = base_valuation.get('equity_value', 0)
    base_share_price = base_valuation.get('share_price', 0)
    net_debt = base_valuation.get('net_debt', 0)
    
    if NUMPY_AVAILABLE:
        results = _run_numpy_simulation(
            base_assumptions, base_ev, base_equity, base_share_price,
            net_debt, ranges, num_simulations
        )
    else:
        results = _run_python_simulation(
            base_assumptions, base_ev, base_equity, base_share_price,
            net_debt, ranges, num_simulations
        )
    
    return results


def _run_numpy_simulation(
    base_assumptions: Dict, base_ev: float, base_equity: float,
    base_share_price: float, net_debt: float, ranges: Dict, num_simulations: int
) -> Dict[str, Any]:
    """Run simulation using numpy for speed"""
    
    # Generate random variations for each assumption
    revenue_growth_base = base_assumptions.get('revenue_growth', 0.10)
    ebitda_margin_base = base_assumptions.get('ebitda_margin', 0.18)
    terminal_growth_base = base_assumptions.get('terminal_growth', 0.04)
    wacc_base = base_assumptions.get('wacc', 0.12)
    
    # Generate normally distributed variations
    np.random.seed(42)  # For reproducibility
    
    revenue_mult = 1 + np.random.uniform(ranges['revenue_growth'][0], ranges['revenue_growth'][1], num_simulations)
    margin_mult = 1 + np.random.uniform(ranges['ebitda_margin'][0], ranges['ebitda_margin'][1], num_simulations)
    tg_mult = 1 + np.random.uniform(ranges['terminal_growth'][0], ranges['terminal_growth'][1], num_simulations)
    wacc_mult = 1 + np.random.uniform(ranges['wacc'][0], ranges['wacc'][1], num_simulations)
    
    # Simplified valuation sensitivity model
    # EV is roughly proportional to FCFF / (WACC - g)
    # FCFF is proportional to Revenue * Margin
    
    revenue_effect = revenue_mult ** 5  # 5 years of growth
    margin_effect = margin_mult
    discount_effect = wacc_base / (wacc_base * wacc_mult)
    terminal_effect = (wacc_base - terminal_growth_base) / (wacc_base * wacc_mult - terminal_growth_base * tg_mult)
    
    # Prevent extreme values from division issues
    terminal_effect = np.clip(terminal_effect, 0.1, 10)
    
    # Combined effect on valuation
    ev_multiplier = revenue_effect * margin_effect * terminal_effect * 0.7 + 0.3
    
    # Simulate valuations
    simulated_ev = base_ev * ev_multiplier
    simulated_equity = simulated_ev - net_debt if net_debt else simulated_ev * (base_equity / base_ev) if base_ev > 0 else simulated_ev
    simulated_share_price = base_share_price * (simulated_equity / base_equity) if base_equity > 0 else base_share_price
    
    # Calculate statistics
    return {
        'num_simulations': num_simulations,
        'share_price': {
            'mean': float(np.mean(simulated_share_price)),
            'median': float(np.median(simulated_share_price)),
            'std': float(np.std(simulated_share_price)),
            'min': float(np.min(simulated_share_price)),
            'max': float(np.max(simulated_share_price)),
            'percentile_5': float(np.percentile(simulated_share_price, 5)),
            'percentile_25': float(np.percentile(simulated_share_price, 25)),
            'percentile_75': float(np.percentile(simulated_share_price, 75)),
            'percentile_95': float(np.percentile(simulated_share_price, 95)),
            'histogram': _create_histogram(simulated_share_price, 20),
        },
        'enterprise_value': {
            'mean': float(np.mean(simulated_ev)),
            'median': float(np.median(simulated_ev)),
            'std': float(np.std(simulated_ev)),
            'percentile_5': float(np.percentile(simulated_ev, 5)),
            'percentile_95': float(np.percentile(simulated_ev, 95)),
        },
        'equity_value': {
            'mean': float(np.mean(simulated_equity)),
            'median': float(np.median(simulated_equity)),
            'std': float(np.std(simulated_equity)),
            'percentile_5': float(np.percentile(simulated_equity, 5)),
            'percentile_95': float(np.percentile(simulated_equity, 95)),
        },
        'probability_above_current': float(np.mean(simulated_share_price > base_share_price) * 100),
        'confidence_interval_90': (
            float(np.percentile(simulated_share_price, 5)),
            float(np.percentile(simulated_share_price, 95))
        ),
    }


def _run_python_simulation(
    base_assumptions: Dict, base_ev: float, base_equity: float,
    base_share_price: float, net_debt: float, ranges: Dict, num_simulations: int
) -> Dict[str, Any]:
    """Run simulation using pure Python"""
    
    random.seed(42)
    
    revenue_growth_base = base_assumptions.get('revenue_growth', 0.10)
    ebitda_margin_base = base_assumptions.get('ebitda_margin', 0.18)
    terminal_growth_base = base_assumptions.get('terminal_growth', 0.04)
    wacc_base = base_assumptions.get('wacc', 0.12)
    
    simulated_share_prices = []
    simulated_evs = []
    simulated_equities = []
    
    for _ in range(num_simulations):
        # Generate random multipliers
        revenue_mult = 1 + random.uniform(ranges['revenue_growth'][0], ranges['revenue_growth'][1])
        margin_mult = 1 + random.uniform(ranges['ebitda_margin'][0], ranges['ebitda_margin'][1])
        tg_mult = 1 + random.uniform(ranges['terminal_growth'][0], ranges['terminal_growth'][1])
        wacc_mult = 1 + random.uniform(ranges['wacc'][0], ranges['wacc'][1])
        
        # Simplified valuation sensitivity
        revenue_effect = revenue_mult ** 5
        margin_effect = margin_mult
        
        new_wacc = wacc_base * wacc_mult
        new_tg = terminal_growth_base * tg_mult
        
        if new_wacc > new_tg:
            terminal_effect = (wacc_base - terminal_growth_base) / (new_wacc - new_tg)
            terminal_effect = max(0.1, min(10, terminal_effect))
        else:
            terminal_effect = 1.0
        
        ev_multiplier = revenue_effect * margin_effect * terminal_effect * 0.7 + 0.3
        
        sim_ev = base_ev * ev_multiplier
        sim_equity = sim_ev * (base_equity / base_ev) if base_ev > 0 else sim_ev
        sim_price = base_share_price * (sim_equity / base_equity) if base_equity > 0 else base_share_price
        
        simulated_share_prices.append(sim_price)
        simulated_evs.append(sim_ev)
        simulated_equities.append(sim_equity)
    
    # Calculate statistics
    simulated_share_prices.sort()
    simulated_evs.sort()
    simulated_equities.sort()
    
    def percentile(data, p):
        idx = int(len(data) * p / 100)
        return data[min(idx, len(data) - 1)]
    
    def mean(data):
        return sum(data) / len(data)
    
    def std(data):
        m = mean(data)
        variance = sum((x - m) ** 2 for x in data) / len(data)
        return math.sqrt(variance)
    
    return {
        'num_simulations': num_simulations,
        'share_price': {
            'mean': mean(simulated_share_prices),
            'median': percentile(simulated_share_prices, 50),
            'std': std(simulated_share_prices),
            'min': min(simulated_share_prices),
            'max': max(simulated_share_prices),
            'percentile_5': percentile(simulated_share_prices, 5),
            'percentile_25': percentile(simulated_share_prices, 25),
            'percentile_75': percentile(simulated_share_prices, 75),
            'percentile_95': percentile(simulated_share_prices, 95),
            'histogram': _create_histogram_python(simulated_share_prices, 20),
        },
        'enterprise_value': {
            'mean': mean(simulated_evs),
            'median': percentile(simulated_evs, 50),
            'std': std(simulated_evs),
            'percentile_5': percentile(simulated_evs, 5),
            'percentile_95': percentile(simulated_evs, 95),
        },
        'equity_value': {
            'mean': mean(simulated_equities),
            'median': percentile(simulated_equities, 50),
            'std': std(simulated_equities),
            'percentile_5': percentile(simulated_equities, 5),
            'percentile_95': percentile(simulated_equities, 95),
        },
        'probability_above_current': sum(1 for p in simulated_share_prices if p > base_share_price) / num_simulations * 100,
        'confidence_interval_90': (
            percentile(simulated_share_prices, 5),
            percentile(simulated_share_prices, 95)
        ),
    }


def _create_histogram(data, num_bins: int) -> List[Dict[str, Any]]:
    """Create histogram data using numpy"""
    counts, bin_edges = np.histogram(data, bins=num_bins)
    histogram = []
    for i in range(len(counts)):
        histogram.append({
            'bin_start': float(bin_edges[i]),
            'bin_end': float(bin_edges[i + 1]),
            'count': int(counts[i]),
            'percentage': float(counts[i] / len(data) * 100)
        })
    return histogram


def _create_histogram_python(data: List[float], num_bins: int) -> List[Dict[str, Any]]:
    """Create histogram data using pure Python"""
    min_val = min(data)
    max_val = max(data)
    bin_width = (max_val - min_val) / num_bins
    
    bins = [0] * num_bins
    for value in data:
        bin_idx = min(int((value - min_val) / bin_width), num_bins - 1)
        bins[bin_idx] += 1
    
    histogram = []
    for i in range(num_bins):
        histogram.append({
            'bin_start': min_val + i * bin_width,
            'bin_end': min_val + (i + 1) * bin_width,
            'count': bins[i],
            'percentage': bins[i] / len(data) * 100
        })
    return histogram


def sensitivity_analysis(
    base_value: float,
    variable_name: str,
    variable_range: List[float],
    calculate_fn
) -> List[Dict[str, float]]:
    """
    Run sensitivity analysis on a single variable
    
    Args:
        base_value: Base value of the variable
        variable_name: Name of the variable
        variable_range: List of values to test
        calculate_fn: Function that calculates output given variable value
    
    Returns:
        List of results for each tested value
    """
    results = []
    for value in variable_range:
        output = calculate_fn(value)
        results.append({
            variable_name: value,
            'output': output,
            'change_from_base': (value - base_value) / base_value * 100 if base_value != 0 else 0
        })
    return results
