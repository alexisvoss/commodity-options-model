"""
Example: Using Hedging Strategies

Shows how traders use the Greeks to manage risk.
"""

from src.greeks import GreeksCalculator
from src.hedging import HedgeCalculator, PortfolioAnalyzer, DeltaNeutralStrategy

def main():
    print("="*70)
    print("  HEDGING STRATEGIES EXAMPLE")
    print("="*70)
    
    # Example 1: Hedging a long oil position
    print("\n📊 SCENARIO 1: Long Oil Position with Put Hedge")
    print("   I own 10,000 barrels of Brent crude oil")
    print("   I want to protect against downside")
    
    # Create a pricing model for protection
    hedge_model = GreeksCalculator(
        spot_price=90.00,
        strike_price=85.00,  # Protect below this price
        time_to_expiry=0.25,
        risk_free_rate=0.04,
        volatility=0.30
    )
    
    put_price = hedge_model.put_price()
    put_greeks = hedge_model.all_greeks('put')
    
    print(f"\n💰 Put Option Details:")
    print(f"   Strike Price: $85.00 (floor price)")
    print(f"   Put Price: ${put_price:.2f}/barrel")
    print(f"   Total Cost: ${put_price * 10000:,.2f} for 10,000 barrels")
    
    # Calculate hedge
    hedge_calc = HedgeCalculator(10000, 'put')
    hedge_info = hedge_calc.calculate_hedge_ratio(put_greeks)
    
    print(f"\n🛡️  Hedge Calculation:")
    print(f"   Position Size: {hedge_info['position_size']:,.0f} barrels")
    print(f"   Put Delta: {hedge_info['delta']:.4f}")
    print(f"   Portfolio Delta: {hedge_info['portfolio_delta']:.2f}")
    
    # Example 2: Portfolio with multiple positions
    print("\n\n📈 SCENARIO 2: Multi-Position Portfolio")
    print("   Analyzing risk across multiple positions")
    
    portfolio = PortfolioAnalyzer()
    
    # Add long spot oil
    spot_greeks = {'delta': 1.0, 'gamma': 0, 'vega': 0, 'theta': 0}
    portfolio.add_position('Brent Crude Long (Spot)', 1000, spot_greeks, 90.00)
    
    # Add short call (sold covered call)
    call_model = GreeksCalculator(90, 95, 0.25, 0.04, 0.30)
    call_greeks = call_model.all_greeks('call')
    portfolio.add_position('Call Short 95-Strike', -100, call_greeks, call_model.call_price())
    
    # Add long put (bought protection)
    put_model = GreeksCalculator(90, 85, 0.25, 0.04, 0.30)
    put_greeks = put_model.all_greeks('put')
    portfolio.add_position('Put Long 85-Strike', 100, put_greeks, put_model.put_price())
    
    # Show portfolio
    print("\n📊 Portfolio Positions:")
    df = portfolio.get_position_dataframe()
    print(df.to_string(index=False))
    
    # Show summary Greeks
    summary = portfolio.portfolio_summary()
    print(f"\n📊 Portfolio Greeks:")
    print(f"   Total Delta: {summary['total_delta']:.2f}")
    print(f"   Total Gamma: {summary['total_gamma']:.6f}")
    print(f"   Total Vega:  {summary['total_vega']:.4f}")
    print(f"   Total Theta: ${summary['total_theta']:.4f}/day")
    print(f"   Delta % of Portfolio Value: {summary['delta_pct']:.2f}%")
    
    # Example 3: Delta-Neutral Strategies
    print("\n\n🎯 SCENARIO 3: Delta-Neutral Strategies")
    
    # Long call spread
    print("\n📈 Long Call Spread (Bull Strategy):")
    print("   Buy $90 call, Sell $95 call")
    
    spread = DeltaNeutralStrategy.long_call_spread(
        spot=90,
        long_strike=90,
        short_strike=95,
        expiry=0.25,
        rate=0.04,
        vol=0.30
    )
    
    print(f"   Net Cost: ${spread['net_cost']:.2f}/barrel")
    print(f"   Max Profit: ${spread['max_profit']:.2f}/barrel")
    print(f"   Max Loss: ${spread['max_loss']:.2f}/barrel")
    print(f"   Breakeven: ${spread['breakeven']:.2f}")
    print(f"   Delta: {spread['delta']:.4f} (how much it moves with spot)")
    
    # Protective put
    print("\n🛡️  Protective Put (Insurance Strategy):")
    print("   Long Stock, Long $85 Put")
    
    protective = DeltaNeutralStrategy.protective_put(
        spot=90,
        strike=85,
        expiry=0.25,
        rate=0.04,
        vol=0.30
    )
    
    print(f"   Stock Price: ${protective['stock_price']:.2f}")
    print(f"   Put Cost: ${protective['put_cost']:.2f}")
    print(f"   Floor Price: ${protective['floor_price']:.2f}")
    print(f"   Interpretation: {protective['interpretation']}")
    
    print("\n" + "="*70)
    print("✅ Hedging strategies loaded and ready!")
    print("="*70)

if __name__ == "__main__":
    main()