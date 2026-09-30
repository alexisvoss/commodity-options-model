# Contributing

Thank you for your interest in this project! This is an educational derivatives pricing model built to demonstrate professional Python development practices.

## Project Status

This is a **completed educational project** that demonstrates:
- Black-Scholes option pricing
- Greeks calculations
- Backtesting framework
- Professional code quality

While contributions are welcome, the core functionality is complete and stable.

## Ways to Contribute

### 1. Bug Reports
Found a bug? Please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Your environment (Python version, OS)

Example:
Title: Call price calculation incorrect for very short expiry

Description:
When time_to_expiry < 0.01 years, the model returns NaN

Steps to reproduce:

Create model with time_to_expiry=0.001
Call model.call_price()
Observe NaN result

Expected: Valid price between 0 and spot_price
Actual: NaN

### 2. Documentation Improvements
- Typos or unclear explanations
- Missing examples
- Better API documentation
- Visual explanations of Greeks

### 3. Code Quality
- Improved error messages
- Additional test cases
- Performance optimizations
- Code style improvements

### 4. New Features
Before implementing new features, please open an issue to discuss:
- What problem does it solve?
- How does it fit with the project?
- Implementation approach

Potential areas:
- American options (early exercise)
- Dividend-paying assets
- Implied volatility calculation
- Additional Greeks (Vanna, Volga)

## Development Setup

### 1. Fork and Clone
```bash
git clone https://github.com/alexisvoss/commodity-options-model.git
cd commodity-options-model
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Make Your Changes
```bash
git checkout -b feature/my-improvement
# Make your changes...
```

### 4. Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src

# Run specific test file
pytest tests/test_black_scholes.py -v
```

### 5. Code Quality
```bash
# Format code
black src/ tests/ examples/

# Lint
pylint src/

# Type checking (if using type hints)
mypy src/
```

### 6. Commit and Push
```bash
git add .
git commit -m "Add feature: [brief description]"
git push origin feature/my-improvement
```

### 7. Open Pull Request
- Describe what you changed and why
- Reference any related issues
- Explain how to test your changes

## Code Style Guidelines

### Python Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where possible
- Write docstrings for all functions and classes
- Keep functions focused and readable

### Example:
```python
def delta(self, option_type: str = 'call') -> float:
    """
    Calculate option delta.
    
    Delta measures the rate of change of option price
    with respect to spot price changes.
    
    Args:
        option_type: 'call' or 'put'
    
    Returns:
        Delta value (call: 0-1, put: -1-0)
    
    Raises:
        ValueError: If option_type is invalid
    """
    d1, _ = self._calculate_d1_d2()
    if option_type == 'call':
        return norm.cdf(d1)
    elif option_type == 'put':
        return norm.cdf(d1) - 1
    else:
        raise ValueError("option_type must be 'call' or 'put'")
```

### Comments
- Explain **why**, not what (code shows what)
- Comment complex mathematical formulas
- Add references to papers/textbooks
- Keep comments up-to-date with code

### Testing
- Add tests for new features
- All tests must pass before PR merge
- Aim for high coverage (>90%)
- Test edge cases and error conditions

## Commit Message Format

Keep commits atomic and well-described:
[Category] Brief description

Longer explanation if needed.

Bullet point 1
Bullet point 2

References: closes #123

**Categories**:
- `fix:` - Bug fix
- `feat:` - New feature
- `docs:` - Documentation
- `test:` - Test additions/fixes
- `refactor:` - Code restructuring
- `perf:` - Performance improvements

**Example**:
feat: Add American option pricing

Implement binomial tree model for American options.
Supports both calls and puts with early exercise.

Binomial tree valuation
Automatic optimal exercise boundary detection
95% accuracy vs market prices (backtested)

References: closes #42

## Pull Request Process

1. **Before you start**: Check for open issues/PRs on the same topic
2. **Make changes**: Follow code style guidelines
3. **Write tests**: All new code must have tests
4. **Document**: Update README/USAGE if needed
5. **Self-review**: Check your own changes first
6. **Submit PR**: 
   - Clear title and description
   - Link to related issues
   - Explain testing approach
7. **Respond to feedback**: Be open to suggestions

## Testing Requirements

All contributions must include tests:

```python
def test_my_new_feature():
    """Test that new feature works correctly"""
    result = my_new_feature(input_data)
    expected = calculate_expected(input_data)
    assert abs(result - expected) < 0.01
```

Run before submitting:
```bash
pytest tests/ -v --cov=src
```

## Review Process

- Automated tests must pass
- Code review for style and correctness
- At least one approval required
- Then merge to main

**Review typically takes**: 2-7 days depending on complexity

## Questions?

- Open an issue for bugs
- Start a discussion for ideas
- Check existing issues first (your question may be answered!)

## Code of Conduct

Be respectful and professional:
- Help others learn
- Admit mistakes gracefully
- Give credit where due
- Focus on the work, not the person

---

Thank you for contributing! 🙏
