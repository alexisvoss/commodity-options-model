import pytest
import numpy as np
from src.greeks import GreeksCalculator

class TestGreeksCalculator:
    """Test suite for the Greeks calculations"""
    
    def setup_method(self):
        """
        Setup method runs before each test.
        Creates a model with standard parameters for testing.
        """
        self.model = GreeksCalculator(
            spot_price=100,
            strike_price=100,
            time_to_expiry=0.25,  # 3 months
            risk_free_rate=0.05,
            volatility=0.20
        )
    
    def test_delta_call_range(self):
        """
        Test that call delta is between 0 and 1.
        
        Call delta should ALWAYS be between 0 and 1:
        - OTM calls (spot < strike): delta near 0 (won't be exercised)
        - ATM calls (spot ≈ strike): delta near 0.5 (50% chance)
        - ITM calls (spot > strike): delta near 1 (will be exercised)
        """
        delta = self.model.delta('call')
        assert 0 <= delta <= 1, f"Call delta {delta} out of range [0, 1]"
    
    def test_delta_put_range(self):
        """
        Test that put delta is between -1 and 0.
        
        Put delta should ALWAYS be between -1 and 0:
        - OTM puts (spot > strike): delta near 0
        - ATM puts (spot ≈ strike): delta near -0.5
        - ITM puts (spot < strike): delta near -1
        """
        delta = self.model.delta('put')
        assert -1 <= delta <= 0, f"Put delta {delta} out of range [-1, 0]"
    
    def test_delta_call_put_relationship(self):
        """
        Test the relationship between call and put delta.
        
        Put delta = Call delta - 1
        This follows from put-call parity relationships.
        """
        call_delta = self.model.delta('call')
        put_delta = self.model.delta('put')
        
        expected_put_delta = call_delta - 1
        assert abs(put_delta - expected_put_delta) < 0.0001, \
            f"Put delta {put_delta} != Call delta - 1 ({expected_put_delta})"
    
    def test_gamma_always_positive(self):
        """
        Test that gamma is always positive.
        
        Gamma measures convexity and is always positive for both calls and puts.
        This is because options have positive convexity (you benefit from big moves).
        """
        gamma = self.model.gamma()
        assert gamma > 0, f"Gamma {gamma} should be positive"
    
    def test_gamma_decreases_with_time(self):
        """
        Test that gamma decreases as time to expiry increases.
        
        ATM options have highest gamma near expiry (time decay accelerates).
        OTM/ITM options have lower gamma.
        """
        # Model at 0.25 years (3 months)
        gamma_near_expiry = self.model.gamma()
        
        # Model further from expiry (1 year)
        model_far = GreeksCalculator(100, 100, 1.0, 0.05, 0.20)
        gamma_far = model_far.gamma()
        
        # Gamma should be higher when closer to expiry
        assert gamma_near_expiry > gamma_far, \
            f"Gamma near expiry {gamma_near_expiry} should be > gamma far {gamma_far}"
    
    def test_vega_always_positive(self):
        """
        Test that vega is always positive.
        
        Higher volatility increases option prices (both calls and puts).
        So vega is always positive.
        """
        vega = self.model.vega()
        assert vega > 0, f"Vega {vega} should be positive"
    
    def test_vega_increases_with_time(self):
        """
        Test that vega increases with time to expiry.
        
        Longer-dated options have more time for volatility to matter.
        Short-dated options are less sensitive to vol changes.
        """
        vega_near_expiry = self.model.vega()
        
        model_far = GreeksCalculator(100, 100, 1.0, 0.05, 0.20)
        vega_far = model_far.vega()
        
        assert vega_far > vega_near_expiry, \
            f"Vega far {vega_far} should be > vega near {vega_near_expiry}"
    
    def test_theta_call_near_expiry(self):
        """
        Test that theta is negative for long calls near expiry.
        
        Time decay hurts long option holders (you lose money if nothing changes).
        Theta is most negative for ATM options very close to expiry.
        """
        theta = self.model.theta('call')
        # Near expiry, theta should be negative (time decay)
        assert theta < 0, f"Call theta {theta} should be negative (time decay)"
    
    def test_theta_put_near_expiry(self):
        """
        Test that theta is negative for long puts near expiry.
        """
        theta = self.model.theta('put')
        # For ATM puts, theta should typically be negative
        assert theta < 0, f"Put theta {theta} should be negative (time decay)"
    
    def test_rho_call_positive(self):
        """
        Test that call rho is positive.
        
        Higher interest rates increase call option values
        (because the strike price is discounted less).
        """
        rho = self.model.rho('call')
        assert rho > 0, f"Call rho {rho} should be positive"
    
    def test_rho_put_negative(self):
        """
        Test that put rho is negative.
        
        Higher interest rates decrease put option values
        (because you get less interest on the money you're protecting).
        """
        rho = self.model.rho('put')
        assert rho < 0, f"Put rho {rho} should be negative"
    
    def test_all_greeks_returns_complete_dict(self):
        """
        Test that all_greeks returns all necessary values.
        """
        greeks = self.model.all_greeks('call')
        
        required_keys = ['price', 'delta', 'gamma', 'vega', 'theta', 'rho']
        for key in required_keys:
            assert key in greeks, f"Missing key '{key}' in Greeks dictionary"
        
        # All values should be numbers
        for key, value in greeks.items():
            assert isinstance(value, (int, float, np.number)), \
                f"Greek '{key}' should be a number, got {type(value)}"
    
    def test_greeks_for_otm_call(self):
        """
        Test Greeks for an out-of-the-money (OTM) call.
        
        OTM calls (spot < strike):
        - Low delta (unlikely to be exercised)
        - Lower gamma (delta won't change much)
        - Still positive vega (still sensitive to vol)
        """
        # OTM call: spot=90, strike=100
        otm_call = GreeksCalculator(90, 100, 0.25, 0.05, 0.20)
        
        delta = otm_call.delta('call')
        gamma = otm_call.gamma()
        vega = otm_call.vega()
        
        # OTM calls have low delta
        assert delta < 0.5, f"OTM call delta {delta} should be < 0.5"
        # Still positive gamma and vega
        assert gamma > 0, "OTM call gamma should be positive"
        assert vega > 0, "OTM call vega should be positive"
    
    def test_greeks_for_itm_call(self):
        """
        Test Greeks for an in-the-money (ITM) call.
        
        ITM calls (spot > strike):
        - High delta (very likely to be exercised)
        - Lower gamma (delta won't change much more)
        - Still positive vega
        """
        # ITM call: spot=110, strike=100
        itm_call = GreeksCalculator(110, 100, 0.25, 0.05, 0.20)
        
        delta = itm_call.delta('call')
        gamma = itm_call.gamma()
        vega = itm_call.vega()
        
        # ITM calls have high delta
        assert delta > 0.5, f"ITM call delta {delta} should be > 0.5"
        # Still positive gamma and vega
        assert gamma > 0, "ITM call gamma should be positive"
        assert vega > 0, "ITM call vega should be positive"