from config import Config
from clitellum import server

__author__ = 'Sergio'

cfg = Config('server.cfg')
srv = server.create_server_from_config('TestServer', cfg)


@srv.handler_manager.handler('mi_mensaje')
class MiHandler:

    def __init__(self):
        pass


srv.start()

kk = srv.handler_manager.get_handler('mi_mensaje')


del kk

srv.stop()