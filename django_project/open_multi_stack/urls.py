from rest_framework import routers
from .views import QueueViewSet

router = routers.DefaultRouter()
router.register(r'queues', QueueViewSet)

