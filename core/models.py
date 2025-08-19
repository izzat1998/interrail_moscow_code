from django.db import models


class Territory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Territory'
        verbose_name_plural = 'Territories'
        db_table = 'territory'

    def __str__(self):
        return self.name