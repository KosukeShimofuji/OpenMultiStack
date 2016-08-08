from open_multi_stack.models import Account, Instance, Queue
from django.contrib import admin

class AccountAdmin(admin.ModelAdmin):
    fields = ['provider', 'username', 'password', 'tenant_name', 'tenant_id',
            'auth_url', 'region_name', 'version', 'status']
    list_display = ('provider', 'username', 'region_name', 'tenant_name', 'tenant_id')

class InstanceAdmin(admin.ModelAdmin):
    fields = ['account', 'name', 'ip_addr', 'key_name', 'key_raw']
    list_display = ('account', 'name', 'ip_addr', 'regist_datetime')

class QueueAdmin(admin.ModelAdmin):
    fields = ['status', 'instance']
    list_display = ('status', 'instance', 'regist_datetime')

admin.site.register(Account,  AccountAdmin)
admin.site.register(Instance, InstanceAdmin)
admin.site.register(Queue,    QueueAdmin)

