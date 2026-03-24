# quant-tiny

A tiny & lightweight quantitative trading framework for learning.

## Installation

```bash
pip install quant-tiny
```

## Quick Start

```python
from quant_tiny import Backtest, Bar, Strategy


class MyStrategy(Strategy):
    def on_bar(self, bar: Bar, portfolio):
        if portfolio.position.is_flat and bar.close > 100:
            return [self.buy(bar.timestamp, 10, bar.close)]
        return []

data = [
    Bar("2024-01-01", 100, 105, 95, 102, 1000),
    Bar("2024-01-02", 102, 108, 100, 106, 1200),
]

backtest = Backtest(data, MyStrategy())
result = backtest.run()
print(f"Final value: ${result['final_value']:.2f}")
print(f"Total trades: {result['total_trades']}")
```

## Run Tests

This project keeps example strategies in `pytest` tests instead of a separate
`examples/` directory.

```bash
pytest -q
```

You can find the demo strategy and regression tests in `tests/test_core.py`.

## Features

- **Core Components**: `Strategy`, `Bar`, `Order`, `Portfolio`, `Position`
- **Backtesting**: Simple event-driven backtest engine
- **Indicators**: `sma()`, `ema()`, `rsi()`

## License

MIT
