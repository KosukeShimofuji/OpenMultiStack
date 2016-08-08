from rest_framework import serializers
from .models import Queue, Instance, Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('provider', 'region_name', 'tenant_name')
        read_only_fields = ('provider', 'region_name', 'tenant_name')

class InstanceSerializer(serializers.ModelSerializer):
    account = AccountSerializer()

    class Meta:
        model = Instance
        fields = ('id', 'name', 'instance_id', 'ip_addr', 'key_name', 'key_raw', 'account')
        read_only_fields = ('id', 'name', 'instance_id', 'ip_addr', 'key_name', 'key_raw', 'account')

class QueueSerializer(serializers.ModelSerializer):
    instance = InstanceSerializer(required=False)

    class Meta:
        model = Queue
        fields = ('id', 'status', 'regist_datetime', 'instance')
        read_only_fields = ('status','instance')

