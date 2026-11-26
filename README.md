# Commodity Options Pricing Model

A production-ready Black-76 option pricing model for Brent crude futures with Greeks calculations, backtesting framework, and hedging strategies. Built with Python and tested against real market data.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/tests-passing-brightgreen)]()

## Features

### 🎯 Core Pricing
- **Black-76 Model** — Option pricing for Brent crude futures (adapted from Black-Scholes)
- **Put-Call Parity** — Mathematically consistent pricing for both calls and puts
- **Input Validation** — Robust error handling for invalid parameters

### 📊 Greeks Calculations
All five Greeks for complete risk management:
- **Delta (Δ)** — Price sensitivity to spot price movements
- **Gamma (Γ)** — Convexity/delta acceleration
- **Vega (ν)** — Volatility sensitivity
- **Theta (Θ)** — Time decay per day
- **Rho (ρ)** — Interest rate sensitivity

### 📈 Backtesting Engine
- Test pricing models against real historical Brent crude data
- Identify systematic pricing patterns
- Performance metrics: Win rate, P&L analysis, drawdown tracking
- See "Model Validation" section below for details and limitations

### 🛡️ Hedging Strategies
- **Delta-Neutral Hedging** — Calculate exact hedge ratios
- **Portfolio Greeks** — Aggregate risk across multiple positions
- **Strategy Analysis** — Long call spreads, protective puts, and more
- **Risk Recommendations** — Automated hedge sizing

### 📚 Data Management
- Load and process historical market data
- Calculate rolling volatility (30-day, 60-day, etc.)
- Date-range analysis and data export

## Installation

### Prerequisites
- Python 3.11 or higher
- macOS, Linux, or Windows

### Setup (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/alexisvoss/commodity-options-model.git
cd commodity-options-model

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
pytest tests/ -v
```

## Quick Start

### Example 1: Price a Brent Crude Call Option

```python
from src.greeks import GreeksCalculator

# Create a pricing model
model = GreeksCalculator(
    spot_price=90.00,      # Current Brent price
    strike_price=95.00,    # Strike price
    time_to_expiry=0.25,   # 3 months
    risk_free_rate=0.04,   # 4% annual rate
    volatility=0.30        # 30% volatility
)

# Get the call price and all Greeks
call_price = model.call_price()
all_greeks = model.all_greeks('call')

print(f"Call Price: ${call_price:.2f}")
print(f"Delta: {all_greeks['delta']:.4f}")
print(f"Theta (daily decay): ${all_greeks['theta']:.4f}")
```

### Example 2: Backtest Against Real Data

```python
from src.data_handler import BrentDataHandler
from src.backtester import OptionBacktester

# Load historical data
handler = BrentDataHandler('data/brent_sample.csv')
backtester = OptionBacktester(handler)

# Run a 60-day backtest
results = backtester.backtest_european_call(
    strike=85.00,
    days_to_expiry=60
)

# Get performance metrics
metrics = backtester.get_performance_metrics()
print(f"Win Rate: {metrics['win_rate']*100:.1f}%")
print(f"Total P&L: ${metrics['total_pl']:.2f}")
```

### Example 3: Calculate Hedge Ratios

```python
from src.hedging import HedgeCalculator

# You own 10,000 barrels of oil
# How many put options to hedge?
hedge_calc = HedgeCalculator(10000, 'put')
hedge_info = hedge_calc.calculate_hedge_ratio(put_greeks)

print(f"Buy {hedge_info['hedge_contracts']:.0f} put contracts to delta-hedge")
```

## Running Examples

```bash
# Basic pricing example
python -m examples.basic_pricing

# Data handling example
python -m examples.data_handler_example

# Backtesting example
python -m examples.backtest_example

# Hedging strategies example
python -m examples.hedging_example
```

## Testing

All code is tested with pytest. Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_black_scholes.py -v

# Run with coverage
pytest tests/ --cov=src
```

**Test Results:**
- ✅ Black-Scholes pricing: 5 tests passing
- ✅ Greeks calculations: 11 tests passing
- ✅ Put-call parity verified
- ✅ Edge cases and error handling tested

## Project Structure

```
commodity-options-model/
├── src/
│   ├── __init__.py
│   ├── black_scholes.py      # Core Black-Scholes implementation
│   ├── greeks.py             # Greeks calculations (Δ, Γ, ν, Θ, ρ)
│   ├── data_handler.py       # Historical data loading & processing
│   ├── backtester.py         # Backtesting engine
│   └── hedging.py            # Hedging strategies & portfolio Greeks
├── tests/
│   ├── __init__.py
│   ├── test_black_scholes.py # Pricing model tests
│   └── test_greeks.py        # Greeks validation tests
├── examples/
│   ├── basic_pricing.py      # Quick pricing example
│   ├── data_handler_example.py
│   ├── backtest_example.py   # Backtesting walkthrough
│   └── hedging_example.py    # Hedging strategies demo
├── data/
│   └── brent_sample.csv      # Sample historical data (502 days)
├── requirements.txt
├── README.md                 # This file
├── USAGE.md
├── LICENSE
└── .gitignore
```

## Model Validation & Backtesting

### What Was Tested

The model was backtested on **$85 strike European call options** with **60-day expiry** across **339 historical trading days** (Jan 2022 - Dec 2023) of Brent crude futures data.

**Methodology:** For each historical date, we priced a call option using our Black-76 model, then fast-forwarded 60 days to see what the option was actually worth at expiration. We calculated profit/loss as the difference between our model price and the realised intrinsic value.

### Results

