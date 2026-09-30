"""
Hedging Strategies and Portfolio Risk Management

This module provides tools for calculating hedge ratios,
portfolio Greeks, and delta-neutral hedging strategies.

Real traders use these to manage risk in their positions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List
from src.greeks import GreeksCalculator


class HedgeCalculator:
    """Calculate hedging strategies and portfolio Greeks"""
    
    def __init__(self, position_size: int, option_type: str = 'call'):
        """
        Initialize hedge calculator for a position.
        
        Args:
            position_size: Number of contracts/barrels in position
            option_type: 'call' or 'put' (what we're hedging with)
        
        Example:
            I own 10,000 barrels of oil (long position)
            I want to hedge with put options (insurance)
            HedgeCalculator(10000, 'put')
        """
        self.position_size = position_size
        self.option_type = option_type
    
    def calculate_hedge_ratio(self, greeks: Dict) -> Dict:
        """
        Calculate how many option contracts needed to hedge.
        
        Delta hedging: Use delta to determine hedge size.
        
        Delta = 0.5 means:
        - If oil price goes up $1, position gains $0.50
        - So we need enough options to offset that
        
        Args:
            greeks: Dictionary of Greeks from GreeksCalculator
        
        Returns:
            Dictionary with hedge calculations
        """
        delta = greeks['delta']
        
        # How many options to delta-hedge?
        # Hedge contracts = position size / delta
        if delta != 0:
            hedge_contracts = abs(self.position_size / delta)
        else:
            hedge_contracts = float('inf')  # Can't hedge perfectly if delta is 0
        
        # Portfolio delta after hedging
        portfolio_delta = self.position_size * delta
        
        # Gamma and Vega exposure
        gamma_exposure = self.position_size * greeks.get('gamma', 0)
        vega_exposure = self.position_size * greeks.get('vega', 0)
        theta_exposure = self.position_size * greeks.get('theta', 0)
        
        return {
            'hedge_contracts': hedge_contracts,
            'option_type': self.option_type,
            'position_size': self.position_size,
            'delta': delta,
            'portfolio_delta': portfolio_delta,
            'gamma_exposure': gamma_exposure,
            'vega_exposure': vega_exposure,
            'theta_exposure': theta_exposure
        }
    
    def portfolio_greeks(self, position_greeks: Dict, 
                        hedge_greeks: Dict, hedge_size: int) -> Dict:
        """
        Calculate combined Greeks for position + hedge.
        
        Args:
            position_greeks: Greeks of the underlying position
            hedge_greeks: Greeks of the hedge (options)
            hedge_size: Number of hedge contracts
        
        Returns:
            Portfolio Greeks after hedging
        """
        # Position Greeks
        pos_delta = self.position_size * position_greeks.get('delta', 1)  # Spot has delta=1
        pos_vega = self.position_size * position_greeks.get('vega', 0)  # Spot has vega=0
        pos_theta = self.position_size * position_greeks.get('theta', 0)
        
        # Hedge Greeks (multiply by hedge size)
        hedge_delta = hedge_size * hedge_greeks.get('delta', 0)
        hedge_gamma = hedge_size * hedge_greeks.get('gamma', 0)
        hedge_vega = hedge_size * hedge_greeks.get('vega', 0)
        hedge_theta = hedge_size * hedge_greeks.get('theta', 0)
        
        # Total portfolio
        return {
            'total_delta': pos_delta + hedge_delta,
            'total_gamma': hedge_gamma,  # Position has no gamma
            'total_vega': pos_vega + hedge_vega,
            'total_theta': pos_theta + hedge_theta,
            'is_delta_neutral': abs(pos_delta + hedge_delta) < 0.1,
            'position_delta': pos_delta,
            'hedge_delta': hedge_delta
        }


class PortfolioAnalyzer:
    """Analyze Greeks across multiple positions"""
    
    def __init__(self):
        """Initialize portfolio analyzer"""
        self.positions = []
    
    def add_position(self, name: str, quantity: int, greeks: Dict, price: float):
        """
        Add a position to the portfolio.
        
        Args:
            name: Name of the position (e.g., "Brent Crude Long")
            quantity: Number of contracts
            greeks: Greeks dictionary
            price: Current price of the position
        """
        self.positions.append({
            'name': name,
            'quantity': quantity,
            'greeks': greeks,
            'price': price,
            'market_value': quantity * price
        })
    
    def portfolio_summary(self) -> Dict:
        """
        Get total Greeks for the entire portfolio.
        
        Returns:
            Dictionary with aggregated Greeks
        """
        if not self.positions:
            return None
        
        total_delta = 0
        total_gamma = 0
        total_vega = 0
        total_theta = 0
        total_value = 0
        
        for pos in self.positions:
            qty = pos['quantity']
            greeks = pos['greeks']
            
            total_delta += qty * greeks.get('delta', 0)
            total_gamma += qty * greeks.get('gamma', 0)
            total_vega += qty * greeks.get('vega', 0)
            total_theta += qty * greeks.get('theta', 0)
            total_value += pos['market_value']
        
        return {
            'total_delta': total_delta,
            'total_gamma': total_gamma,
            'total_vega': total_vega,
            'total_theta': total_theta,
            'total_portfolio_value': total_value,
            'delta_pct': (total_delta / total_value * 100) if total_value > 0 else 0,
            'num_positions': len(self.positions)
        }
    
    def get_position_dataframe(self) -> pd.DataFrame:
        """
        Get all positions as a DataFrame for analysis.
        
        Returns:
            DataFrame with position details and Greeks
        """
        data = []
        for pos in self.positions:
            data.append({
                'Position': pos['name'],
                'Quantity': pos['quantity'],
                'Price': pos['price'],
                'Market Value': pos['market_value'],
                'Delta': pos['quantity'] * pos['greeks'].get('delta', 0),
                'Gamma': pos['quantity'] * pos['greeks'].get('gamma', 0),
                'Vega': pos['quantity'] * pos['greeks'].get('vega', 0),
                'Theta': pos['quantity'] * pos['greeks'].get('theta', 0)
            })
        
        return pd.DataFrame(data)
    
    def recommend_hedge(self, target_delta: float = 0) -> Dict:
        """
        Recommend how much to hedge to reach a target delta.
        
        Args:
            target_delta: Target portfolio delta (0 = delta-neutral)
        
        Returns:
            Hedge recommendation
        """
        summary = self.portfolio_summary()
        if summary is None:
            return None
        
        current_delta = summary['total_delta']
        delta_to_hedge = current_delta - target_delta
        
        return {
            'current_delta': current_delta,
            'target_delta': target_delta,
            'delta_to_hedge': delta_to_hedge,
            'recommendation': f"Buy {abs(delta_to_hedge):.0f} put contracts to delta-hedge" 
                            if delta_to_hedge > 0 else 
                            f"Buy {abs(delta_to_hedge):.0f} call contracts to delta-hedge"
        }


class DeltaNeutralStrategy:
    """Build and analyze delta-neutral trading strategies"""
    
    @staticmethod
    def long_call_spread(spot: float, long_strike: float, short_strike: float,
                        expiry: float, rate: float, vol: float) -> Dict:
        """
        Long call spread: Buy lower strike, sell higher strike.
        
        Benefits:
        - Limited downside (premium paid)
        - Limited upside (short call caps it)
        - Lower cost than just buying a call
        
        Args:
            All standard option parameters
        
        Returns:
            Analysis of the spread
        """
        # Long call (buy lower strike)
        long_model = GreeksCalculator(spot, long_strike, expiry, rate, vol)
        long_price = long_model.call_price()
        long_delta = long_model.delta('call')
        
        # Short call (sell higher strike)
        short_model = GreeksCalculator(spot, short_strike, expiry, rate, vol)
        short_price = short_model.call_price()
        short_delta = short_model.delta('call')
        
        # Spread Greeks
        spread_price = long_price - short_price
        spread_delta = long_delta - short_delta
        spread_gamma = long_model.gamma() - short_model.gamma()
        spread_vega = long_model.vega() - short_model.vega()
        
        return {
            'strategy': 'Long Call Spread',
            'long_strike': long_strike,
            'short_strike': short_strike,
            'net_cost': spread_price,
            'max_profit': (short_strike - long_strike) - spread_price,
            'max_loss': spread_price,
            'delta': spread_delta,
            'gamma': spread_gamma,
            'vega': spread_vega,
            'breakeven': long_strike + spread_price
        }
    
    @staticmethod
    def protective_put(spot: float, strike: float, expiry: float, 
                      rate: float, vol: float) -> Dict:
        """
        Protective put: Hold stock, buy put (insurance).
        
        This is like insurance — protects against downside.
        
        Args:
            All standard option parameters
        
        Returns:
            Analysis of the protected position
        """
        put_model = GreeksCalculator(spot, strike, expiry, rate, vol)
        put_price = put_model.put_price()
        
        # Protected position Greeks
        protected_delta = 1 + put_model.delta('put')  # Stock delta + put delta
        protected_gamma = put_model.gamma()  # Stock has no gamma
        protected_vega = put_model.vega()  # Stock has no vega
        
        return {
            'strategy': 'Protective Put (Long Stock + Long Put)',
            'stock_price': spot,
            'put_strike': strike,
            'put_cost': put_price,
            'floor_price': strike,  # Can't go below this
            'max_cost': put_price,
            'delta': protected_delta,
            'gamma': protected_gamma,
            'vega': protected_vega,
            'interpretation': 'Downside protected, upside unlimited'
        }
    