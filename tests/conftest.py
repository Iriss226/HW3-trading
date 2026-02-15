# tests/conftest.py
import numpy as np
import pandas as pd
import pytest
import sys
import os

# Add the parent directory (hw3) to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.subject import MarketDataSubject
from trading.observers import VolatilityBreakoutStrategyObserver, RiskObserver, LoggerObserver
from trading.broker import Broker
from trading.engine import Engine

# Price series fixtures
@pytest.fixture
def prices():
    """Default price series - steady uptrend"""
    return pd.Series(np.linspace(100, 120, 200))

@pytest.fixture
def volatile_prices():
    """Volatile price series that should generate signals"""
    # Create price series with some breakouts
    base = np.linspace(100, 110, 150)
    spikes = np.array([115, 105, 118, 95, 120])  # Add some spikes
    return pd.Series(np.concatenate([base, spikes]))

@pytest.fixture
def downward_prices():
    """Downward trending price series"""
    return pd.Series(np.linspace(120, 80, 150))

@pytest.fixture
def short_prices():
    """Short price series for testing window limits"""
    return pd.Series([100, 101, 102, 103, 104])

@pytest.fixture
def single_price():
    """Single price for edge case testing"""
    return pd.Series([100.0])

@pytest.fixture
def empty_prices():
    """Empty price series for edge case testing"""
    return pd.Series([])

# Subject fixtures
@pytest.fixture
def subject():
    """Market data subject fixture"""
    return MarketDataSubject()

@pytest.fixture
def subject_with_observers(strategy, risk, logger):
    """Subject with all observers attached"""
    subject = MarketDataSubject()
    subject.attach(strategy)
    subject.attach(risk)
    subject.attach(logger)
    return subject

# Observer fixtures
@pytest.fixture
def strategy():
    """Strategy observer with default window"""
    return VolatilityBreakoutStrategyObserver(window=20)

@pytest.fixture
def strategy_small_window():
    """Strategy observer with small window for testing"""
    return VolatilityBreakoutStrategyObserver(window=5)

@pytest.fixture
def strategy_large_window():
    """Strategy observer with large window"""
    return VolatilityBreakoutStrategyObserver(window=50)

@pytest.fixture
def risk():
    """Risk observer with default limits"""
    return RiskObserver(max_position=1000, max_exposure=100000)

@pytest.fixture
def risk_strict():
    """Risk observer with strict limits"""
    return RiskObserver(max_position=10, max_exposure=5000)

@pytest.fixture
def risk_lenient():
    """Risk observer with lenient limits"""
    return RiskObserver(max_position=10000, max_exposure=1000000)

@pytest.fixture
def logger():
    """Logger observer fixture"""
    return LoggerObserver()

# Broker fixtures
@pytest.fixture
def broker():
    """Broker with default cash"""
    return Broker(cash=1_000)

@pytest.fixture
def broker_rich():
    """Broker with lots of cash"""
    return Broker(cash=1_000_000)

@pytest.fixture
def broker_poor():
    """Broker with very little cash"""
    return Broker(cash=1_000)

@pytest.fixture
def broker_with_position(broker):
    """Broker with an existing position"""
    broker.market_order('buy', 100, 100.0)
    return broker

# Engine fixtures
@pytest.fixture
def engine(subject, strategy, broker):
    """Basic engine with required components"""
    return Engine(subject, strategy, broker)

@pytest.fixture
def engine_with_risk(subject, strategy, broker, risk):
    """Engine with risk observer"""
    return Engine(subject, strategy, broker, risk=risk)

@pytest.fixture
def engine_with_logger(subject, strategy, broker, logger):
    """Engine with logger observer"""
    return Engine(subject, strategy, broker, logger=logger)

@pytest.fixture
def engine_full(subject, strategy, broker, risk, logger):
    """Engine with all observers"""
    return Engine(subject, strategy, broker, risk=risk, logger=logger)

# Combined fixtures for complex tests
@pytest.fixture
def all_components(strategy, risk, logger, broker):
    """All components for testing"""
    subject = MarketDataSubject()
    subject.attach(strategy)
    subject.attach(risk)
    subject.attach(logger)
    return {
        'subject': subject,
        'strategy': strategy,
        'risk': risk,
        'logger': logger,
        'broker': broker
    }

