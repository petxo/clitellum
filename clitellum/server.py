from clitellum import processors
from clitellum.core.fsm import Startable
from clitellum.handlers import HandlerManager

__author__ = 'sergio'


## Crea un server desde un config
def create_server_from_config(cfg):
    identification = Identification(cfg['identification']['id'], cfg['identification']['type'])
    ag = processors.create_agent_from_config(identification, cfg["agent"])
    control = processors.create_agent_from_config(identification, cfg["controller"])
    return Server(identification, ag, control)


## Clase que contiene la informacion de identificacion de un proceso
class Identification:

    def __init__(self, id_service, type_service):
        self._id = id_service
        self._type = type_service

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type


class Server(Startable):

    def __init__(self, identification, agent, controller):
        Startable.__init__(self)
        self.identification = identification
        self.handler_manager = HandlerManager()
        self._agent = agent
        self._agent.configure(self.handler_manager)
        self._controller = controller

    def _invokeOnStart(self):
        Startable._invokeOnStart(self)
        self._agent.start()
        self._controller.start()

    def _invokeOnStopped(self):
        Startable._invokeOnStopped(self)
        self._agent.stop()
        self._controller.stop()

    def __del__(self):
        Startable.__del__(self)


