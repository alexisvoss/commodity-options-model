import numpy as np
from scipy.stats import norm
from typing import Tuple, Dict

class BlackScholesModel:
    """European option pricing using Black-Scholes formula"""
    
    def __init__(self, spot_price: float, strike_price: float, 
                 time_to_expiry: float, risk_free_rate: float, 
                 volatility: float):
        """
        Initialize the Black-Scholes model with option parameters.
        
        Args:
            spot_price: Current asset price (S) - e.g., current oil price
            strike_price: Option strike price (K) - the price you can buy/sell at
            time_to_expiry: Time to expiration in years (T) - e.g., 0.25 for 3 months
            risk_free_rate: Annual risk-free rate (r) - e.g., 0.05 for 5%
            volatility: Annual volatility (σ) - e.g., 0.20 for 20%
        """
        self.S = spot_price
        self.K = strike_price
        self.T = time_to_expiry
        self.r = risk_free_rate
        self.sigma = volatility
        
        # Input validation - make sure the inputs make sense
        if any(x <= 0 for x in [spot_price, strike_price, time_to_expiry, volatility]):
            raise ValueError("Spot, strike, time, and volatility must be positive")
        if risk_free_rate < 0:
            raise ValueError("Risk-free rate cannot be negative")
    
    def _calculate_d1_d2(self) -> Tuple[float, float]:
        """
        Calculate d1 and d2 from the Black-Scholes formula.
        
        These are intermediate values needed for the pricing formula.
        d1 and d2 measure how many standard deviations the spot price 
        is from the strike price.
        
        Returns:
            Tuple of (d1, d2) values
        """
        d1 = (np.log(self.S / self.K) + 
              (self.r + 0.5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        return d1, d2
    
    def call_price(self) -> float:
        """
        Calculate European call option price.
        
        A call option gives you the right to BUY at the strike price.
        Formula: C = S*N(d1) - K*e^(-rT)*N(d2)
        
        Where:
        - S = spot price
        - N(d) = cumulative normal distribution (probability)
        - K = strike price
        - e^(-rT) = discount factor (present value)
        
        Returns:
            The fair price of the call option
        """
        d1, d2 = self._calculate_d1_d2()
        call = (self.S * norm.cdf(d1) - 
                self.K * np.exp(-self.r * self.T) * norm.cdf(d2))
        return call
    
    def put_price(self) -> float:
        """
        Calculate European put option price.
        
        A put option gives you the right to SELL at the strike price.
        Formula: P = K*e^(-rT)*N(-d2) - S*N(-d1)
        
        Returns:
            The fair price of the put option
        """
        d1, d2 = self._calculate_d1_d2()
        put = (self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - 
               self.S * norm.cdf(-d1))
        return put
    
    def prices(self) -> Dict[str, float]:
        """
        Return both call and put prices in a dictionary.
        
        Returns:
            Dictionary with 'call' and 'put' keys and their prices
        """
        return {
            'call': self.call_price(),
            'put': self.put_price()
        }