from django.contrib import admin
from .models import Counterparty


@admin.register(Counterparty)
class CounterpartyAdmin(admin.ModelAdmin):
    list_display = ['name',]
    search_fields = ['name']