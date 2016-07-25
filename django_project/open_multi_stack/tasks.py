import time

from celery import task

@task
def add(a, b):
    time.sleep(10)
    return a + b

