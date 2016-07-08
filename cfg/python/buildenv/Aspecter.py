import re

class Aspecter(type):
    aspect_rules = []
    wrapped_methods = []
    def __new__(cls, name, bases, dict):
        for key, value in dict.items():
            if hasattr(value, "__call__") and key != "__metaclass__":
                dict[key] = Aspecter.wrap_method(value)
        return type.__new__(cls, name, bases, dict)

    @classmethod
    def register(cls, name_pattern="", in_objects=(), out_objects=(), pre_function=None, post_function=None):
        rule = {"name_pattern": name_pattern, "in_objects": in_objects, "out_objects": out_objects, "pre": pre_function, "post":post_function}
        cls.aspect_rules.append(rule)

    @classmethod
    def wrap_method(cls, method):
        def call(*args, **kw):
            pre_functions = cls.matching_pre_functions(method, args, kw)
            for function in pre_functions:
                function(method, *args, **kw)
            results = method(*args, **kw)
            post_functions = cls.matching_post_functions(method, results)
            for function in post_functions:
                function(results, *args, **kw)
            return results
        return call

    @classmethod
    def matching_names(cls, method):
        return [rule for rule in cls.aspect_rules if re.match(rule["name_pattern"],method.func_name) or rule["name_pattern"] == ""]

    @classmethod
    def matching_pre_functions(cls, method, args, kw):
        all_args = args + tuple(kw.values())
        return [rule["pre"] for rule in cls.matching_names(method) if rule["pre"] and (rule["in_objects"] == () or any((type(arg) in rule["in_objects"] for arg in all_args)))]

    @classmethod
    def matching_post_functions(cls, method, results):
        if type(results) != tuple:
            results = (results,)
        return [rule["post"] for rule in cls.matching_names(method) if rule["post"] and (rule["out_objects"] == () or any((type(result) in rule["out_objects"] for result in results)))]

