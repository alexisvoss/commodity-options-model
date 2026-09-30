"""
Example: Using the Brent Data Handler

This demonstrates how to load historical data and calculate volatility.
"""

from src.data_handler import BrentDataHandler

def main():
    print("="*60)
    print("  BRENT DATA HANDLER EXAMPLE")
    print("="*60)
    
    # Load the historical data
    handler = BrentDataHandler('data/brent_sample.csv')
    
    # Get summary statistics
    print("\n📊 DATASET SUMMARY:")
    stats = handler.summary_statistics()
    print(f"  Current Price:        ${stats['current_price']:.2f}/barrel")
    print(f"  Min Price:            ${stats['min_price']:.2f}/barrel")
    print(f"  Max Price:            ${stats['max_price']:.2f}/barrel")
    print(f"  Mean Price:           ${stats['mean_price']:.2f}/barrel")
    print(f"  Price Range:          ${stats['price_range']:.2f}/barrel")
    print(f"  Std Dev:              ${stats['std_price']:.2f}/barrel")
    print(f"  Trading Days:         {stats['num_days']}")
    
    # Get latest data
    print("\n📈 LATEST 5 TRADING DAYS:")
    latest = handler.get_latest_data(5)
    for idx, row in latest.iterrows():
        print(f"  {row['Date'].date()}: ${row['Close']:.2f} (High: ${row['High']:.2f}, Low: ${row['Low']:.2f})")
    
    # Get data for a specific date
    print("\n📅 DATA FOR SPECIFIC DATE:")
    sample_date = latest.iloc[0]['Date'].strftime('%Y-%m-%d')
    data = handler.get_data_at_date(sample_date, window=30)
    
    if data:
        print(f"  Date:                 {data['date']}")
        print(f"  Spot Price:           ${data['price']:.2f}/barrel")
        print(f"  30-Day Volatility:    {data['volatility']*100:.2f}%")
        print(f"  High:                 ${data['high']:.2f}")
        print(f"  Low:                  ${data['low']:.2f}")
    
    # Calculate volatility over time
    print("\n📊 VOLATILITY ANALYSIS:")
    vol_30 = handler.calculate_volatility(30)
    vol_60 = handler.calculate_volatility(60)
    
    print(f"  30-Day Volatility (current):  {vol_30.iloc[-1]*100:.2f}%")
    print(f"  60-Day Volatility (current):  {vol_60.iloc[-1]*100:.2f}%")
    print(f"  30-Day Volatility (min):      {vol_30.min()*100:.2f}%")
    print(f"  30-Day Volatility (max):      {vol_30.max()*100:.2f}%")
    
    # Get a date range
    print("\n📆 DATA FOR DATE RANGE:")
    print("  (Showing first 5 rows from 2023)")
    
    range_data = handler.get_price_range('2023-01-01', '2023-01-31')
    print(f"  Retrieved {len(range_data)} trading days in January 2023")
    print(f"  Min price: ${range_data['Close'].min():.2f}")
    print(f"  Max price: ${range_data['Close'].max():.2f}")
    print(f"  Mean price: ${range_data['Close'].mean():.2f}")
    
    print("\n" + "="*60)
    print("✅ Data Handler is working correctly!")
    print("="*60)

if __name__ == "__main__":
    main()