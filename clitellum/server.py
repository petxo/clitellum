from clitellum import processors
from clitellum.core.fsm import Startable
from clitellum.handlers import HandlerManager

__author__ = 'sergio'


## Crea un server desde un config
def create_server_from_config(name, cfg):
    ag = processors.create_agent_from_config(cfg["agent"])
    control = processors.create_agent_from_config(cfg["controller"])
    return Server(name, ag, control)


class Server(Startable):

    def __init__(self, name, agent, controller):
        Startable.__init__(self)
        self.name = name
        self.handler_manager = HandlerManager()
        self._agent = agent
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


