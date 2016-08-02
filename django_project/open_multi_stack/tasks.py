from celery import task
from time import sleep
from datetime import datetime

@task

def create_openstack_instance(r):
    f = open("/tmp/test.txt", "a")
    f.writelines(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "execute create_openstack_instance\n")
    f.close()
    sleep(10)
    f = open("/tmp/test.txt", "a")
    f.writelines(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "finish create_openstack_instance\n")
    f.close()