# Test data fixtures
@pytest.fixture
def expected_signals():
    """Expected signals for specific price patterns"""
    return {
        'buy_pattern': [100, 101, 102, 103, 115],  # Should generate buy
        'sell_pattern': [100, 99, 98, 97, 85],      # Should generate sell
        'hold_pattern': [100, 101, 102, 101, 102]   # Should hold
    }

@pytest.fixture
def trade_scenarios():
    """Different trading scenarios for testing"""
    return {
        'profitable_trade': {
            'buy_price': 100,
            'sell_price': 120,
            'qty': 10,
            'expected_profit': 200
        },
        'losing_trade': {
            'buy_price': 100,
            'sell_price': 80,
            'qty': 10,
            'expected_loss': -200
        },
        'breakeven_trade': {
            'buy_price': 100,
            'sell_price': 100,
            'qty': 10,
            'expected_profit': 0
        }
    }

# Mock fixtures for testing
@pytest.fixture
def mock_strategy(mocker):
    """Mocked strategy observer for isolated testing"""
    strategy = mocker.Mock(spec=VolatilityBreakoutStrategyObserver)
    strategy.last_signal = 0
    strategy.window = 20
    return strategy

@pytest.fixture
def mock_risk(mocker):
    """Mocked risk observer for isolated testing"""
    risk = mocker.Mock(spec=RiskObserver)
    risk.is_safe_to_trade.return_value = True
    risk.max_position = 1000
    return risk

@pytest.fixture
def mock_logger(mocker):
    """Mocked logger observer for isolated testing"""
    logger = mocker.Mock(spec=LoggerObserver)
    return logger

@pytest.fixture
def mock_broker(mocker):
    """Mocked broker for isolated testing"""
    broker = mocker.Mock(spec=Broker)
    broker.cash = 1000
    broker.position = 0
    broker.get_equity.return_value = 1000
    return broker

# Parameterized test data
@pytest.fixture(params=[5, 10, 20, 50])
def strategy_window(request):
    """Parameterized strategy window sizes"""
    return VolatilityBreakoutStrategyObserver(window=request.param)

@pytest.fixture(params=[100, 1000, 10000])
def broker_cash(request):
    """Parameterized broker cash amounts"""
    return Broker(cash=request.param)

@pytest.fixture(params=[10, 100, 1000])
def risk_max_position(request):
    """Parameterized risk max positions"""
    return RiskObserver(max_position=request.param)

# Helper fixtures for specific test scenarios
@pytest.fixture
def breakout_scenario():
    """Complete breakout scenario with expected results"""
    prices = pd.Series([100, 101, 102, 103, 115, 114, 113, 112, 100])
    expected_signals = [0, 0, 0, 0, 1, 0, 0, 0, -1]  # Buy at 115, sell at 100
    return {
        'prices': prices,
        'expected_signals': expected_signals,
        'expected_trades': 2  # One buy, one sell
    }

@pytest.fixture
def no_breakout_scenario():
    """Scenario with no breakouts"""
    prices = pd.Series([100, 101, 102, 101, 102, 101, 102, 101, 102])
    expected_signals = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    return {
        'prices': prices,
        'expected_signals': expected_signals,
        'expected_trades': 0
    }

# Performance testing fixtures
@pytest.fixture
def long_price_series():
    """Long price series for performance testing"""
    return pd.Series(np.random.randn(1000) * 10 + 100)

@pytest.fixture
def price_series_with_dates():
    """Price series with datetime index"""
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    prices = np.linspace(100, 120, 200) + np.random.randn(200) * 2
    return pd.Series(prices, index=dates)

# Environment fixtures
@pytest.fixture(autouse=True)
def set_random_seed():
    """Set random seed for reproducibility"""
    np.random.seed(42)
    yield
    # No cleanup needed

# Monkeypatch fixtures for testing edge cases
@pytest.fixture
def failing_broker(monkeypatch):
    """Broker that fails on certain conditions"""
    def failing_market_order(self, side, qty, price):
        if price > 1000:  # Fail on extreme prices
            raise RuntimeError("Price too high")
        return original_market_order(self, side, qty, price)
    
    original_market_order = Broker.market_order
    monkeypatch.setattr(Broker, 'market_order', failing_market_order)
    return Broker(cash=100000)