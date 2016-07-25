from open_multi_stack.models import Account, Instance
from django.contrib import admin

class AccountAdmin(admin.ModelAdmin):
    fields = ['provider', 'username', 'password', 'tenantname', 'tenant_id', 'auth_url', 'status']
    list_display = ('provider', 'username', 'tenantname', 'tenant_id')

class InstanceAdmin(admin.ModelAdmin):
    fields = ['account', 'name', 'ip_addr', 'username', 'password', 'key']
    list_display = ('account', 'name', 'ip_addr')

admin.site.register(Account, AccountAdmin)
admin.site.register(Instance)

