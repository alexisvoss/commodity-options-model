import numpy as np
from scipy.stats import norm
from src.black_scholes import BlackScholesModel

class GreeksCalculator(BlackScholesModel):
    """
    Calculate option Greeks for risk management.
    
    Greeks are measures of how sensitive an option price is to changes in:
    - Delta: Spot price movement
    - Gamma: Delta sensitivity (convexity)
    - Vega: Volatility changes
    - Theta: Time passage (time decay)
    - Rho: Interest rate changes
    
    Inherits from BlackScholesModel, so we can use S, K, T, r, sigma attributes
    and the _calculate_d1_d2() method.
    """
    
    def delta(self, option_type: str = 'call') -> float:
        """
        Delta: Rate of change of option price with respect to spot price.
        
        What it means:
        - Delta of 0.5 means if the stock goes up $1, option price goes up ~$0.50
        - Call delta ranges from 0 to 1 (ITM calls approach 1, OTM approach 0)
        - Put delta ranges from -1 to 0 (ITM puts approach -1, OTM approach 0)
        
        Formula:
        - Call delta = N(d1)
        - Put delta = N(d1) - 1
        
        Args:
            option_type: 'call' or 'put'
        
        Returns:
            Delta value (sensitivity to spot price changes)
        """
        d1, _ = self._calculate_d1_d2()
        if option_type == 'call':
            return norm.cdf(d1)
        elif option_type == 'put':
            return norm.cdf(d1) - 1
        else:
            raise ValueError("option_type must be 'call' or 'put'")
    
    def gamma(self) -> float:
        """
        Gamma: Rate of change of delta with respect to spot price.
        
        What it means:
        - Gamma tells you how much delta will change if the spot price moves
        - High gamma = delta changes quickly (risky)
        - Low gamma = delta changes slowly (stable)
        - Same for calls and puts (always positive)
        
        Formula: Γ = n(d1) / (S * σ * √T)
        
        Where n(d1) = standard normal probability density function
        
        Returns:
            Gamma value (always positive, same for calls and puts)
        """
        d1, _ = self._calculate_d1_d2()
        gamma = norm.pdf(d1) / (self.S * self.sigma * np.sqrt(self.T))
        return gamma
    
    def vega(self) -> float:
        """
        Vega: Rate of change of option price with respect to volatility.
        
        What it means:
        - Vega of 0.2 means if volatility increases 1%, option price increases $0.20
        - Higher volatility = higher option prices (more uncertainty = more valuable)
        - Same for calls and puts (always positive)
        
        Formula: ν = S * n(d1) * √T
        
        Returns:
            Vega per 1% change in volatility (divided by 100 for convention)
        """
        d1, _ = self._calculate_d1_d2()
        # We divide by 100 because this is "vega per 1% volatility change"
        vega = self.S * norm.pdf(d1) * np.sqrt(self.T) / 100
        return vega
    
    def theta(self, option_type: str = 'call') -> float:
        """
        Theta: Rate of change of option price with respect to time.
        
        What it means:
        - Theta is usually NEGATIVE (time decay hurts long option holders)
        - Theta of -0.05 means you lose ~$0.05 per day if other factors unchanged
        - As expiration approaches, theta accelerates (time decay speeds up)
        
        Formula:
        - Call theta = -S*n(d1)*σ/(2√T) - r*K*e^(-rT)*N(d2)
        - Put theta = -S*n(d1)*σ/(2√T) + r*K*e^(-rT)*N(-d2)
        
        Args:
            option_type: 'call' or 'put'
        
        Returns:
            Theta per day (we divide by 365 to convert from yearly to daily)
        """
        d1, d2 = self._calculate_d1_d2()
        
        # First term: time decay from volatility
        term1 = -self.S * norm.pdf(d1) * self.sigma / (2 * np.sqrt(self.T))
        
        if option_type == 'call':
            # Second term: effect of interest rates on calls
            term2 = -self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
            theta = term1 + term2
        elif option_type == 'put':
            # Second term: effect of interest rates on puts (opposite sign)
            term2 = self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-d2)
            theta = term1 + term2
        else:
            raise ValueError("option_type must be 'call' or 'put'")
        
        # Convert from annual to daily (divide by 365)
        return theta / 365
    
    def rho(self, option_type: str = 'call') -> float:
        """
        Rho: Rate of change of option price with respect to interest rate.
        
        What it means:
        - Rho measures sensitivity to interest rate changes
        - Call rho is positive (higher rates → higher call prices)
        - Put rho is negative (higher rates → lower put prices)
        - Rho is usually small compared to other Greeks
        
        Formula:
        - Call rho = K * T * e^(-rT) * N(d2)
        - Put rho = -K * T * e^(-rT) * N(-d2)
        
        Args:
            option_type: 'call' or 'put'
        
        Returns:
            Rho per 1% interest rate change (divided by 100 for convention)
        """
        _, d2 = self._calculate_d1_d2()
        
        if option_type == 'call':
            rho = self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(d2) / 100
        elif option_type == 'put':
            rho = -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-d2) / 100
        else:
            raise ValueError("option_type must be 'call' or 'put'")
        
        return rho
    
    def all_greeks(self, option_type: str = 'call') -> dict:
        """
        Calculate all Greeks at once.
        
        This is convenient when you want the complete risk profile.
        
        Args:
            option_type: 'call' or 'put'
        
        Returns:
            Dictionary with all Greek values plus the option price
        """
        return {
            'price': self.call_price() if option_type == 'call' else self.put_price(),
            'delta': self.delta(option_type),
            'gamma': self.gamma(),
            'vega': self.vega(),
            'theta': self.theta(option_type),
            'rho': self.rho(option_type)
        }