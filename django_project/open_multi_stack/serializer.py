from rest_framework import serializers
from .models import Queue

class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = ('id', 'status', 'regist_datetime', 'instance')
        read_only_fields = ('status','instance')

