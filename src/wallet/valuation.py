"""Valuation domain service."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ValuationResult:
    total: float
    currency: str


class ValuationService:
    def __init__(self, rate_provider):
        self._rate_provider = rate_provider

    def value(self, wallet, currency):
        total = sum(
            stock.quantity * self._rate_provider.rate(stock.stock_type, currency)
            for stock in wallet.stocks
        )
        return ValuationResult(total=total, currency=currency)
