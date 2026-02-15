# tests/test_observers.py
def test_logger_records_all_prices(subject, logger, prices):
    subject.attach(logger)
    for p in prices:
        subject.notify(float(p))

    assert logger.prices[0] == float(prices.iloc[0])
    assert len(logger.prices) == len(prices)