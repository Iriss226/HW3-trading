# HW3: Observer Pattern Trading System

![CI Status](https://github.com/Iriss226/HW3-trading/workflows/CI%20Pipeline/badge.svg)

A minimal market data broadcasting system implementing the Observer pattern for trading signal generation, risk monitoring, and logging.

## 📋 Table of Contents
- [Design Overview](#design-overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [CI/CD Pipeline](#cicd-pipeline)
- [Implementation Details](#implementation-details)

## 🎯 Design Overview

### Observer Pattern Implementation
The system uses the Observer pattern to decouple market data updates from various components:

- **Subject**: `MarketDataSubject` maintains a list of observers and notifies them of price changes
- **Observers**: Concrete implementations react to price updates:
  - `VolatilityBreakoutStrategyObserver`: Generates trading signals (-1, 0, +1) based on volatility
  - `RiskObserver`: Monitors position and exposure limits
  - `LoggerObserver`: Records all price updates and signals for analysis

### System Components
- **Broker**: Executes market orders, maintains cash and position
- **Engine**: Orchestrates the simulation loop, connecting signals to orders

## 📁 Project Structure
hw3/
├── .github/
│ └── workflows/
│ └── ci.yml # GitHub Actions CI pipeline
├── trading/
│ ├── init.py
│ ├── subject.py # MarketDataSubject implementation
│ ├── observers.py # Strategy, Risk, Logger observers
│ ├── broker.py # Broker for order execution
│ └── engine.py # Main trading engine
├── tests/
│ ├── init.py
│ ├── conftest.py # Pytest fixtures
│ ├── test_subject.py # Subject tests
│ ├── test_observers.py # Observer tests
│ ├── test_broker.py # Broker tests
│ └── test_engine.py # Engine tests
├── requirements.txt # Python dependencies
├── pyproject.toml # Pytest and coverage config
└── README.md # This file


## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip or conda package manager

### Setup with pip

```bash
# Clone the repository
git clone https://github.com/Iriss226/HW3-trading.git
cd HW3-trading

# Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

### Set up with Conda
```bash
# Create conda environment
conda create -n trading_env python=3.9
conda activate trading_env

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage and examples
```python
import pandas as pd
from trading.subject import MarketDataSubject
from trading.observers import VolatilityBreakoutStrategyObserver, RiskObserver, LoggerObserver
from trading.broker import Broker
from trading.engine import Engine

# Create components
subject = MarketDataSubject()
strategy = VolatilityBreakoutStrategyObserver(window=20)
risk = RiskObserver(max_position=1000, max_exposure=100000)
logger = LoggerObserver()
broker = Broker(cash=100000)

# Create engine with all observers
engine = Engine(subject, strategy, broker, risk, logger)

# Run simulation on price data
prices = pd.Series([100, 101, 102, 103, 115, 114, 113, 112, 100])
final_equity = engine.run(prices)

print(f"Final equity: ${final_equity:.2f}")
print(f"Number of trades: {len(broker.trades)}")
```

## Access Logged Data
```python
# Get logged data as DataFrame
df = logger.get_dataframe()
print(df.head())

# Get performance summary
summary = engine.get_performance_summary()
print(summary)
```
## Running test
```bash
pytest
pytest -v
```
## Running test with coverage
```bash
# Run tests and generate coverage report
coverage run -m pytest

# View coverage report in terminal
coverage report

# Generate HTML coverage report
coverage html
# Then open htmlcov/index.html in your browser

```

