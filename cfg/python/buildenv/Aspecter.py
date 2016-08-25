import re

class Aspecter(type):
    aspect_rules = []
    def __new__(cls, name, bases, dict):
        for key, value in dict.items():
            if hasattr(value, "__call__") and key != "__metaclass__":
                dict[key] = Aspecter.wrap_method(value)
        return type.__new__(cls, name, bases, dict)

    @classmethod
    def register(cls, name_pattern="", in_objects=(), out_objects=()):
        rule = {"name_pattern": name_pattern, "in_objects": in_objects, "out_objects": out_objects}
        cls.aspect_rules.append(rule)

    @classmethod
    def wrap_method(cls, method):
        def call(*args, **kw):
            print("[entry] %s" % method)
            results = method(*args, **kw)
            print("[exit] %s" % method)
            return results
        return call

