from datetime import datetime
from time import sleep
from open_multi_stack.tasks import create_openstack_instance

def post_save_queue_table(sender, instance, **kwargs):
    f = open("/tmp/test.txt", "a")
    f.writelines(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "prepare_execute_task\n")
    f.close()

    create_openstack_instance.delay(instance.id)

    f = open("/tmp/test.txt", "a")
    f.writelines(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "after_execute_task\n")
    f.close()


