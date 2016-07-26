import django_filters
from rest_framework import viewsets, filters
from .models import Queue
from .serializer import QueueSerializer

class QueueViewSet(viewsets.ModelViewSet):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer

