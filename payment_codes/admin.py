from django.contrib import admin

from payment_codes.models import InterrailRuCode, InterrailRuApplication


@admin.register(InterrailRuCode)
class InterrailRuCodeAdmin(admin.ModelAdmin):
    list_display = ["number", "territory", "code_status", "date"]
    search_fields = ["number", "code_status"]
    list_filter = ["code_status", "territory"]


@admin.register(InterrailRuApplication)
class InterrailRuApplicationAdmin(admin.ModelAdmin):
    list_display = ["number", "forwarder", "date"]
    search_fields = ["number", "cargo"]
    list_filter = ["sending_type", "date"]
