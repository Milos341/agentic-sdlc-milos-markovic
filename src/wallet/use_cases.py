"""Application use cases of the Wallet Valuation context."""


class CalculateWalletValueUseCase:
    def __init__(self, wallet_repository, valuation_service):
        self._wallet_repository = wallet_repository
        self._valuation_service = valuation_service

    def calculate(self, wallet_id, currency):
        wallet = self._wallet_repository.load(wallet_id)
        return self._valuation_service.value(wallet, currency)
