from django.db import models

# Create your models here.

class Account(models.Model):
    username   = models.CharField(max_length=128)
    tenantname = models.CharField(max_length=128)
    tenant_id  = models.CharField(max_length=128)
    password   = models.CharField(max_length=128)
    auth_url   = models.CharField(max_length=128)
    version    = models.CharField(max_length=128)
    STATUS_AVAILABLE = "available"
    STATUS_UNAVAILABLE = "unavailable"
    STATUS_SET = (
            (STATUS_AVAILABLE, "使用可能"),
            (STATUS_UNAVAILABLE, "使用不可"),
    )
    status = models.CharField(choices=STATUS_SET, default=STATUS_AVAILABLE, max_length=12)
    provider    = models.CharField(max_length=128)

