from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default=None, null=True)

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        db_table = 'role'

    def __str__(self):
        return self.name


class Page(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        db_table = 'page'

    def __str__(self):
        return self.name


class VerificationCode(models.Model):
    code = models.CharField(max_length=6)
    telegram_id = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Verification Code'
        verbose_name_plural = 'Verification Codes'
        db_table = 'verification_code'

    def __str__(self):
        return f"{self.telegram_id} - {self.code}"


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('client', 'Client'),
        ('counterparty', 'Counterparty'),
    )

    # Fields that actually exist in the production database
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    profile_icon = models.CharField(max_length=50, blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    telegram_access = models.BooleanField(default=False)
    subscribed_to_email = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='client')
    telegram_username = models.CharField(max_length=100, blank=True, null=True)
    
    company = models.ForeignKey('customer.Company', on_delete=models.CASCADE, related_name='company_users', blank=True, null=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'user'

    def __str__(self):
        return self.username


# Keep the old name for backward compatibility
CustomUser = User
