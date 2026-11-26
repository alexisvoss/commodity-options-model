"""
Backtesting Engine for Options Pricing Model

This module tests how well the Black-76 model (for commodity futures)
performs against real historical market data.

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
        - Price a call option using Black-76
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

    def backtest_european_call_delta_hedged(self, strike: float, days_to_expiry: int,
                                           start_date: str = None) -> pd.DataFrame:
        """
        Backtest a delta-hedged short call strategy (STATIC HEDGE).

        Strategy:
        1. Sell a call at model price
        2. Buy delta-equivalent futures to hedge (set once)
        3. Hold for days_to_expiry days
        4. Close both positions at expiration

        If hedged P&L ≈ 0: The edge was directional (not mispricing)
        If hedged P&L > 0: The edge came from mispricing
        """
        print(f"\n🔄 Running DELTA-HEDGED backtest: {strike} strike call, {days_to_expiry} days to expiry")
        print(f"   Risk-free rate: {self.r*100:.1f}%")
        print(f"   Strategy: Sell call + buy delta-equivalent futures (STATIC)")

        if start_date is None:
            start_idx = 0
        else:
            start_idx = self.df[self.df['Date'] >= start_date].index[0]

        results = []

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

            model_price = model.call_price()
            delta = model.delta('call')

            expiry_date = expiry_row['Date']
            expiry_price = expiry_row['Close']

            realized_payoff = max(expiry_price - strike, 0)

            call_pnl = model_price - realized_payoff
            futures_pnl = (expiry_price - current_price) * delta
            hedged_pnl = call_pnl + futures_pnl
            unhedged_pnl = call_pnl

            results.append({
                'date': current_date,
                'spot_price': current_price,
                'strike': strike,
                'model_price': model_price,
                'delta': delta,
                'expiry_date': expiry_date,
                'expiry_price': expiry_price,
                'realized_payoff': realized_payoff,
                'unhedged_pnl': unhedged_pnl,
                'futures_pnl': futures_pnl,
                'hedged_pnl': hedged_pnl,
                'hedged_pnl_pct': (hedged_pnl / model_price * 100) if model_price > 0 else 0,
                'volatility': vol
            })

        self.results_hedged = pd.DataFrame(results)
        return self.results_hedged

    def get_hedged_performance_metrics(self) -> Dict:
        """
        Calculate performance metrics for delta-hedged strategy.

        Key insight: If hedged P&L ≈ 0, the edge was directional.
                     If hedged P&L > 0, there was real mispricing.
        """
        if not hasattr(self, 'results_hedged') or len(self.results_hedged) == 0:
            return None

        hedged_pl = self.results_hedged['hedged_pnl']
        unhedged_pl = self.results_hedged['unhedged_pnl']

        total_hedged_pl = hedged_pl.sum()
        total_unhedged_pl = unhedged_pl.sum()
        total_trades = len(hedged_pl)
        winning_hedged = (hedged_pl > 0).sum()

        hedged_returns = hedged_pl / self.results_hedged['model_price']
        mean_hedged_return = hedged_returns.mean()
        std_hedged_return = hedged_returns.std()
        sharpe_hedged = (mean_hedged_return / std_hedged_return * np.sqrt(252)) if std_hedged_return > 0 else 0

        cumsum_hedged = hedged_pl.cumsum()
        running_max = cumsum_hedged.expanding().max()
        drawdown = cumsum_hedged - running_max
        max_drawdown_hedged = drawdown.min()

        return {
            'total_trades': total_trades,
            'unhedged_total_pl': total_unhedged_pl,
            'hedged_total_pl': total_hedged_pl,
            'pl_reduction': total_unhedged_pl - total_hedged_pl,
            'winning_trades_hedged': winning_hedged,
            'win_rate_hedged': winning_hedged / total_trades if total_trades > 0 else 0,
            'avg_hedged_pl': hedged_pl.mean(),
            'std_hedged_pl': hedged_pl.std(),
            'sharpe_hedged': sharpe_hedged,
            'max_drawdown_hedged': max_drawdown_hedged,
            'insight': self._interpret_hedged_results(total_unhedged_pl, total_hedged_pl)
        }

    def _interpret_hedged_results(self, unhedged_pl: float, hedged_pl: float) -> str:
        """
        Interpret what the delta-hedged results tell us.
        """
        reduction_pct = (abs(unhedged_pl - hedged_pl) / abs(unhedged_pl) * 100) if unhedged_pl != 0 else 0

        if abs(hedged_pl) < abs(unhedged_pl) * 0.1:
            return (f"✅ DIRECTIONAL EDGE CONFIRMED: {reduction_pct:.1f}% of profit came from oil direction, "
                   f"not mispricing. The model's edge was directional shorting, not pricing accuracy.")
        elif abs(hedged_pl) > abs(unhedged_pl) * 0.5:
            return (f"🤔 MISPRICING SIGNAL: Only {reduction_pct:.1f}% of profit eliminated by hedging. "
                   f"Model may have found genuine mispricings.")
        else:
            return (f"⚠️ MIXED RESULTS: {reduction_pct:.1f}% of profit from direction, "
                   f"{100-reduction_pct:.1f}% from other sources.")

    def backtest_european_call_delta_hedged_daily(self, strike: float, days_to_expiry: int,
                                              start_date: str = None) -> pd.DataFrame:
        """
        Backtest delta-hedged short call with DAILY REBALANCING.

        Strategy:
        1. Day 1: Sell call, buy delta of futures
        2. Day 2-60: Recalculate delta each day, adjust futures position
        3. Day 60: Close both at expiration

        Daily rebalancing = more realistic trading, cleaner alpha isolation

        Key difference from static hedge:
        - Static: Set delta hedge once, never adjust (gamma profit included)
        - Daily: Rebalance delta every day to stay neutral (isolates true alpha)

        Args:
            strike: Strike price of the option
            days_to_expiry: Days until option expiration
            start_date: Starting date for backtest (default: earliest available)

        Returns:
            DataFrame with daily delta-hedged backtest results
        """
        print(f"\n🔄 Running DAILY-REBALANCED delta-hedged backtest: {strike} strike call, {days_to_expiry} days to expiry")
        print(f"   Risk-free rate: {self.r*100:.1f}%")
        print(f"   Strategy: Sell call + rebalance delta hedge DAILY")

        if start_date is None:
            start_idx = 0
        else:
            start_idx = self.df[self.df['Date'] >= start_date].index[0]

        results = []

        # For each potential trade start date
        for i in range(start_idx, len(self.df) - days_to_expiry):
            entry_row = self.df.iloc[i]
            entry_date = entry_row['Date']
            entry_price = entry_row['Close']

            # Get volatility at entry
            entry_vol = self._get_volatility_at_date(str(entry_date.date()), window=30)

            if entry_vol is None or pd.isna(entry_vol):
                continue

            # === DAY 1: ENTRY ===
            T_entry = days_to_expiry / 365.0

            try:
                model_entry = GreeksCalculator(
                    spot_price=entry_price,
                    strike_price=strike,
                    time_to_expiry=T_entry,
                    risk_free_rate=self.r,
                    volatility=entry_vol
                )
            except ValueError:
                continue

            model_price_entry = model_entry.call_price()
            delta_entry = model_entry.delta('call')

            # Initialize tracking variables
            cumulative_rebalance_pnl = 0.0
            prev_delta = delta_entry
            prev_spot = entry_price

            # === DAYS 2-60: DAILY REBALANCING ===
            for day in range(1, days_to_expiry):
                rebal_idx = i + day

                if rebal_idx >= len(self.df):
                    break

                rebal_row = self.df.iloc[rebal_idx]
                current_spot = rebal_row['Close']
                current_date = rebal_row['Date']

                # Get volatility at this date
                current_vol = self._get_volatility_at_date(str(current_date.date()), window=30)

                if current_vol is None or pd.isna(current_vol):
                    break

                # Time to expiry from THIS date
                T_current = (days_to_expiry - day) / 365.0

                try:
                    model_current = GreeksCalculator(
                        spot_price=current_spot,
                        strike_price=strike,
                        time_to_expiry=T_current,
                        risk_free_rate=self.r,
                        volatility=current_vol
                    )
                except ValueError:
                    break

                # Calculate new delta
                current_delta = model_current.delta('call')

                # === REBALANCING CALCULATION ===
                # Previous day: we held (prev_delta) futures at (prev_spot)
                # Today: price moved to (current_spot)
                # P&L on our previous futures hedge:
                futures_pnl_today = prev_delta * (current_spot - prev_spot)

                # We need to rebalance from (prev_delta) to (current_delta)
                # This is the "rebalancing cost" - we're locking in gains/losses
                cumulative_rebalance_pnl += futures_pnl_today

                # Update for next iteration
                prev_delta = current_delta
                prev_spot = current_spot

            # === EXPIRATION: CLOSE ALL POSITIONS ===
            expiry_row = self.df.iloc[i + days_to_expiry]
            expiry_date = expiry_row['Date']
            expiry_price = expiry_row['Close']

            # Short call P&L
            realized_payoff = max(expiry_price - strike, 0)
            call_pnl = model_price_entry - realized_payoff

            # Final futures P&L (last day rebalancing)
            final_futures_pnl = prev_delta * (expiry_price - prev_spot)
            cumulative_rebalance_pnl += final_futures_pnl

            # Total hedged P&L
            total_hedged_pnl = call_pnl + cumulative_rebalance_pnl
            unhedged_pnl = call_pnl

            # Store result
            results.append({
                'entry_date': entry_date,
                'entry_spot': entry_price,
                'strike': strike,
                'model_price': model_price_entry,
                'entry_delta': delta_entry,
                'expiry_date': expiry_date,
                'expiry_price': expiry_price,
                'realized_payoff': realized_payoff,
                'call_pnl': call_pnl,
                'cumulative_rebalance_pnl': cumulative_rebalance_pnl,
                'total_hedged_pnl': total_hedged_pnl,
                'unhedged_pnl': unhedged_pnl,
                'hedged_pnl_pct': (total_hedged_pnl / model_price_entry * 100) if model_price_entry > 0 else 0,
            })

        self.results_hedged_daily = pd.DataFrame(results)
        return self.results_hedged_daily

    def get_daily_hedged_performance_metrics(self) -> Dict:
        """
        Calculate performance metrics for daily-rebalanced delta-hedged strategy.

        Key insight: If daily-hedged P&L ≈ 0, the edge was truly directional.
                     If significant P&L remains, it's genuine pricing alpha (minus gamma).
        """
        if not hasattr(self, 'results_hedged_daily') or len(self.results_hedged_daily) == 0:
            return None

        hedged_pl = self.results_hedged_daily['total_hedged_pnl']
        unhedged_pl = self.results_hedged_daily['unhedged_pnl']

        total_hedged_pl = hedged_pl.sum()
        total_unhedged_pl = unhedged_pl.sum()
        total_trades = len(hedged_pl)
        winning_hedged = (hedged_pl > 0).sum()

        hedged_returns = hedged_pl / self.results_hedged_daily['model_price']
        mean_hedged_return = hedged_returns.mean()
        std_hedged_return = hedged_returns.std()
        sharpe_hedged = (mean_hedged_return / std_hedged_return * np.sqrt(252)) if std_hedged_return > 0 else 0

        cumsum_hedged = hedged_pl.cumsum()
        running_max = cumsum_hedged.expanding().max()
        drawdown = cumsum_hedged - running_max
        max_drawdown_hedged = drawdown.min()

        return {
            'total_trades': total_trades,
            'unhedged_total_pl': total_unhedged_pl,
            'hedged_total_pl': total_hedged_pl,
            'pl_reduction': total_unhedged_pl - total_hedged_pl,
            'pl_reduction_pct': (abs(total_unhedged_pl - total_hedged_pl) / abs(total_unhedged_pl) * 100) if total_unhedged_pl != 0 else 0,
            'winning_trades_hedged': winning_hedged,
            'win_rate_hedged': winning_hedged / total_trades if total_trades > 0 else 0,
            'avg_hedged_pl': hedged_pl.mean(),
            'std_hedged_pl': hedged_pl.std(),
            'sharpe_hedged': sharpe_hedged,
            'max_drawdown_hedged': max_drawdown_hedged,
            'insight': self._interpret_daily_hedged_results(total_unhedged_pl, total_hedged_pl)
        }

    def _interpret_daily_hedged_results(self, unhedged_pl: float, hedged_pl: float) -> str:
        """
        Interpret daily-rebalanced delta-hedged results.

        With daily rebalancing, gamma P&L is mostly eliminated.
        Remaining P&L is closer to true pricing alpha (or just volatility assumption gap).
        """
        reduction_pct = (abs(unhedged_pl - hedged_pl) / abs(unhedged_pl) * 100) if unhedged_pl != 0 else 0

        if abs(hedged_pl) < abs(unhedged_pl) * 0.05:  # <5% remains
            return (f"✅ DIRECTIONAL CONFIRMED (Daily): {reduction_pct:.1f}% of profit from oil direction. "
                   f"Remaining is volatility assumption gap, not trading edge.")
        elif abs(hedged_pl) < abs(unhedged_pl) * 0.2:  # 5-20% remains
            return (f"⚠️ MOSTLY DIRECTIONAL (Daily): {reduction_pct:.1f}% from oil direction. "
                   f"Small residual from vol assumptions, possibly minor gamma capture.")
        else:
            return (f"🤔 SIGNIFICANT ALPHA (Daily): Only {reduction_pct:.1f}% from direction. "
                   f"Daily rebalancing kept most profit, suggesting genuine pricing edge.")

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
