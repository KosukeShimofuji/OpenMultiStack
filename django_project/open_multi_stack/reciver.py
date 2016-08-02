from datetime import datetime
from time import sleep

def test(sender, instance, **kwargs):
    f = open("/tmp/test.txt", "a")
    f.writelines("test " + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' ' + str(instance.id) + "\n")
    f.writelines("start signal reciver\n")
    sleep(10)
    f.writelines("end signal reciver\n")
    f.close()


