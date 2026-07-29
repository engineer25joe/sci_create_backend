"""
billing_service - the only place credit balances are checked or
changed. Never mutate CreditWallet.balance directly elsewhere; always
create a CreditTransaction (its save() keeps the wallet balance in
sync automatically).
"""
from django.db import transaction

from apps.billing.models import CreditTransaction, CreditTransactionType, CreditWallet


class InsufficientCreditsError(Exception):
    def __init__(self, required: int, available: int):
        self.required = required
        self.available = available
        super().__init__(f"Insufficient credits: need {required}, have {available}.")


def get_or_create_wallet(workspace) -> CreditWallet:
    wallet, _ = CreditWallet.objects.get_or_create(workspace=workspace)
    return wallet


def get_balance(workspace) -> int:
    wallet = get_or_create_wallet(workspace)
    return wallet.balance


@transaction.atomic
def grant_credits(*, workspace, amount: int, reason: str = "") -> CreditTransaction:
    wallet = get_or_create_wallet(workspace)
    return CreditTransaction.objects.create(
        wallet=wallet, transaction_type=CreditTransactionType.GRANT, amount=amount, reason=reason
    )


@transaction.atomic
def deduct_credits(*, workspace, amount: int, reason: str = "", related_ai_request=None) -> CreditTransaction:
    """
    amount should be a positive integer (the cost) - this function
    stores it as a negative CreditTransaction.amount internally.
    Raises InsufficientCreditsError if the wallet can't cover it.
    """
    wallet = get_or_create_wallet(workspace)
    if wallet.balance < amount:
        raise InsufficientCreditsError(required=amount, available=wallet.balance)

    return CreditTransaction.objects.create(
        wallet=wallet,
        transaction_type=CreditTransactionType.DEBIT,
        amount=-amount,
        reason=reason,
        related_ai_request=related_ai_request,
    )
