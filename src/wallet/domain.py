"""Domain model of the Wallet Valuation context."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Stock:
    quantity: int
    stock_type: str


class Wallet:
    def __init__(self, stocks):
        self.stocks = list(stocks)
