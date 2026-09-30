"""
Example 1: Basic Brent Crude Option Pricing

This script demonstrates how to use the Black-Scholes model 
to price European options on Brent crude futures.
"""

from src.greeks import GreeksCalculator

def print_separator(title: str):
    """Print a formatted separator for readability"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def main():
    """Main example function"""
    
    print_separator("EXAMPLE 1: Basic Brent Crude Call Pricing")
    
    # Create a pricing model for a Brent crude call option
    # Current Brent price: $85.50/barrel
    # Strike price: $90/barrel (betting oil will go up)
    # 3 months to expiry
    # Risk-free rate: 4% annual
    # Volatility: 30% annual (oil is volatile!)
    
    model = GreeksCalculator(
        spot_price=85.50,      # Current Brent price
        strike_price=90.00,    # Strike price
        time_to_expiry=0.25,   # 3 months = 0.25 years
        risk_free_rate=0.04,   # 4% annual rate
        volatility=0.30        # 30% volatility
    )
    
    print("\n📊 OPTION PARAMETERS:")
    print(f"  Spot Price (current Brent):  ${model.S:.2f}/barrel")
    print(f"  Strike Price:                ${model.K:.2f}/barrel")
    print(f"  Time to Expiry:              {model.T:.2f} years (3 months)")
    print(f"  Risk-Free Rate:              {model.r*100:.1f}%")
    print(f"  Volatility:                  {model.sigma*100:.1f}%")
    
    # Calculate the call option price
    call_price = model.call_price()
    put_price = model.put_price()
    
    print("\n💰 OPTION PRICES:")
    print(f"  Call Option Price:  ${call_price:.2f}/barrel")
    print(f"  Put Option Price:   ${put_price:.2f}/barrel")
    print(f"\n  Example: If you buy 1,000 barrels of calls, cost = ${call_price * 1000:,.2f}")
    
    # Get all Greeks for the call option
    call_greeks = model.all_greeks('call')
    
    print("\n📈 CALL OPTION GREEKS (Risk Sensitivities):")
    print(f"  Delta (Δ):  {call_greeks['delta']:.4f}")
    print(f"    → If oil rises $1, call option gains ${call_greeks['delta']:.2f}")
    
    print(f"\n  Gamma (Γ):  {call_greeks['gamma']:.6f}")
    print(f"    → Delta will change by {call_greeks['gamma']:.6f} for each $1 oil move")
    
    print(f"\n  Vega (ν):   {call_greeks['vega']:.4f}")
    print(f"    → If volatility increases 1%, call price gains ${call_greeks['vega']:.2f}")
    
    print(f"\n  Theta (Θ):  ${call_greeks['theta']:.4f} per day")
    print(f"    → Time decay costs ${abs(call_greeks['theta']):.2f} per day (if nothing changes)")
    
    print(f"\n  Rho (ρ):    {call_greeks['rho']:.4f}")
    print(f"    → If rates increase 1%, call price changes by ${call_greeks['rho']:.2f}")
    
    # Get Greeks for put option
    put_greeks = model.all_greeks('put')
    
    print("\n📉 PUT OPTION GREEKS:")
    print(f"  Delta (Δ):  {put_greeks['delta']:.4f}")
    print(f"    → If oil rises $1, put option loses ${abs(put_greeks['delta']):.2f}")
    
    print(f"  Vega (ν):   {put_greeks['vega']:.4f}")
    print(f"  Theta (Θ):  ${put_greeks['theta']:.4f} per day")
    print(f"  Rho (ρ):    {put_greeks['rho']:.4f}")
    
    # Example 2: Compare different strike prices
    print_separator("EXAMPLE 2: Compare Different Strike Prices")
    
    strikes = [80, 85, 90, 95, 100]
    print("\nStrike Price | Call Price | Call Delta | Implied Probability")
    print("-" * 65)
    
    for strike in strikes:
        model_strike = GreeksCalculator(
            spot_price=85.50,
            strike_price=strike,
            time_to_expiry=0.25,
            risk_free_rate=0.04,
            volatility=0.30
        )
        call = model_strike.call_price()
        delta = model_strike.delta('call')
        
        # Delta approximates probability of finishing ITM
        prob_itm = delta * 100
        
        print(f"  ${strike:5.2f}     | ${call:8.2f}   | {delta:8.4f}    | {prob_itm:5.1f}%")
    
    # Example 3: Impact of volatility
    print_separator("EXAMPLE 3: Impact of Volatility on Option Price")
    
    print("\nVolatility | Call Price | Put Price  | Vega")
    print("-" * 50)
    
    volatilities = [0.10, 0.20, 0.30, 0.40, 0.50]
    
    for vol in volatilities:
        model_vol = GreeksCalculator(
            spot_price=85.50,
            strike_price=90.00,
            time_to_expiry=0.25,
            risk_free_rate=0.04,
            volatility=vol
        )
        call = model_vol.call_price()
        put = model_vol.put_price()
        vega = model_vol.vega()
        
        print(f"  {vol*100:5.0f}%     | ${call:8.2f}  | ${put:8.2f} | {vega:.4f}")
    
    print("\n💡 Notice: Higher volatility → Higher option prices (both calls and puts)")
    print("   This is why options traders care about volatility!")
    
    print_separator("✅ Example Complete!")
    print("\nYou now understand how to:")
    print("  1. Create an option pricing model")
    print("  2. Calculate fair option prices")
    print("  3. Understand Greeks (risk sensitivities)")
    print("  4. Compare different market scenarios")

if __name__ == "__main__":
    main()
    