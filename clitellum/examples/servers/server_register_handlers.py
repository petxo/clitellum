from config import Config
from clitellum import server
from clitellum.handlers import HandlerBase

__author__ = 'Sergio'

cfg = Config('server.cfg')
srv = server.create_server_from_config(cfg)


@srv.handler_manager.handler('mi_mensaje')
class MiHandler(HandlerBase):

    def __init__(self):
        HandlerBase.__init__(self)


srv.start()

kk = srv.handler_manager.get_handler('mi_mensaje')


del kk

srv.stop()