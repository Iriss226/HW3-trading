# tests/test_engine.py
from unittest.mock import MagicMock
import sys
import os

# Add the parent directory (hw3) to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trading.engine import Engine
from trading.subject import MarketDataSubject
from trading.broker import Broker

def test_engine_uses_strategy_observer_signal(prices):
    subject = MarketDataSubject()
    fake_strategy = MagicMock()
    fake_strategy.last_signal = 0

    broker = Broker(cash=1_000)

    # Attach fake strategy as an observer
    subject.attach(fake_strategy)

    engine = Engine(subject, fake_strategy, broker)

    # You can control fake_strategy.last_signal over time via side_effect
    # or by updating it in a custom observer implementation for more realism.

    equity = engine.run(prices)

    # Assert broker was called appropriately, equity consistent, etc.