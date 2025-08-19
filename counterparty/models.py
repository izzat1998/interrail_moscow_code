from django.db import models


class Counterparty(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Counterparty'
        verbose_name_plural = 'Counterparties'
        db_table = 'counterparty'

    def __str__(self):
        return self.name