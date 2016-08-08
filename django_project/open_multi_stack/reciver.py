from datetime import datetime
from time import sleep
from open_multi_stack.tasks import create_openstack_instance, delete_openstack_instance

def post_save_queue_table(sender, instance, **kwargs):
    create_openstack_instance.delay(instance)

def pre_delete_queue_table(sender, instance, **kwargs):
    delete_openstack_instance.delay(instance)

