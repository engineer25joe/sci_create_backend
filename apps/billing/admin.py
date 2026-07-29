from django.contrib import admin

from apps.billing.models import CreditTransaction, CreditWallet, Plan, Subscription


@admin.register(CreditWallet)
class CreditWalletAdmin(admin.ModelAdmin):
    list_display = ("workspace", "balance", "updated_at")
    search_fields = ("workspace__name",)


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ("wallet", "transaction_type", "amount", "reason", "created_at")
    list_filter = ("transaction_type",)
    readonly_fields = [f.name for f in CreditTransaction._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "billing_interval", "price_minor_units", "currency", "monthly_credit_allowance", "is_active")
    list_filter = ("tier", "billing_interval", "is_active")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("workspace", "plan", "status", "current_period_end")
    list_filter = ("status",)
    search_fields = ("workspace__name",)
