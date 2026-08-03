from django.urls import path

from apps.billing.views import CreditBalanceView

app_name = "billing"

urlpatterns = [
    path("credits/", CreditBalanceView.as_view(), name="credit_balance"),
]
