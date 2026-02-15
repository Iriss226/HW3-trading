# trading/engine.py
import pandas as pd
from typing import Optional, List, Dict, Any
from .subject import MarketDataSubject
from .observers import VolatilityBreakoutStrategyObserver, RiskObserver, LoggerObserver
from .broker import Broker

class Engine:
    def __init__(
        self,
        subject: MarketDataSubject,
        strategy: VolatilityBreakoutStrategyObserver,
        broker: Broker,
        risk: Optional[RiskObserver] = None,
        logger: Optional[LoggerObserver] = None,
    ):
        self.subject = subject
        self.strategy = strategy
        self.broker = broker
        self.risk = risk
        self.logger = logger
        
        # Attach observers to subject if not already attached
        if self.strategy not in self.subject._observers:
            self.subject.attach(self.strategy)
        if self.risk and self.risk not in self.subject._observers:
            self.subject.attach(self.risk)
        if self.logger and self.logger not in self.subject._observers:
            self.subject.attach(self.logger)
        
        # Track performance
        self.equity_curve: List[float] = []
        self.trade_log: List[Dict[str, Any]] = []

    def run(self, prices: pd.Series) -> float:
        """
        Run trading simulation on price series
        
        Args:
            prices: Pandas Series of prices indexed by time
            
        Returns:
            float: Final equity (cash + position value)
        """
        self.equity_curve = []  # Reset equity curve
        self.trade_log = []  # Reset trade log
        
        for timestamp, price in prices.items():
            # Notify all observers of price update
            self.subject.notify(price)
            
            # Read strategy signal (from previous price update)
            # Note: signal is based on price history up to previous price
            signal = self.strategy.last_signal
            
            # Log signal if logger is present
            if self.logger:
                self.logger.log_signal(signal)
            
            # Update risk with current position if risk observer exists
            if self.risk:
                self.risk.update_position(self.broker.position)
            
            # Send order to broker if signal != 0 and risk allows
            if signal != 0:
                # Check risk before executing if risk observer exists
                if self.risk and not self.risk.is_safe_to_trade():
                    # Log risk block if logger exists
                    if self.logger:
                        self.logger.log_event(f"Risk block at price {price}, signal {signal}")
                else:
                    # Execute order
                    self._execute_signal(signal, price, timestamp)
            
            # Record equity
            current_equity = self.broker.get_equity(price)
            self.equity_curve.append(current_equity)
        
        # Return final equity
        final_price = prices.iloc[-1] if not prices.empty else 0
        return self.broker.get_equity(final_price)
    
    def _execute_signal(self, signal: int, price: float, timestamp) -> None:
        """Execute trading signal"""
        try:
            if signal == 1:  # Buy signal
                # Determine quantity (simplified: 10% of cash, minimum 1 share)
                max_spend = self.broker.cash * 0.1
                qty = max(1, int(max_spend / price))
                
                # Ensure we don't exceed max position if risk observer exists
                if self.risk:
                    max_allowed = self.risk.max_position - self.broker.position
                    qty = min(qty, max_allowed)
                
                if qty > 0:
                    self.broker.market_order('buy', qty, price)
                    self._log_trade('buy', qty, price, timestamp)
                    
            elif signal == -1:  # Sell signal
                if self.broker.position > 0:
                    # Sell all position (or partial if risk limits)
                    qty = self.broker.position
                    
                    # Check if we should sell only part due to risk
                    if self.risk:
                        # For sell, we want to reduce position, so no max check needed
                        pass
                    
                    self.broker.market_order('sell', qty, price)
                    self._log_trade('sell', qty, price, timestamp)
                    
        except (RuntimeError, ValueError) as e:
            # Log error but continue simulation
            error_msg = f"Order failed at price {price}, signal {signal}: {e}"
            if self.logger:
                self.logger.log_event(error_msg)
            else:
                print(error_msg)
    
    def _log_trade(self, side: str, qty: int, price: float, timestamp) -> None:
        """Log trade execution"""
        trade = {
            'timestamp': timestamp,
            'side': side,
            'qty': qty,
            'price': price,
            'cash_after': self.broker.cash,
            'position_after': self.broker.position
        }
        self.trade_log.append(trade)
        
        # Also log to logger if present
        if self.logger:
            self.logger.log_trade(trade)
    
    def get_equity_curve(self) -> pd.Series:
        """Return equity curve as pandas Series"""
        if not self.equity_curve or not hasattr(prices, 'index'):
            return pd.Series(self.equity_curve)
        return pd.Series(self.equity_curve, index=prices.index)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Return performance summary"""
        if not self.equity_curve:
            return {}
        
        initial_equity = self.equity_curve[0]
        final_equity = self.equity_curve[-1]
        
        return {
            'initial_equity': initial_equity,
            'final_equity': final_equity,
            'total_return': (final_equity / initial_equity - 1) if initial_equity > 0 else 0,
            'total_trades': len(self.trade_log),
            'buy_trades': len([t for t in self.trade_log if t['side'] == 'buy']),
            'sell_trades': len([t for t in self.trade_log if t['side'] == 'sell']),
            'final_cash': self.broker.cash,
            'final_position': self.broker.position
        }