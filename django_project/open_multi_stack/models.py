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
            (STATUS_AVAILABLE, "available"),
            (STATUS_UNAVAILABLE, "unavailable"),
    )
    status = models.CharField(choices=STATUS_SET, default=STATUS_AVAILABLE, max_length=12)
    provider    = models.CharField(max_length=128)

    def __str__(self):
        return self.tenantname + '_' + self.provider

class Instance(models.Model):
    name    = models.CharField(max_length=128)
    ip      = models.CharField(max_length=128)
    key     = models.CharField(max_length=128)
    account = models.ForeignKey(Account)

    def __str__(self):
        return self.name + '_' + self.ip + '_' + self.account

