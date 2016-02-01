from clitellum.endpoints.channels.factories import CustomFactoryBase


class MyOutBound:
    def __init__(self):
        pass


class MyOutBoundFactory(CustomFactoryBase):
    def __init__(self):
        CustomFactoryBase.__init__(self)

    def create_from_cfg(self, cfg):
        return MyOutBound()
