# Register your models here.
from django.contrib import admin

from payment_codes.models import PaymentCode, Territory, Counterparty, Application

admin.site.register(PaymentCode)
admin.site.register(Territory)
admin.site.register(Counterparty)

admin.site.register(Application)
