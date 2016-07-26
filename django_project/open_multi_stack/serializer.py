from rest_framework import serializers
from .models import Queue

class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = ('id', 'op', 'status', 'regist_datetime')
        read_only_fields = ('status',)

