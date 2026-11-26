"""Tests for VALUATION-STORY-001, backend sub-stories BE-001.2 and BE-001.3."""

from wallet.domain import Stock, Wallet
from wallet.use_cases import CalculateWalletValueUseCase, WalletNotFound
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


class FakeWalletRepository:
    """Fake WalletRepository: serves wallets by identifier and records loads."""

    def __init__(self, wallets):
        self._wallets = wallets
        self.loaded_ids = []

    def load(self, wallet_id):
        self.loaded_ids.append(wallet_id)
        return self._wallets.get(wallet_id)


class RecordingValuationService:
    """Wraps the real ValuationService to record calls made by the use case."""

    def __init__(self, rate_provider):
        self._delegate = ValuationService(rate_provider)
        self.calls = []

    def value(self, wallet, currency):
        self.calls.append((wallet, currency))
        return self._delegate.value(wallet, currency)


def test_valuation_be_001_2_s1_wallet_is_loaded_and_valued_in_requested_currency():
    # GIVEN a fake WalletRepository holds a wallet with 2 bitcoin and 3 petroleum
    wallet = Wallet([Stock(2, "bitcoin"), Stock(3, "petroleum")])
    repository = FakeWalletRepository({"wallet-1": wallet})
    # AND a fake RateProvider returns 100 USD per bitcoin and 2 USD per petroleum
    rates = FakeRateProvider({("bitcoin", "USD"): 100, ("petroleum", "USD"): 2})
    valuation_service = RecordingValuationService(rates)
    use_case = CalculateWalletValueUseCase(repository, valuation_service)

    # WHEN the use case calculates the wallet value in USD
    result = use_case.calculate("wallet-1", "USD")

    # THEN the repository is asked to load the wallet by its identifier
    assert repository.loaded_ids == ["wallet-1"]
    # AND the Valuation Domain Service is asked to value the loaded wallet in USD
    assert valuation_service.calls == [(wallet, "USD")]
    # AND the result contains the total 206 and the currency USD
    assert result.total == 206
    assert result.currency == "USD"


def test_valuation_be_001_2_s3_no_valuation_is_attempted_for_a_missing_wallet():
    # GIVEN a fake WalletRepository holds no wallet with the requested identifier
    repository = FakeWalletRepository({})
    rates = FakeRateProvider({("bitcoin", "USD"): 100})
    valuation_service = RecordingValuationService(rates)
    use_case = CalculateWalletValueUseCase(repository, valuation_service)

    # WHEN the use case calculates the wallet value in USD
    result = use_case.calculate("missing-wallet", "USD")

    # THEN a not-found use case result is returned for that identifier
    assert isinstance(result, WalletNotFound)
    assert result.wallet_id == "missing-wallet"
    # AND the Valuation Domain Service is not called
    assert valuation_service.calls == []
