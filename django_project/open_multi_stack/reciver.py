from datetime import datetime

def test(sender, instance, **kwargs):
    f = open("/tmp/test.txt", "a")
    f.writelines("test " + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "\n")
    f.close()

