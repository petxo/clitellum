from clitellum.core.fsm import Startable
from clitellum.endpoints import gateways

__author__ = 'Sergio'


## Crea un agente desde la configuracion
# Ej:
# {
#   input_gateway : ...
#   output_gateway : ...
# }
def create_agent_from_config(cfg):
    # Creamos el receiver gateway
    rg = gateways.CreateReceiverFromConfig(cfg["receiver_gateway"])
    sg = gateways.CreateSenderFromConfig(cfg["sender_gateway"])
    return AgentProcessor(rg, sg)


## @package clitellum.processors
#  Este paquete contiene las clases que encapsulan la relacion del los mensajes con sus manejadores

## Clase que implementa el procesamiento de los mensajes
class AgentProcessor(Startable):

    def __init__(self, receiver_gateway, sender_gateway):
        Startable.__init__(self)
        self._receiver_gateway = receiver_gateway
        self._senderGateway = sender_gateway
        self._receiver_gateway.OnMessageReceived += self.__on_message_received

    def __on_message_received(sender, args):
        pass

    def _invokeOnStart(self):
        Startable._invokeOnStart(self)
        self._receiver_gateway.start()
        self._senderGateway.connect()

    def _invokeOnStopped(self):
        Startable._invokeOnStopped(self)
        self._receiver_gateway.stop()
        self._senderGateway.close()

    def __del__(self):
        Startable.__del__(self)