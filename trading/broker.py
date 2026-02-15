# trading/broker.py
from typing import Tuple, List, Dict, Any

class Broker:
    def __init__(self, cash: float = 1_000_000):
        self.cash = cash
        self.position = 0
        self.trades: List[Dict[str, Any]] = []
        
    def market_order(self, side: str, qty: int, price: float) -> None:
        """
        Execute a market order
        Args:
            side: 'buy' or 'sell'
            qty: number of shares to trade
            price: current market price
        Raises:
            ValueError: If side is invalid, qty is negative, or price is non-positive
            RuntimeError: If insufficient cash for buy or insufficient shares for sell
        """
        # Validate inputs
        self._validate_order(side, qty, price)
        
        # Execute order based on side
        if side.lower() == 'buy':
            self._execute_buy(qty, price)
        elif side.lower() == 'sell':
            self._execute_sell(qty, price)
        
        # Record trade
        self.trades.append({
            'side': side.lower(),
            'qty': qty,
            'price': price,
            'cash_after': self.cash,
            'position_after': self.position
        })
    
    def _validate_order(self, side: str, qty: int, price: float) -> None:
        """Validate order parameters"""
        # Check side
        if side.lower() not in ['buy', 'sell']:
            raise ValueError(f"Invalid side: {side}. Must be 'buy' or 'sell'")
        
        # Check quantity
        if qty <= 0:
            raise ValueError(f"Invalid quantity: {qty}. Must be positive")
        
        # Check price
        if price <= 0:
            raise ValueError(f"Invalid price: {price}. Must be positive")
    
    def _execute_buy(self, qty: int, price: float) -> None:
        """Execute a buy order"""
        cost = qty * price
        
        # Check if we have enough cash
        if cost > self.cash:
            raise RuntimeError(f"Insufficient cash: ${self.cash:.2f} < ${cost:.2f}")
        
        # Update cash and position
        self.cash -= cost
        self.position += qty
    
    def _execute_sell(self, qty: int, price: float) -> None:
        """Execute a sell order"""
        # Check if we have enough shares
        if qty > self.position:
            raise RuntimeError(f"Insufficient shares: {self.position} < {qty}")
        
        # Update cash and position
        proceeds = qty * price
        self.cash += proceeds
        self.position -= qty
    
    def get_equity(self, current_price: float) -> float:
        """Calculate total equity (cash + position value)"""
        return self.cash + (self.position * current_price)
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """Return list of executed trades"""
        return self.trades.copy()
    
    def reset(self) -> None:
        """Reset broker to initial state"""
        self.cash = 1_000_000
        self.position = 0
        self.trades.clear()
    
    def __str__(self) -> str:
        """String representation of broker state"""
        return f"Broker(cash={self.cash:.2f}, position={self.position})"