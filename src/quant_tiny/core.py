from dataclasses import dataclass
from enum import Enum


class Side(Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass
class Bar:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Order:
    timestamp: str
    side: Side
    quantity: float
    price: float


@dataclass
class Position:
    quantity: float
    avg_price: float

    @property
    def is_flat(self) -> bool:
        return self.quantity == 0


@dataclass
class Portfolio:
    cash: float
    position: Position

    @property
    def equity(self) -> float:
        return self.cash + (self.position.quantity * self.position.avg_price)


class Strategy:
    def __init__(self):
        self.orders: list[Order] = []

    def on_bar(self, bar: Bar, portfolio: Portfolio) -> list[Order]:
        raise NotImplementedError

    def buy(self, timestamp: str, quantity: float, price: float) -> Order:
        order = Order(timestamp, Side.BUY, quantity, price)
        self.orders.append(order)
        return order

    def sell(self, timestamp: str, quantity: float, price: float) -> Order:
        order = Order(timestamp, Side.SELL, quantity, price)
        self.orders.append(order)
        return order
