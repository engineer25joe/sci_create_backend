import uuid

from django.db import models


class CreditWallet(models.Model):
    """
    One per workspace. balance is a cached/denormalized value kept in
    sync by CreditTransaction.save() - the transactions table is the
    source of truth (append-only ledger), this is just for fast reads.
    """

    workspace = models.OneToOneField(
        "identity.Workspace", on_delete=models.CASCADE, related_name="credit_wallet"
    )
    balance = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.workspace.name} - {self.balance} credits"


class CreditTransactionType(models.TextChoices):
    GRANT = "grant", "Grant (free plan allowance, promo, etc.)"
    PURCHASE = "purchase", "Purchase"
    DEBIT = "debit", "Debit (AI usage)"
    REFUND = "refund", "Refund"


class CreditTransaction(models.Model):
    """
    Append-only ledger - never updated or deleted after creation. The
    wallet's balance is always derived from summing these, and this
    model's save() keeps CreditWallet.balance in sync automatically so
    callers don't have to remember to do it themselves.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(CreditWallet, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=CreditTransactionType.choices)
    amount = models.IntegerField(help_text="Positive for grants/purchases/refunds, negative for debits.")
    reason = models.CharField(max_length=200, blank=True)
    related_ai_request = models.ForeignKey(
        "ai_core.AIRequestLog", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            CreditWallet.objects.filter(pk=self.wallet_id).update(
                balance=models.F("balance") + self.amount
            )

    def __str__(self):
        return f"{self.transaction_type} {self.amount} - {self.wallet.workspace.name}"
