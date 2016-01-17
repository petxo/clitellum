__author__ = 'Sergio'

from clitellum import server
from config import Config
from clitellum.handlers import HandlerBase
import yaml
import logging
import logging.config

logcfg = yaml.load(open('logging.yml', 'r'))
logging.config.dictConfig(logcfg)

cfg = Config('server.cfg')
srv = server.create_server_from_config(cfg)


@srv.handler_manager.handler('MensajeSaludo')
class MensajeSaludoHandler(HandlerBase):

    def __init__(self):
        HandlerBase.__init__(self)

    def handle_message(self, message):
        print message

srv.start()
input('Pulsa Enter para finalizar')

srv.stop()