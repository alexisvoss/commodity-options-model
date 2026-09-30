import pytest
import numpy as np
from src.black_scholes import BlackScholesModel

class TestBlackScholesModel:
    """Test suite for the Black-Scholes pricing model"""
    
    def test_call_price_basic(self):
        """
        Test that the call price calculation works and returns a reasonable value.
        
        For an at-the-money (ATM) option (spot = strike = 100):
        - The call price should be between 10 and 15 for these parameters
        - This is a sanity check
        """
        model = BlackScholesModel(
            spot_price=100,
            strike_price=100,
            time_to_expiry=1,
            risk_free_rate=0.05,
            volatility=0.2
        )
        call = model.call_price()
        assert 10 < call < 15, f"Call price {call} is outside expected range"
    
    def test_put_price_basic(self):
        """Test that put price calculation works"""
        model = BlackScholesModel(
            spot_price=100,
            strike_price=100,
            time_to_expiry=1,
            risk_free_rate=0.05,
            volatility=0.2
        )
        put = model.put_price()
        assert 5 < put < 10, f"Put price {put} is outside expected range"
    
    def test_put_call_parity(self):
        """
        Test put-call parity relationship.
        
        Put-call parity states: Call - Put = S - K*e^(-rT)
        This is a fundamental relationship that must hold for European options.
        
        If this test passes, it means our pricing formulas are consistent!
        """
        model = BlackScholesModel(
            spot_price=100,
            strike_price=100,
            time_to_expiry=1,
            risk_free_rate=0.05,
            volatility=0.2
        )
        call = model.call_price()
        put = model.put_price()
        
        # Left side of parity equation
        parity_lhs = call - put
        
        # Right side of parity equation
        parity_rhs = 100 - 100 * np.exp(-0.05 * 1)
        
        # They should be very close (within 0.01)
        assert abs(parity_lhs - parity_rhs) < 0.01, \
            f"Put-call parity failed: {parity_lhs} != {parity_rhs}"
    
    def test_invalid_inputs(self):
        """
        Test that the model rejects invalid inputs.
        
        We should get an error if we try to pass negative prices or volatility.
        """
        # Test negative spot price
        with pytest.raises(ValueError):
            BlackScholesModel(-100, 100, 1, 0.05, 0.2)
        
        # Test negative volatility
        with pytest.raises(ValueError):
            BlackScholesModel(100, 100, 1, 0.05, -0.2)
        
        # Test zero time to expiry
        with pytest.raises(ValueError):
            BlackScholesModel(100, 100, 0, 0.05, 0.2)
    
    def test_prices_dictionary(self):
        """Test that the prices() method returns a dictionary with both prices"""
        model = BlackScholesModel(90, 95, 0.25, 0.04, 0.30)
        prices = model.prices()
        
        assert isinstance(prices, dict), "prices() should return a dictionary"
        assert 'call' in prices, "Dictionary should have 'call' key"
        assert 'put' in prices, "Dictionary should have 'put' key"
        assert prices['call'] > 0, "Call price should be positive"
        assert prices['put'] > 0, "Put price should be positive":