import yaml
import logging
import logging.config
from clitellum import server
from config import Config
from clitellum.handlers import HandlerBase

logcfg = yaml.load(open('logging.yml', 'r'))
logging.config.dictConfig(logcfg)

cfg = Config('server.cfg')
srv = server.create_server_from_config(cfg)


@srv.handler_manager.handler('Saludos.MensajeSaludo')
class MensajeSaludoHandler(HandlerBase):
    def __init__(self):
        HandlerBase.__init__(self)

    def handle_message(self, message):
        print '\n' + message['Mensaje']
        k = 1 / 0


srv.start()
raw_input('Pulsa Enter para finalizar')

srv.stop()
