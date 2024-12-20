from django.contrib import admin

from payment_codes.models import PaymentCode, Territory, Counterparty, Application


@admin.register(PaymentCode)
class PaymentCodeAdmin(admin.ModelAdmin):
    list_display = ["number", "territory", "code_status", "date"]
    search_fields = ["number", "code_status"]
    list_filter = ["code_status", "territory"]


@admin.register(Territory)
class TerritoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Counterparty)
class CounterpartyAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["number", "forwarder", "date"]
    search_fields = ["number", "cargo"]
    list_filter = ["sending_type", "date"]
