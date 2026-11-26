# Black-76 Commodity Options Pricing Model

A production-ready Python implementation of the Black-76 options pricing model for commodity futures (Brent crude oil), with comprehensive Greeks calculations, backtesting framework, and rigorous edge isolation analysis.

## Overview

This model prices European-style options on commodity futures using the Black-76 framework, which is the standard for futures options (unlike Black-Scholes which uses spot prices, Black-76 uses forward prices).

**What this model does:**
- Price European call and put options on Brent crude futures
- Calculate all five Greeks (Delta, Gamma, Vega, Theta, Rho) for risk management
- Backtest historical pricing accuracy using real 2022-2023 Brent data
- Isolate trading edge sources through delta-hedging (static and daily rebalancing)

## Key Features

### 1. Black-76 Pricing Engine
```python
from src.black_scholes import Black76Model

model = Black76Model(
    spot_price=116.29,
    strike_price=85.00,
    time_to_expiry=60/365,
    risk_free_rate=0.04,
    volatility=0.35
)

call_price = model.call_price()  # Uses forward price F = S * e^(r*T)
put_price = model.put_price()
```

### 2. Greeks Calculator
```python
from src.greeks import GreeksCalculator

greeks = GreeksCalculator(
    spot_price=116.29,
    strike_price=85.00,
    time_to_expiry=60/365,
    risk_free_rate=0.04,
    volatility=0.35
)

delta = greeks.delta('call')    # Directional sensitivity
gamma = greeks.gamma()          # Delta acceleration
vega = greeks.vega()            # Volatility sensitivity
theta = greeks.theta('call')    # Time decay
rho = greeks.rho('call')        # Interest rate sensitivity
```

### 3. Backtesting Framework

Three levels of edge isolation:

#### **Test 1: Unhedged Strategy**
Price calls, track profit if sold at model price vs bought back at intrinsic value.

#### **Test 2: Static Delta-Hedged**
Sell call at model price, buy delta-equivalent futures position on day 1, hold both until expiry.
- Removes directional exposure
- Keeps gamma profit from staying hedged
- Isolates true pricing edge vs directional betting

#### **Test 3: Daily-Rebalanced Delta-Hedged**
Sell call, then rebalance delta hedge every single day for 60 days.
- Removes both directional and gamma profit
- Isolates pure pricing alpha
- If this is negative, there is no pricing edge

---

## Backtest Results: Brent Crude Calls, 2022-2023

**Setup:** Strike $85, 60-day expiry, 339 trades across 2 years

### Part 1: Unhedged Strategy
```
Total P&L:          $2,118.64
Winning Trades:     303 (89.4%)
Losing Trades:      36
Sharpe Ratio:       3.52
Max Drawdown:       -$151.90
```

**Interpretation:** Our model prices calls and sells them. If we bought them back at intrinsic value at expiry, we'd make $2.1K. But this includes profit from Brent's directional decline and gamma effects—not necessarily pricing accuracy.

---

### Part 2: Static Delta-Hedged (Hold hedge 60 days)
```
Unhedged P&L:       $2,118.64
Hedged P&L:         $523.11
Profit from Direction: 75.3%
Profit from Other:  24.7%

Win Rate (Hedged):  79.4%
Sharpe (Hedged):    4.20
Max Drawdown:       -$102.86
```

**Interpretation:** When we hedge directional risk with a static delta position, we lose $1,595.53 of profit (75.3% of the total). This tells us:
- **75% of profit came from Brent's 2022-23 decline** (directional bet)
- **25% came from gamma capture** (benefits of being delta-hedged but not rebalancing daily) + volatility assumption gap
- The model is not pricing calls more accurately than the market—it's betting on oil direction.

---

### Part 3: Daily-Rebalanced Delta-Hedged (Rebalance delta every day)
```
Unhedged P&L:       $2,118.64
Daily Hedged P&L:   -$127.44 ← LOSS
P&L Reduction:      106.0%

Win Rate:           42.5%
Sharpe:             0.29
```

**Interpretation:** When we rebalance the delta hedge every day, we:
- Eliminate gamma profit
- Remove all directional exposure
- Keep only pure pricing alpha (if any exists)

Result: **-$127.44 loss**, which means:
- **There is NO pricing alpha in this model**
- All $2.1K profit came from: directional betting (75%) + gamma capture (25%)
- The volatility assumption was slightly too high—we sold calls assuming Brent would be more volatile than it turned out to be

---

## Conclusion

**What this model teaches:**

This project demonstrates a rigorous approach to options trading analysis:

1. **Pricing vs Trading** — Just because a model prices calls profitably doesn't mean it found mispricings. It could be directional betting or gamma capture.

2. **Delta-Hedging as Diagnostic** — By progressively removing sources of profit (directional first, gamma second), we identified exactly where returns came from.

3. **Intellectual Honesty** — A 89.4% win rate looks great until you delta-hedge and realize 75% was directional. Daily rebalancing revealed the remaining 25% was gamma, not mispricing.

4. **Why This Matters** — Understanding your edge is crucial for:
   - Managing risk correctly (we were actually making a directional bet, not a market-neutral trade)
   - Sizing positions appropriately
   - Not claiming alpha you don't have

**For your portfolio:** This project shows you can:
- Implement industry-standard options models
- Build realistic backtesting frameworks
- Rigorously isolate trading edge sources
- Be honest about what the results actually mean

