from django.db import models

from users.models import CustomUser


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=False)
    modified = models.DateTimeField(auto_now=False)

    class Meta:
        abstract = True



class Territory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Territory"
        verbose_name_plural = "Territories"
        db_table = "territory"

    def __str__(self):
        return self.name


class Counterparty(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Counterparty"
        verbose_name_plural = "Counterparties"
        db_table = "counterparty"

    def __str__(self):
        return self.name


# Create your models here.
class Application(TimeStampedModel):
    CONTAINER_TYPE_CHOICES = (
        ("20", "20"),
        ("20HC", "20HC"),
        ("40", "40"),
        ("40HC", "40HC"),
        ("45", "45"),
    )

    LOADING_TYPE_CHOICES = (
        ("wagon", "Wagon"),
        ("container", "Container"),
    )
    SENDING_TYPE_CHOICES = (
        ("single", "Одиночный"),
        ("block_train", "КП"),
    )

    number = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
    )
    request_file = models.FileField(
        upload_to="interrail_russian/applications/", blank=True, null=True
    )
    sending_type = models.CharField(
        max_length=100, blank=True, choices=SENDING_TYPE_CHOICES
    )
    quantity = models.IntegerField(default=1)
    date = models.DateField(blank=True, null=True)
    territories = models.ManyToManyField(Territory, related_name="ru_applications")
    forwarder = models.ForeignKey(
        Counterparty, related_name="ru_applications", on_delete=models.CASCADE
    )
    paid_telegram = models.BooleanField(default=False)
    departure = models.TextField(blank=True)
    departure_code = models.TextField(blank=True)
    destination = models.TextField(blank=True)
    destination_code = models.TextField(blank=True)
    cargo = models.TextField(blank=True)
    hs_code = models.TextField(blank=True)
    etcng = models.TextField(blank=True)
    loading_type = models.CharField(
        max_length=100, choices=LOADING_TYPE_CHOICES, default=LOADING_TYPE_CHOICES[0][0]
    )
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    container_type = models.CharField(
        max_length=255, blank=True, choices=CONTAINER_TYPE_CHOICES, default=""
    )
    rolling_stock_1 = models.TextField(blank=True)
    rolling_stock_2 = models.TextField(blank=True)
    conditions_of_carriage = models.TextField(blank=True)
    agreed_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    add_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    border_crossing = models.TextField(blank=True)
    containers_or_wagons = models.TextField(default="")
    period = models.TextField(blank=True)
    shipper = models.TextField(blank=True)
    consignee = models.TextField(blank=True)
    departure_country = models.TextField(blank=True)
    destination_country = models.TextField(blank=True)
    manager = models.ForeignKey(
        CustomUser, related_name="applications", on_delete=models.SET_NULL, null=True
    )
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Application"
        verbose_name_plural = "Applications"
        db_table = "application"

    def __str__(self):
        return self.number


class PaymentCode(TimeStampedModel):
    CHECKING = "Checking"
    USED = "Used"
    CANCELED = "Canceled"
    COMPLETED = "Completed"
    CODE_STATUS_CHOICES = (
        ("Checking", "Checking"),
        ("Used", "Used"),
        ("Canceled", "Canceled"),
        ("Completed", "Completed"),
    )

    code_status = models.CharField(
        choices=CODE_STATUS_CHOICES, default=CODE_STATUS_CHOICES[0][0], max_length=50
    )
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="codes"
    )
    number = models.CharField(max_length=20, blank=True)
    territory = models.ForeignKey(
        Territory, related_name="codes", on_delete=models.SET_NULL, null=True
    )
    date = models.DateField(blank=True, null=True)
    smgs_code = models.CharField(max_length=20, blank=True)
    smgs_date = models.DateField(blank=True, null=True)
    weight = models.CharField(max_length=100, blank=True, default="")
    wagon_number = models.CharField(max_length=100, blank=True, default="")
    container_number = models.CharField(max_length=100, blank=True, default="")
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    add_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    smgs_file = models.FileField(
        upload_to="applications/smgs_file/", blank=True, null=True
    )
    comment = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "PaymentCode"
        verbose_name_plural = "PaymentCodes"
        db_table = "payment_code"

    def __str__(self):
        return self.number
