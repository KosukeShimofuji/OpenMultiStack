from django.db import models
from django.db.models.signals import post_save
from .reciver import post_save_queue_table
from datetime import datetime

# Create your models here.

class Account(models.Model):
    username   = models.CharField(max_length=128)
    tenantname = models.CharField(max_length=128)
    tenant_id  = models.CharField(max_length=128)
    password   = models.CharField(max_length=128)
    auth_url   = models.CharField(max_length=128)
    STATUS_AVAILABLE = "available"
    STATUS_UNAVAILABLE = "unavailable"
    STATUS_SET = (
            (STATUS_AVAILABLE, "available"),
            (STATUS_UNAVAILABLE, "unavailable"),
    )
    status = models.CharField(choices=STATUS_SET, default=STATUS_AVAILABLE, max_length=12)
    provider    = models.CharField(max_length=128)
    regist_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.tenantname + '_' + self.provider

class Instance(models.Model):
    name        = models.CharField(max_length=128)
    ip_addr     = models.CharField(max_length=128)
    username    = models.CharField(max_length=128)
    password    = models.CharField(max_length=128)
    key         = models.TextField(blank=True, null=False)
    regist_date = models.DateField(auto_now_add=True)
    account     = models.ForeignKey(Account)

    def __str__(self):
        return self.name + '_' + self.ip_addr 

class Queue(models.Model):
    regist_datetime = models.DateTimeField(auto_now_add=True)
    STATUS_QUEUEING = "queueing"
    STATUS_BOOTING  = "booting"
    STATUS_RUNNING  = "running"
    STATUS_DESTROYING  = "destroying"
    STATUS_FAILED   = "failed"
    STATUS_SET = (
            (STATUS_QUEUEING, "queueing"),
            (STATUS_BOOTING,  "booting"),
            (STATUS_RUNNING,  "running"),
            (STATUS_DESTROYING,  "destroying"),
            (STATUS_FAILED,   "failed"),
    )
    status = models.CharField(choices=STATUS_SET, default=STATUS_QUEUEING, max_length=12)
    instance = models.ForeignKey(Instance, null=True)

    def __str__(self):
        return self.regist_datetime.strftime('%Y-%m-%d %H:%M') + '_' + self.status
    
post_save.connect(post_save_queue_table, sender=Queue)

