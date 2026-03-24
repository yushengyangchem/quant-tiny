from .core import Bar


def sma(bars: list[Bar], period: int) -> list[float]:
    if period <= 0:
        raise ValueError("period must be a positive integer")
    if len(bars) < period:
        return []
    result = []
    for i in range(period - 1, len(bars)):
        window = [b.close for b in bars[i - period + 1 : i + 1]]
        result.append(sum(window) / period)
    return result


def ema(bars: list[Bar], period: int) -> list[float]:
    if period <= 0:
        raise ValueError("period must be a positive integer")
    if len(bars) < period:
        return []
    multiplier = 2 / (period + 1)
    result = [sma(bars[:period], period)[0]]
    for i in range(period, len(bars)):
        value = (bars[i].close - result[-1]) * multiplier + result[-1]
        result.append(value)
    return result


def rsi(bars: list[Bar], period: int = 14) -> list[float]:
    if period <= 0:
        raise ValueError("period must be a positive integer")
    if len(bars) < period + 1:
        return []
    gains = []
    losses = []
    for i in range(1, len(bars)):
        change = bars[i].close - bars[i - 1].close
        gains.append(max(0, change))
        losses.append(max(0, -change))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    result = []
    if avg_loss == 0:
        result.append(100.0)
    else:
        rs = avg_gain / avg_loss
        result.append(100 - (100 / (1 + rs)))

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(100 - (100 / (1 + rs)))

    return result
