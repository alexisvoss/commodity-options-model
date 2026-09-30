"""
Backtesting Engine for Options Pricing Model

This module tests how well the Black-Scholes model performs
against real historical market data.

How it works:
1. For each date in history, we "pretend" we're at that date
2. We price an option using our model
3. We see what the option was actually worth at expiry
4. We calculate if our model was correct
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from typing import List, Dict
from src.greeks import GreeksCalculator
from src.data_handler import BrentDataHandler


class OptionBacktester:
    """Backtest option pricing model against historical data"""
    
    def __init__(self, data_handler: BrentDataHandler, risk_free_rate: float = 0.04):
        """
        Initialize the backtester.
        
        Args:
            data_handler: BrentDataHandler instance with historical data
            risk_free_rate: Annual risk-free rate (default 4%)
        """
        self.data_handler = data_handler
        self.df = data_handler.df.copy()
        self.r = risk_free_rate
        self.results = []
    
    def _get_price_at_date(self, date: str) -> float:
        """Get the spot price at a specific date"""
        try:
            return float(self.df[self.df['Date'] == date]['Close'].values[0])
        except (IndexError, TypeError):
            return None
    
    def _get_volatility_at_date(self, date: str, window: int = 30) -> float:
        """Get realized volatility at a specific date"""
        try:
            idx = self.df[self.df['Date'] == date].index[0]
            vol_series = self.data_handler.calculate_volatility(window)
            return vol_series.iloc[idx]
        except (IndexError, TypeError):
            return None
    
    def backtest_european_call(self, strike: float, days_to_expiry: int,
                              start_date: str = None) -> pd.DataFrame:
        """
        Backtest European call option pricing.
        
        How it works:
        - For each day in history (starting from start_date)
        - Price a call option using Black-Scholes
        - Wait `days_to_expiry` days
        - See what the option was actually worth at expiry
        - Calculate profit/loss
        
        Args:
            strike: Strike price of the option
            days_to_expiry: Days until option expiration
            start_date: Starting date for backtest (default: earliest available)
        
        Returns:
            DataFrame with backtest results for each trading day
        """
        print(f"\n🔄 Running backtest: {strike} strike call, {days_to_expiry} days to expiry")
        print(f"   Risk-free rate: {self.r*100:.1f}%")
        
        # Determine starting point
        if start_date is None:
            start_idx = 0
        else:
            start_idx = self.df[self.df['Date'] >= start_date].index[0]
        
        results = []
        
        # Loop through each trading day
        for i in range(start_idx, len(self.df) - days_to_expiry):
            current_row = self.df.iloc[i]
            expiry_row = self.df.iloc[i + days_to_expiry]
            
            # Current date information
            current_date = current_row['Date']
            current_price = current_row['Close']
            
            # Calculate volatility from historical data
            vol = self._get_volatility_at_date(str(current_date.date()), window=30)
            
            if vol is None or pd.isna(vol):
                continue
            
            # Time to expiry in years
            T = days_to_expiry / 365.0
            
            # Create pricing model at this date
            try:
                model = GreeksCalculator(
                    spot_price=current_price,
                    strike_price=strike,
                    time_to_expiry=T,
                    risk_free_rate=self.r,
                    volatility=vol
                )
            except ValueError:
                # Skip if inputs are invalid
                continue
            
            # Model price at this date
            model_price = model.call_price()
            delta = model.delta('call')
            gamma = model.gamma()
            vega = model.vega()
            
            # What actually happened at expiry
            expiry_date = expiry_row['Date']
            expiry_price = expiry_row['Close']
            
            # Intrinsic value at expiry (what the option was actually worth)
            realized_payoff = max(expiry_price - strike, 0)
            
            # Profit/Loss: if we sold the call at model price and bought it back at expiry
            profit_loss = model_price - realized_payoff
            
            # Store result
            results.append({
                'date': current_date,
                'spot_price': current_price,
                'strike': strike,
                'model_price': model_price,
                'expiry_date': expiry_date,
                'expiry_price': expiry_price,
                'realized_payoff': realized_payoff,
                'profit_loss': profit_loss,
                'profit_loss_pct': (profit_loss / model_price * 100) if model_price > 0 else 0,
                'delta': delta,
                'gamma': gamma,
                'vega': vega,
                'volatility': vol
            })
        
        self.results = pd.DataFrame(results)
        return self.results
    
    def backtest_european_put(self, strike: float, days_to_expiry: int,
                             start_date: str = None) -> pd.DataFrame:
        """
        Backtest European put option pricing.
        
        Similar to call backtest but for put options.
        """
        print(f"\n🔄 Running backtest: {strike} strike put, {days_to_expiry} days to expiry")
        print(f"   Risk-free rate: {self.r*100:.1f}%")
        
        # Determine starting point
        if start_date is None:
            start_idx = 0
        else:
            start_idx = self.df[self.df['Date'] >= start_date].index[0]
        
        results = []
        
        # Loop through each trading day
        for i in range(start_idx, len(self.df) - days_to_expiry):
            current_row = self.df.iloc[i]
            expiry_row = self.df.iloc[i + days_to_expiry]
            
            current_date = current_row['Date']
            current_price = current_row['Close']
            
            vol = self._get_volatility_at_date(str(current_date.date()), window=30)
            
            if vol is None or pd.isna(vol):
                continue
            
            T = days_to_expiry / 365.0
            
            try:
                model = GreeksCalculator(
                    spot_price=current_price,
                    strike_price=strike,
                    time_to_expiry=T,
                    risk_free_rate=self.r,
                    volatility=vol
                )
            except ValueError:
                continue
            
            model_price = model.put_price()
            delta = model.delta('put')
            
            expiry_date = expiry_row['Date']
            expiry_price = expiry_row['Close']
            
            # Intrinsic value of put at expiry
            realized_payoff = max(strike - expiry_price, 0)
            
            profit_loss = model_price - realized_payoff
            
            results.append({
                'date': current_date,
                'spot_price': current_price,
                'strike': strike,
                'model_price': model_price,
                'expiry_date': expiry_date,
                'expiry_price': expiry_price,
                'realized_payoff': realized_payoff,
                'profit_loss': profit_loss,
                'profit_loss_pct': (profit_loss / model_price * 100) if model_price > 0 else 0,
                'delta': delta,
                'volatility': vol
            })
        
        self.results = pd.DataFrame(results)
        return self.results
    
    def get_performance_metrics(self) -> Dict:
        """
        Calculate performance metrics from backtest results.
        
        Metrics:
        - Total P&L: Sum of all profits/losses
        - Win Rate: % of trades that were profitable
        - Sharpe Ratio: Risk-adjusted returns
        - Max Drawdown: Largest peak-to-trough decline
        """
        if len(self.results) == 0:
            return None
        
        pl = self.results['profit_loss']
        
        total_pl = pl.sum()
        total_trades = len(pl)
        winning_trades = (pl > 0).sum()
        losing_trades = (pl < 0).sum()
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Calculate Sharpe ratio
        daily_returns = pl / self.results['model_price']
        mean_return = daily_returns.mean()
        std_return = daily_returns.std()
        sharpe_ratio = (mean_return / std_return * np.sqrt(252)) if std_return > 0 else 0
        
        # Calculate max drawdown
        cumsum_pl = pl.cumsum()
        running_max = cumsum_pl.expanding().max()
        drawdown = cumsum_pl - running_max
        max_drawdown = drawdown.min()
        
        return {
            'total_pl': total_pl,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': pl[pl > 0].mean() if winning_trades > 0 else 0,
            'avg_loss': pl[pl < 0].mean() if losing_trades > 0 else 0,
            'mean_pl': pl.mean(),
            'std_pl': pl.std(),
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'sortino_ratio': (mean_return / daily_returns[daily_returns < 0].std() * np.sqrt(252)) 
                            if len(daily_returns[daily_returns < 0]) > 0 else 0
        }