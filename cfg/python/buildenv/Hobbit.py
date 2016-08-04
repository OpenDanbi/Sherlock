import Aspecter

def log_entry(method, *args, **kw):
    list_desc = method.replace(' ','')

    print("[entry] %s" % method)
    print(list_desc)

def log_exit(result, *args, **kw):
    print("[exit] %s" % result)

class Hobbit(object):
    __metaclass__ = Aspecter.Aspecter

    name = None
    def __init__(self,name):
        self.name = name

    def walk(self):
        print("%s walks" % self.name)

    def run(self):
        print("%s runs" % self.name)

    def command(self, cmdType, receiver):
        if 'walk' == cmdType:
            receiver.walk()
        elif 'run' == cmdType:
            receiver.run()

Aspecter.Aspecter.register(name_pattern="^.*", pre_function=log_entry, post_function=log_exit)

