import numpy as np
from typing import List, Optional, Dict, Any
from collections import deque

class Observer:
    """Base observer interface for market data updates"""
    def update(self, price: float) -> None:
        raise NotImplementedError

class VolatilityBreakoutStrategyObserver(Observer):
    def __init__(self, window: int = 20):
        self.window = window
        self._prices: List[float] = []
        self._last_signal: int = 0
        self._returns: List[float] = []
        
    def update(self, price: float) -> None:
        """
        Maintain price history, compute returns, rolling std,
        and set self._last_signal to -1/0/+1
        """
        # Add new price
        self._prices.append(price)
        
        # Keep only window-sized history
        if len(self._prices) > self.window:
            self._prices.pop(0)
        
        # Calculate return if we have at least 2 prices
        if len(self._prices) >= 2:
            returns = (self._prices[-1] - self._prices[-2]) / self._prices[-2]
            self._returns.append(returns)
            
            # Keep returns same length as prices
            if len(self._returns) > self.window:
                self._returns.pop(0)
        
        # Generate signal if we have enough data
        self._last_signal = self._generate_signal()
    
    def _generate_signal(self) -> int:
        """Generate trading signal based on volatility breakout"""
        if len(self._prices) < self.window or len(self._returns) < 2:
            return 0  # Not enough data
        
        # Calculate rolling volatility (standard deviation of returns)
        volatility = np.std(self._returns)
        latest_return = self._returns[-1]
        
        # Generate signal
        if latest_return > volatility:
            return 1  # Buy signal
        elif latest_return < -volatility:
            return -1  # Sell signal
        return 0  # Hold
    
    @property
    def last_signal(self) -> int:
        return self._last_signal
    
    def get_signal(self) -> int:
        """Alias for last_signal property"""
        return self._last_signal


class RiskObserver(Observer):
    def __init__(self, max_position: int = 1000, max_exposure: float = 100000.0):
        self.max_position = max_position
        self.max_exposure = max_exposure
        self.breached = False
        self.current_position: int = 0
        self.current_price: float = 0.0
        self.alerts: List[str] = []

    def update(self, price: float) -> None:
        """
        Record price and check risk limits
        """
        self.current_price = price
        self._check_limits()
    
    def update_position(self, position: int) -> None:
        """Update current position (called by broker/engine)"""
        self.current_position = position
        self._check_limits()
    
    def _check_limits(self) -> None:
        """Check if any risk limits are breached"""
        # Check position limit
        if abs(self.current_position) > self.max_position:
            if not self.breached:
                self.alerts.append(f"Position limit breached: {self.current_position} > {self.max_position}")
            self.breached = True
        # Check exposure limit
        elif self.current_position * self.current_price > self.max_exposure:
            if not self.breached:
                self.alerts.append(f"Exposure limit breached: {self.current_position * self.current_price} > {self.max_exposure}")
            self.breached = True
        else:
            self.breached = False
    
    def is_safe_to_trade(self) -> bool:
        """Check if it's safe to execute new trades"""
        return not self.breached


class LoggerObserver(Observer):
    def __init__(self):
        self.prices: List[float] = []
        self.signals: List[int] = []
        self.timestamps: List[int] = []
        self._step = 0

    def update(self, price: float) -> None:
        """Append price to self.prices"""
        self.prices.append(price)
        self.timestamps.append(self._step)
        self._step += 1
    
    def log_signal(self, signal: int) -> None:
        """Record trading signal"""
        self.signals.append(signal)
    
    def get_dataframe(self) -> 'pd.DataFrame':
        """Return data as pandas DataFrame"""
        import pandas as pd
        # Align signals with prices (signals may have different length)
        min_length = min(len(self.prices), len(self.signals))
        data = {
            'timestamp': self.timestamps[:min_length],
            'price': self.prices[:min_length],
            'signal': self.signals[:min_length]
        }
        return pd.DataFrame(data)
    
    def clear(self) -> None:
        """Clear all logged data"""
        self.prices.clear()
        self.signals.clear()
        self.timestamps.clear()
        self._step = 0