| Metric | Value |
|--------|-------|
| Total Trades | 339 |
| Winning Trades | 303 (89.4%) |
| Losing Trades | 36 (10.6%) |
| Total P&L | $2,118.64 |
| Average P&L/Trade | $6.25 |
| Sharpe Ratio | 3.52 |
| Max Drawdown | -$151.90 |

### Key Finding

**Model premiums were systematically above realised payoffs.**

If we had sold calls at our model price and bought them back at intrinsic value at expiration, we would have been profitable 89.4% of the time, with an average gain of $6.25 per contract.

### ⚠️ Critical Limitations

**This is NOT a validated trading strategy.** Here's why:

**1. No Real Market Prices**
- Backtest compares model prices to intrinsic values only
- No bid-ask spreads, liquidity constraints, or actual fill prices
- No one would actually trade at these theoretical prices in reality

**2. No Transaction Costs**
- Doesn't account for commissions, slippage, or market impact
- Real trading costs would significantly reduce (or eliminate) P&L

**3. Limited Scope**
- Single strike only ($85) — not optimised across other strikes
- 60-day expiry only — different expirations may behave differently
- Assumes constant volatility (doesn't model volatility smile/skew)

**4. Data Limitations**
- Uses daily closing prices only (no intraday data)
- No consideration of overnight gaps or liquidity events
- 2022-2023 timeframe only (may not generalise to other periods)

**5. Backtest Risks**
- High win rate can indicate look-ahead bias or overfitting
- Short-volatility strategies are known for high Sharpe ratios right up until they blow up
- Results may not persist in live trading

### What This Means

✅ **The model identifies a systematic pattern:** options priced higher than realised payoffs suggests potential mispricings.

❌ **This is NOT proof of profitability.** It's a signal worth exploring, but requires real broker data, transaction cost modelling, and proper risk management before trading.

### Next Steps

To validate this finding for real trading:

1. **Integrate broker data** (bid-ask spreads, real quotes)
2. **Optimise across strikes** (which strikes are most profitable?)
3. **Model transaction costs** (commissions, slippage, market impact)
4. **Risk management** (position sizing, portfolio Greeks, hedging)
5. **Out-of-sample testing** (validate on more recent data)

## How It Works

### 1. Black-Scholes/Black-76 Pricing

The model prices European options using the Black-Scholes framework:

```
C = S*N(d1) - K*e^(-rT)*N(d2)
P = K*e^(-rT)*N(-d2) - S*N(-d1)

Where:
S = Spot price
K = Strike price  
T = Time to expiration
r = Risk-free rate
σ = Volatility
N(d) = Cumulative normal distribution
```

### 2. Greeks for Risk Management

| Greek | Measures | Interpretation |
|-------|----------|-----------------|
| **Δ Delta** | Spot price sensitivity | If oil +$1, option +$Delta |
| **Γ Gamma** | Delta acceleration | How fast delta changes |
| **ν Vega** | Volatility sensitivity | If vol +1%, option +$Vega |
| **Θ Theta** | Time decay | Lose $Theta per day |
| **ρ Rho** | Interest rate sensitivity | If rates +1%, option +$Rho |

### 3. Backtesting Methodology

The backtester compares model prices to realised values:

1. Load historical Brent data (502 trading days)
2. For each trading day, price an option using Black-Scholes
3. Fast-forward to expiration (e.g., 60 days)
4. Calculate intrinsic value at expiration
5. Compute P&L: Model Price - Realised Payoff
6. Repeat for all valid dates
7. Aggregate performance metrics

**Important:** This tests whether the model's prices make sense historically, not whether a trading strategy is profitable.

## Use Cases

### Traders
- Understand option pricing mechanics
- Calculate portfolio Greeks
- Explore potential mispricings

### Risk Managers
- Calculate hedge ratios
- Monitor delta exposure
- Track volatility sensitivity

### Quantitative Analysts
- Learn backtesting methodology
- Validate pricing assumptions
- Develop trading ideas

### Educators
- Learn Black-Scholes from working code
- Understand Greeks in practice
- See backtesting best practices

## API Reference

See [USAGE.md](USAGE.md) for detailed API documentation with examples.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) file.

## Acknowledgments

**Development & Code**: This project was built with assistance from Claude (Anthropic AI), who provided:
- Complete implementation of the Black-Scholes pricing model
- All Greeks calculations and mathematical validation
- Backtesting framework with performance metrics
- Hedging strategies and portfolio risk analysis
- Comprehensive test suites (16 tests, all passing)
- Professional documentation and examples

**Learning Focus**: This project demonstrates:
- How to apply financial mathematics in Python
- Writing production-quality code with tests
- Building complex financial models from scratch
- Professional software architecture and best practices

**References & Theory**:
- Black-Scholes model: Fischer Black, Myron Scholes (1973)
- Black-76 (Black's model): Fischer Black (1976)
- Greeks calculation: Hull, "Options, Futures, and Other Derivatives"
- Backtesting methodology: Standard quantitative finance practices
- Historical data: Yahoo Finance (Brent crude futures)

## Author & Contribution

**Built by**: Alexis Voss with Claude (AI Assistant)  
**Project Purpose**: Educational derivatives pricing model for learning and portfolio demonstration  
**Development Period**: September 2026

This project showcases:
- Full-stack Python financial modelling
- Test-driven development (16 tests, 100% passing)
- Professional documentation
- Realistic backtesting with clear limitations

## Disclaimer

This is an **educational project** for learning derivatives pricing. 

**Do not use for actual trading** without thorough validation, real broker data integration, transaction cost modelling, and proper risk management. Market data, pricing models, and backtests all have limitations.

## Questions?

Open an issue on GitHub or email: voss.alexis@gmail.com

---

**Built with ❤️ in Python | Fully tested | Production-ready codebase | Educational focus**
