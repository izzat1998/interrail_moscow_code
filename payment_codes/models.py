from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InterrailRuApplication(TimeStampedModel):
    LOADING_TYPE_CHOICES = (
        ('wagon', 'Wagon'),
        ('container', 'Container'),
    )
    SENDING_TYPE_CHOICES = (
        ('single', 'Single'),
        ('block_train', 'Block Train'),
    )

    number = models.CharField(max_length=100, blank=True, unique=True)
    request_file = models.FileField(upload_to='interrail_russian/applications/', blank=True, null=True)
    quantity = models.IntegerField(default=1)
    date = models.DateField(blank=True, null=True)
    paid_telegram = models.CharField(max_length=100, blank=True)
    departure = models.CharField(max_length=100, blank=True)
    departure_code = models.CharField(max_length=100, blank=True)
    destination = models.CharField(max_length=100, blank=True)
    destination_code = models.CharField(max_length=100, blank=True)
    cargo = models.CharField(max_length=100, blank=True)
    hs_code = models.CharField(max_length=100, blank=True)
    etcng = models.CharField(max_length=255, blank=True)
    loading_type = models.CharField(max_length=100, choices=LOADING_TYPE_CHOICES, default='wagon')
    weight = models.CharField(max_length=100, blank=True)
    rolling_stock_1 = models.CharField(max_length=255, blank=True)
    rolling_stock_2 = models.CharField(max_length=255, blank=True)
    conditions_of_carriage = models.CharField(max_length=255, blank=True)
    agreed_rate = models.CharField(max_length=50, blank=True)
    border_crossing = models.CharField(max_length=255, blank=True)
    containers_or_wagons = models.TextField(default='')
    period = models.CharField(max_length=255, blank=True)
    shipper = models.CharField(max_length=255, blank=True)
    consignee = models.CharField(max_length=255, blank=True)
    departure_country = models.CharField(max_length=255, blank=True)
    destination_country = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    sending_type = models.CharField(max_length=100, blank=True, choices=SENDING_TYPE_CHOICES)
    add_charges = models.FloatField(blank=True, default=0)
    container_type = models.CharField(max_length=255, blank=True)

    forwarder = models.ForeignKey('counterparty.Counterparty', on_delete=models.CASCADE, related_name='ru_applications')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='ru_applications')
    territories = models.ManyToManyField('core.Territory', related_name='ru_applications')

    class Meta:
        verbose_name = 'MoscowApplication'
        verbose_name_plural = 'MoscowApplications'
        db_table = 'interrail_ru_application'
        ordering = ['-id']

    def __str__(self):
        return self.number or str(self.id)


class InterrailRuCode(TimeStampedModel):
    CODE_STATUS_CHOICES = (
        ('Checking', 'Checking'),
        ('Used', 'Used'),
        ('Canceled', 'Canceled'),
        ('Completed', 'Completed'),
    )

    code_status = models.CharField(choices=CODE_STATUS_CHOICES, default='Checking', max_length=50)
    number = models.CharField(max_length=20, blank=True)
    smgs_code = models.CharField(max_length=20, blank=True)
    smgs_date = models.DateField(blank=True, null=True)
    weight = models.CharField(max_length=100, blank=True, default='')
    wagon_number = models.CharField(max_length=100, blank=True, default='')
    container_number = models.CharField(max_length=100, blank=True, default='')
    rate = models.FloatField(blank=True, default=0)
    add_charges = models.FloatField(blank=True, default=0)
    smgs_file = models.FileField(upload_to='applications/smgs_file/', blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    comment = models.TextField(blank=True, default='')

    application = models.ForeignKey('payment_codes.InterrailRuApplication', on_delete=models.CASCADE, related_name='ru_codes')
    territory = models.ForeignKey('core.Territory', null=True, on_delete=models.SET_NULL, related_name='ru_codes')

    class Meta:
        verbose_name = 'InterrailRuCode'
        verbose_name_plural = 'InterrailRuCodes'
        db_table = 'interrail_ru_code'

    def __str__(self):
        return self.number or str(self.id)
