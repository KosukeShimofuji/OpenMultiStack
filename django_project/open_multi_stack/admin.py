from django.contrib import admin

from .models import OpenStackAccount

@admin.register(OpenStackAccount)
class OpenStackAccount(admin.ModelAdmin):
    pass

