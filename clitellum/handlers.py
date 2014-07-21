import new

__author__ = 'Sergio'


class HandlerManager:

    def __init__(self):
        self.__handlers = dict()

    def handler(self, key, **options):
        def decorator(f):
            # endpoint = options.pop('endpoint', None)
            self.add_handler(key, f, options)
            return f
        return decorator

    def add_handler(self, key, class_type, options):
        self.__handlers[key] = class_type

    def get_handler(self, key):
        return self.__handlers[key]()