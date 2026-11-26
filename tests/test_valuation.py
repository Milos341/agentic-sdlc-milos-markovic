"""Tests for VALUATION-STORY-001, backend sub-story VALUATION-BE-001.3."""

from wallet.domain import Stock, Wallet
from wallet.valuation import ValuationService


class FakeRateProvider:
    """Fake RateProvider: returns fixed rates, no network involved."""

    def __init__(self, rates):
        self._rates = rates

    def rate(self, stock_type, currency):
        return self._rates[(stock_type, currency)]


def test_valuation_be_001_3_s1_each_stock_is_converted_and_summed():
    # GIVEN a wallet with 2 bitcoin and 3 petroleum
    wallet = Wallet([Stock(2, "bitcoin"), Stock(3, "petroleum")])
    # AND a fake rate provider: 100 USD per bitcoin, 2 USD per petroleum
    rates = FakeRateProvider({("bitcoin", "USD"): 100, ("petroleum", "USD"): 2})
    service = ValuationService(rates)

    # WHEN the wallet is valued in USD
    result = service.value(wallet, "USD")

    # THEN the total is 2 * 100 + 3 * 2 = 206, expressed in USD
    assert result.total == 206
    assert result.currency == "USD"
