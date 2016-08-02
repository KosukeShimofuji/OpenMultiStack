from celery import task
from time import sleep
from datetime import datetime

@task

def create_openstack_instance(queue_id):
    f = open("/tmp/test.txt", "a")
    f.writelines(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' ' + str(queue_id) + "\n")
    f.close()