---

## Installation

```bash
# Clone the repo
git clone https://github.com/[your-username]/commodity-options-model.git
cd commodity-options-model

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Pricing
```bash
python -m examples.basic_pricing
```

### Full Backtesting (All 3 Tests)
```bash
python -m examples.backtest_example
```

Output shows:
- Part 1: Unhedged call pricing ($2.1K profit)
- Part 2: Static delta-hedged (shows 75% was directional)
- Part 3: Daily rebalanced (shows no pricing alpha)

### Individual Option Pricing
```python
from src.greeks import GreeksCalculator

model = GreeksCalculator(
    spot_price=116.29,
    strike_price=85.00,
    time_to_expiry=60/365,
    risk_free_rate=0.04,
    volatility=0.35
)

print(f"Call Price: ${model.call_price():.2f}")
print(f"All Greeks: {model.all_greeks('call')}")
```

## Project Structure

```
commodity-options-model/
├── src/
│   ├── __init__.py
│   ├── black_scholes.py      # Black-76 pricing model
│   ├── greeks.py             # Greek calculations
│   ├── data_handler.py       # Historical data loading & processing
│   └── backtester.py         # 3-level backtesting framework
├── data/
│   └── brent_sample.csv      # Historical Brent crude data (2022-2023)
├── examples/
│   ├── __init__.py
│   ├── basic_pricing.py      # Simple pricing example
│   └── backtest_example.py   # Full backtest with all 3 tests
├── tests/
│   ├── __init__.py
│   ├── test_pricing.py       # Black-76 pricing tests
│   ├── test_greeks.py        # Greeks calculation tests
│   └── test_put_call_parity.py
├── requirements.txt
├── README.md
├── USAGE.md
├── CONTRIBUTING.md
└── CHANGELOG.md
```

## The Greeks Explained

| Greek | Meaning | Use Case |
|-------|---------|----------|
| **Delta** | Change in option price per $1 spot move | How much exposure do I have? |
| **Gamma** | Change in delta per $1 spot move | How fast is my hedge degrading? |
| **Vega** | Change in option price per 1% vol change | Am I long or short volatility? |
| **Theta** | Daily time decay | How much do I lose each day? |
| **Rho** | Change in option price per 1% rate change | Interest rate sensitivity (small for near-term) |

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_pricing.py -v

# Run with coverage
pytest tests/ --cov=src
```

**Key Tests:**
- Put-call parity validation
- Greek calculation accuracy
- Backtesting historical P&L

## Data Source

Historical Brent crude futures prices from Yahoo Finance (2022-2023). The backtester uses:
- **30-day rolling volatility** (realized, not implied)
- **60-day option expiry** windows
- **4% risk-free rate** (approximation)

## Limitations & Assumptions

1. **European Options Only** — No early exercise. Real commodity options are American-style.

2. **Realized vs Implied Volatility** — The backtest uses realized (historical) volatility. Real trading uses implied vol from option prices.

3. **No Transaction Costs** — Real trading incurs commissions, bid-ask spreads, and slippage.

4. **No Liquidity Constraints** — We assume we can trade any size at mid-price instantly.

5. **Volatility Smile Ignored** — We assume constant volatility across strikes. Real markets price different strikes differently.

6. **No Dividends** — Brent futures don't pay dividends.

7. **Historical Analysis Only** — Past performance is not predictive of future returns.

## Model Details

### Black-76 Formula
For a commodity futures option:

**Call Price:**
```
C = e^(-rT) * [F*N(d1) - K*N(d2)]
```

**Put Price:**
```
P = e^(-rT) * [K*N(-d2) - F*N(-d1)]
```

Where:
- F = Forward price = S * e^(r*T)
- K = Strike price
- T = Time to expiry
- r = Risk-free rate
- σ = Volatility
- N(x) = Cumulative normal distribution
- d1 = [ln(F/K) + (σ²/2)T] / (σ√T)
- d2 = d1 - σ√T

### Why Black-76 for Futures?
- **Black-Scholes** prices options on spot assets (stocks, indices)
- **Black-76** prices options on futures contracts
- For commodity futures, Black-76 is standard because it uses forward prices, not spot prices

## Attribution

This model was developed with Claude AI (Anthropic).

All code, documentation, and backtesting framework were created by Claude Haiku 4.5 as a learning project to understand options pricing, Greeks calculations, and rigorous edge analysis.

**Key insight:** Use this project to learn not just how to build options models, but how to honestly evaluate whether a model actually found a trading edge or is just capturing directional/gamma effects.

---

## References

- **Black, F., 1976.** "The Pricing of Commodity Contracts"
- **Hull, J.C., 2021.** "Options, Futures, and Other Derivatives" (10th Ed.)
- **Taleb, N.N., 2015.** "Antifragile: Things That Gain from Disorder"

## License

MIT License — feel free to use this for learning and educational purposes.

---

## Next Steps

To extend this model:

1. **Implied Volatility Calculation** — Back out IV from real option prices to compare with realized vol
2. **American Options** — Add binomial tree for early-exercise valuation
3. **Volatility Surface** — Model how implied vol varies by strike and maturity
4. **Monte Carlo** — Price exotic options (Asian, barrier, etc.)
5. **Real-time Trading** — Connect to a broker API for live pricing

---