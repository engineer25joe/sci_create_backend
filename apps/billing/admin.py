from django.contrib import admin

from apps.billing.models import CreditTransaction, CreditWallet


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
