from celery import task
from time import sleep
from datetime import datetime

@task

def create_openstack_instance(queue_id):
    from open_multi_stack.models import Queue
    f = open("/tmp/test.txt", "a")
    f.writelines(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' ' + str(queue_id) + "\n")
    f.writelines(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' ' + str(Queue(queue_id)) + "\n")
    f.close()


