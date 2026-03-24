import pytest

from quant_tiny import Backtest, Bar, Portfolio, Position, Strategy, ema, rsi, sma


class SimpleStrategy(Strategy):
    def on_bar(self, bar: Bar, portfolio):
        if bar.close > 100 and portfolio.position.is_flat:
            return [self.buy(bar.timestamp, 10, bar.close)]
        return []


class SMACrossoverStrategy(Strategy):
    def __init__(self, short_period: int = 2, long_period: int = 3):
        super().__init__()
        self.short_period = short_period
        self.long_period = long_period
        self.bars_history: list[Bar] = []

    def on_bar(self, bar: Bar, portfolio):
        self.bars_history.append(bar)

        if len(self.bars_history) < self.long_period:
            return []

        closes = [item.close for item in self.bars_history]
        short_sma = sum(closes[-self.short_period :]) / self.short_period
        long_sma = sum(closes[-self.long_period :]) / self.long_period

        if short_sma > long_sma and portfolio.position.is_flat:
            quantity = int(portfolio.cash // bar.close)
            if quantity > 0:
                return [self.buy(bar.timestamp, quantity, bar.close)]

        if short_sma < long_sma and not portfolio.position.is_flat:
            return [self.sell(bar.timestamp, portfolio.position.quantity, bar.close)]

        return []


def test_bar_creation():
    bar = Bar("2024-01-01", 100.0, 105.0, 95.0, 102.0, 1000.0)
    assert bar.open == 100.0
    assert bar.close == 102.0


def test_backtest_simple():
    data = [
        Bar("2024-01-01", 100, 105, 95, 102, 1000),
        Bar("2024-01-02", 102, 108, 100, 106, 1200),
    ]
    strategy = SimpleStrategy()
    backtest = Backtest(data, strategy, initial_cash=10000)
    result = backtest.run()

    assert result["total_trades"] == 1
    assert result["orders"][0].price == 102
    assert result["final_value"] == 10040


def test_backtest_handles_empty_data():
    strategy = SimpleStrategy()
    backtest = Backtest([], strategy, initial_cash=5000)

    result = backtest.run()

    assert result == {"final_value": 5000, "total_trades": 0, "orders": []}


def test_backtest_updates_weighted_average_price_and_resets_on_exit():
    portfolio = Portfolio(cash=1000, position=Position(0.0, 0.0))
    strategy = SimpleStrategy()
    backtest = Backtest([], strategy, initial_cash=1000)
    backtest.portfolio = portfolio

    backtest._execute_order(
        strategy.buy("2024-01-01", 2, 100), Bar("2024-01-01", 0, 0, 0, 100, 0)
    )
    backtest._execute_order(
        strategy.buy("2024-01-02", 2, 200), Bar("2024-01-02", 0, 0, 0, 200, 0)
    )

    assert backtest.portfolio.position.quantity == 4
    assert backtest.portfolio.position.avg_price == 150
    assert backtest.portfolio.equity == 1000

    backtest._execute_order(
        strategy.sell("2024-01-03", 4, 180), Bar("2024-01-03", 0, 0, 0, 180, 0)
    )

    assert backtest.portfolio.position.quantity == 0
    assert backtest.portfolio.position.avg_price == 0.0


def test_sma_indicator():
    bars = [Bar(str(i), i, i, i, i, 100) for i in range(1, 11)]
    result = sma(bars, 3)
    assert len(result) == 8
    assert result[0] == 2.0


def test_indicators_handle_insufficient_data():
    bars = [Bar("2024-01-01", 1, 1, 1, 1, 100), Bar("2024-01-02", 2, 2, 2, 2, 100)]

    assert sma(bars, 3) == []
    assert ema(bars, 3) == []
    assert rsi(bars, 3) == []


def test_indicators_reject_non_positive_period():
    bars = [Bar("2024-01-01", 1, 1, 1, 1, 100)]

    with pytest.raises(ValueError):
        sma(bars, 0)

    with pytest.raises(ValueError):
        ema(bars, -1)

    with pytest.raises(ValueError):
        rsi(bars, 0)


def test_ema_indicator():
    bars = [Bar(str(i), i, i, i, i, 100) for i in range(1, 6)]

    result = ema(bars, 3)

    assert result == [2.0, 3.0, 4.0]


def test_rsi_indicator_for_uptrend():
    bars = [Bar(str(i), i, i, i, i, 100) for i in range(1, 7)]

    result = rsi(bars, 3)

    assert result == [100.0, 100.0, 100.0]


def test_sma_crossover_example_behavior():
    data = [
        Bar("2024-01-01", 100, 101, 99, 100, 1000),
        Bar("2024-01-02", 100, 102, 99, 101, 1100),
        Bar("2024-01-03", 101, 105, 100, 104, 1200),
        Bar("2024-01-04", 104, 106, 103, 105, 1200),
        Bar("2024-01-05", 105, 106, 101, 102, 1000),
        Bar("2024-01-06", 102, 103, 97, 98, 1300),
    ]
    strategy = SMACrossoverStrategy()
    backtest = Backtest(data, strategy, initial_cash=10000)

    result = backtest.run()

    assert result["total_trades"] == 2
    assert result["orders"][0].timestamp == "2024-01-03"
    assert result["orders"][0].side.value == "buy"
    assert result["orders"][0].quantity == 96
    assert result["orders"][1].timestamp == "2024-01-05"
    assert result["orders"][1].side.value == "sell"
    assert result["orders"][1].quantity == 96
    assert result["final_value"] == 9808.0
