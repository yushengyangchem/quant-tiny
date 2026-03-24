from .core import Bar, Order, Portfolio, Position, Side, Strategy


class Backtest:
    def __init__(
        self, data: list[Bar], strategy: Strategy, initial_cash: float = 100000.0
    ):
        self.data = data
        self.strategy = strategy
        self.portfolio = Portfolio(initial_cash, Position(0.0, 0.0))
        self.trades: list[Order] = []

    def run(self) -> dict:
        if not self.data:
            return {
                "final_value": self.portfolio.cash,
                "total_trades": 0,
                "orders": self.trades,
            }

        for bar in self.data:
            orders = self.strategy.on_bar(bar, self.portfolio)
            for order in orders:
                self._execute_order(order, bar)

        final_value = self._calculate_portfolio_value(self.data[-1])
        return {
            "final_value": final_value,
            "total_trades": len(self.trades),
            "orders": self.trades,
        }

    def _execute_order(self, order: Order, bar: Bar):
        if order.side == Side.BUY:
            cost = order.quantity * order.price
            if cost <= self.portfolio.cash:
                current_quantity = self.portfolio.position.quantity
                new_quantity = current_quantity + order.quantity
                self.portfolio.cash -= cost
                self.portfolio.position.quantity = new_quantity
                self.portfolio.position.avg_price = (
                    current_quantity * self.portfolio.position.avg_price
                    + order.quantity * order.price
                ) / new_quantity
                self.trades.append(order)
        elif order.side == Side.SELL:
            if order.quantity <= self.portfolio.position.quantity:
                revenue = order.quantity * order.price
                self.portfolio.cash += revenue
                self.portfolio.position.quantity -= order.quantity
                if self.portfolio.position.is_flat:
                    self.portfolio.position.avg_price = 0.0
                self.trades.append(order)

    def _calculate_portfolio_value(self, bar: Bar) -> float:
        return self.portfolio.cash + (self.portfolio.position.quantity * bar.close)
