"""
Data Handler for Historical Brent Crude Price Data

This module loads and processes historical Brent crude price data,
calculates rolling volatility, and provides convenient methods
for accessing data at specific dates.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional

class BrentDataHandler:
    """Load and process historical Brent crude oil data"""
    
    def __init__(self, filepath: str):
        """
        Initialize the data handler with historical price data.
        
        Args:
            filepath: Path to CSV file with columns: Date, Close (at minimum)
        
        Expected CSV format:
            Date,Close,High,Low,Open,Volume
            2022-01-01,90.50,91.20,89.80,90.00,1000000
            2022-01-02,91.30,92.10,90.50,90.80,1100000
        """
        self.filepath = filepath
        
        # Try to load the data
        try:
            self.df = pd.read_csv(filepath)
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        # Handle yfinance format - rename columns if needed
        self.df.columns = self.df.columns.str.strip()
    
        # Convert columns to numeric (this handles mixed types)
        numeric_cols = ['Close', 'High', 'Low', 'Open', 'Volume']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
    
        # Remove any rows with NaN values (header rows, etc.)
        self.df = self.df.dropna(subset=['Close'])
    
        # Ensure Date column is datetime
        self.df['Date'] = pd.to_datetime(self.df['Date'])
    
        # Sort by date (oldest first)
        self.df = self.df.sort_values('Date').reset_index(drop=True)
    
        print(f"✅ Loaded {len(self.df)} trading days of Brent data")
        print(f"   Date range: {self.df['Date'].min().date()} to {self.df['Date'].max().date()}")
    
    def calculate_volatility(self, window: int = 30) -> pd.Series:
        """
        Calculate rolling historical volatility.
        
        Historical volatility is the standard deviation of returns.
        We annualize it by multiplying by sqrt(252) (trading days per year).
        
        Args:
            window: Number of days for rolling calculation (default 30 = monthly vol)
        
        Returns:
            Pandas Series with volatility for each date
            
        Formula:
            Daily return = ln(P_today / P_yesterday)
            Volatility = stdev(returns) * sqrt(252)
        """
        # Calculate daily log returns
        # log return is more accurate than simple return for options pricing
        returns = np.log(self.df['Close'] / self.df['Close'].shift(1))
        
        # Calculate rolling standard deviation (window period)
        rolling_std = returns.rolling(window=window).std()
        
        # Annualize: multiply by sqrt(252 trading days per year)
        volatility = rolling_std * np.sqrt(252)
        
        return volatility
    
    def get_data_at_date(self, date: str, window: int = 30) -> Optional[Dict]:
        """
        Get price and volatility data at a specific date.
        
        This is useful for backtesting:
        - Get the spot price at a historical date
        - Get the realized volatility at that date
        - Use both to price an option as if we're at that date
        
        Args:
            date: Date string in format 'YYYY-MM-DD'
            window: Days used to calculate volatility (default 30)
        
        Returns:
            Dictionary with keys: date, price, volatility, high, low
            Returns None if date not found
        """
        try:
            # Find the row for this date
            row_idx = self.df[self.df['Date'] == date].index[0]
            row = self.df.iloc[row_idx]
        except IndexError:
            print(f"⚠️  Date {date} not found in data")
            return None
        
        # Calculate volatility at this date
        volatility_series = self.calculate_volatility(window)
        vol_at_date = volatility_series.iloc[row_idx]
        
        return {
            'date': date,
            'price': float(row['Close']),
            'volatility': float(vol_at_date),
            'high': float(row['High']) if 'High' in row else None,
            'low': float(row['Low']) if 'Low' in row else None,
            'volume': float(row['Volume']) if 'Volume' in row else None
        }
    
    def get_price_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get data for a range of dates.
        
        Args:
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
        
        Returns:
            DataFrame with data for the date range
        """
        mask = (self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)
        return self.df[mask].copy()
    
    def get_latest_data(self, n_days: int = 5) -> pd.DataFrame:
        """
        Get the most recent N days of data.
        
        Useful for seeing current market conditions.
        
        Args:
            n_days: Number of recent days to return
        
        Returns:
            DataFrame with most recent data
        """
        return self.df.tail(n_days).copy()
    
    def summary_statistics(self) -> Dict:
        """
        Get summary statistics for the entire dataset.
        
        Returns:
            Dictionary with min, max, mean, std of prices
        """
        prices = self.df['Close']
        
        return {
            'min_price': float(prices.min()),
            'max_price': float(prices.max()),
            'mean_price': float(prices.mean()),
            'std_price': float(prices.std()),
            'current_price': float(prices.iloc[-1]),
            'price_range': float(prices.max() - prices.min()),
            'num_days': len(self.df)
        }
    
    def export_with_volatility(self, output_path: str, window: int = 30):
        """
        Export data with calculated volatility to a new CSV file.
        
        This is useful for analysis in Excel or other tools.
        
        Args:
            output_path: Path where to save the CSV
            window: Days used to calculate volatility
        """
        df_export = self.df.copy()
        df_export['Volatility'] = self.calculate_volatility(window)
        df_export['Daily_Return'] = df_export['Close'].pct_change()
        
        df_export.to_csv(output_path, index=False)
        print(f"✅ Exported data to {output_path}")


# Example usage (for testing the module)
if __name__ == "__main__":
    # This only runs if you execute this file directly
    # It's useful for testing during development
    
    print("Data Handler Module Test")
    print("=" * 50)
    print("\nTo use this module:")
    print("  from src.data_handler import BrentDataHandler")
    print("  handler = BrentDataHandler('data/brent_prices.csv')")
    print("  data = handler.get_data_at_date('2023-01-15')")
    print("  stats = handler.summary_statistics()")