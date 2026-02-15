from abc import ABC, abstractmethod
from typing import List, Any

class Observer(ABC):
    """Base observer interface for market data updates"""
    @abstractmethod
    def update(self, price: float) -> None:
        pass

class MarketDataSubject:
    """Subject that maintains observers and notifies them of price updates"""
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer to receive price updates"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer from receiving updates"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, price: float) -> None:
        """Notify all attached observers of price update"""
        for observer in self._observers:
            observer.update(price)