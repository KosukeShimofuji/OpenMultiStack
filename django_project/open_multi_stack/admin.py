from open_multi_stack.models import Account
from django.contrib import admin

class AccountAdmin(admin.ModelAdmin):
    fields = ['provider', 'username', 'password', 'tenantname', 'tenant_id', 
            'auth_url', 'version', 'status']
    list_display = ('provider', 'username', 'tenantname', 'tenant_id')

admin.site.register(Account, AccountAdmin)


