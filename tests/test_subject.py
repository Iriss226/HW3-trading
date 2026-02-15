import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory (hw3) to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock
from trading.subject import MarketDataSubject

def test_attach_and_notify_calls_update():
    subject = MarketDataSubject()
    obs = MagicMock()
    subject.attach(obs)

    subject.notify(101.0)

    obs.update.assert_called_once_with(101.0)


def test_detach_stops_notifications():
    subject = MarketDataSubject()
    obs = MagicMock()
    subject.attach(obs)
    subject.detach(obs)

    subject.notify(101.0)

    obs.update.assert_not_called()