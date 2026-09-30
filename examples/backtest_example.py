"""
Example: Backtesting the Black-Scholes Model

This demonstrates how well our pricing model performs
against real historical Brent crude data.
"""

from src.data_handler import BrentDataHandler
from src.backtester import OptionBacktester

def main():
    print("="*70)
    print("  BACKTESTING BLACK-SCHOLES MODEL")
    print("="*70)
    
    # Load data
    handler = BrentDataHandler('data/brent_sample.csv')
    backtester = OptionBacktester(handler, risk_free_rate=0.04)
    
    # Backtest a call option
    print("\n📊 BACKTEST SCENARIO 1: Call Option")
    print("   Strike: $85, Expiry: 60 days")
    
    results_call = backtester.backtest_european_call(
        strike=85.00,
        days_to_expiry=60,
        start_date='2022-06-01'
    )
    
    metrics_call = backtester.get_performance_metrics()
    
    print("\n💰 RESULTS:")
    print(f"  Total Trades:         {metrics_call['total_trades']}")
    print(f"  Winning Trades:       {metrics_call['winning_trades']} ({metrics_call['win_rate']*100:.1f}%)")
    print(f"  Losing Trades:        {metrics_call['losing_trades']}")
    print(f"  Total P&L:            ${metrics_call['total_pl']:.2f}")
    print(f"  Average P&L/Trade:    ${metrics_call['mean_pl']:.2f}")
    print(f"  Sharpe Ratio:         {metrics_call['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown:         ${metrics_call['max_drawdown']:.2f}")
    
    print("\n📈 SAMPLE TRADES:")
    print("   Date       | Spot  | Model Price | Realized | P&L")
    print("   " + "-"*50)
    
    for idx, row in results_call.head(5).iterrows():
        print(f"   {row['date'].date()} | ${row['spot_price']:6.2f} | "
              f"${row['model_price']:10.2f} | ${row['realized_payoff']:8.2f} | "
              f"${row['profit_loss']:6.2f}")
    
    print("\n" + "="*70)
    print("✅ Backtest Complete!")
    print("="*70)
    print("\n💡 Interpretation:")
    print(f"   Our model made ${metrics_call['total_pl']:.2f} if we sold calls at model price")
    print(f"   and bought them back at intrinsic value.")
    print(f"   Win rate of {metrics_call['win_rate']*100:.1f}% means model was right that often.")

if __name__ == "__main__":
    main()