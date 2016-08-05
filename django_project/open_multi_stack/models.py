from django.db import models
from django.db.models.signals import post_save, post_delete
from .reciver import post_save_queue_table, pre_delete_queue_table
from datetime import datetime

class Account(models.Model):
    username      = models.CharField(max_length=128)
    password      = models.CharField(max_length=128)
    auth_url      = models.CharField(max_length=128)
    tenant_name   = models.CharField(max_length=128)
    tenant_id     = models.CharField(max_length=128)
    region_name   = models.CharField(max_length=128)
    version       = models.CharField(max_length=128)
    STATUS_AVAILABLE = "available"
    STATUS_UNAVAILABLE = "unavailable"
    STATUS_SET = (
            (STATUS_AVAILABLE, "available"),
            (STATUS_UNAVAILABLE, "unavailable"),
    )
    status        = models.CharField(choices=STATUS_SET, default=STATUS_AVAILABLE, max_length=12)
    provider      = models.CharField(max_length=128)
    regist_date   = models.DateField(auto_now_add=True)

    def __str__(self):
        return  self.provider + '_' + self.region_name + '_' + self.tenant_name 

class Instance(models.Model):
    name        = models.CharField(max_length=128)
    ip_addr     = models.CharField(max_length=128)
    key_name    = models.CharField(max_length=128)
    key_raw     = models.TextField(blank=True, null=False)
    regist_datetime = models.DateTimeField(auto_now_add=True)
    account     = models.ForeignKey(Account)

    def __str__(self):
        return self.name + '_' + self.ip_addr 

class Queue(models.Model):
    regist_datetime = models.DateTimeField(auto_now_add=True)
    STATUS_REQUEST  = "REQUEST"
    STATUS_RECIVE   = "RECIVE"
    STATUS_BOOT     = "BOOT"
    STATUS_RUN      = "RUN"
    STATUS_DESTROY  = "DESTROY"
    STATUS_FAILED   = "FAILED"
    STATUS_SET = (
            (STATUS_REQUEST,  "REQUEST"),
            (STATUS_RECIVE,   "RECIVE"),
            (STATUS_BOOT,     "BOOT"),
            (STATUS_RUN,      "RUN"),
            (STATUS_DESTROY,  "DESTROY"),
            (STATUS_FAILED,   "FAILED"),
    )
    status = models.CharField(choices=STATUS_SET, default=STATUS_REQUEST, max_length=12)
    instance = models.ForeignKey(Instance, null=True)

    def __str__(self):
        return self.regist_datetime.strftime('%Y-%m-%d %H:%M') + '_' + self.status
    
post_save.connect(post_save_queue_table, sender=Queue)
pre_delete.connect(post_delete_queue_table, sender=Queue)

