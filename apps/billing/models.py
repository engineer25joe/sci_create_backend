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


class PlanTier(models.TextChoices):
    FREE = "free", "Free"
    STARTER = "starter", "Starter"
    PRO = "pro", "Pro"
    AGENCY = "agency", "Agency"


class BillingInterval(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    QUARTERLY = "quarterly", "Quarterly"
    SEMI_ANNUAL = "semi_annual", "Semi-Annual"
    ANNUAL = "annual", "Annual"


class Plan(models.Model):
    """
    A purchasable plan. Price is stored in the smallest currency unit
    (e.g. cents) to avoid floating point issues, per our architecture's
    multi-currency billing design.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tier = models.CharField(max_length=20, choices=PlanTier.choices)
    billing_interval = models.CharField(max_length=20, choices=BillingInterval.choices, default=BillingInterval.MONTHLY)
    name = models.CharField(max_length=100)
    price_minor_units = models.IntegerField(default=0)
    currency = models.CharField(max_length=3, default="KES")
    monthly_credit_allowance = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.billing_interval})"


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"


class Subscription(models.Model):
    """One per workspace - tracks which Plan a workspace is currently on."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.OneToOneField(
        "identity.Workspace", on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.workspace.name} - {self.plan.name} ({self.status})"
