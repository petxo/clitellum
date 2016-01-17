from clitellum.core import serialization
from clitellum.core.bus import MessageBus
from clitellum.core.fsm import Startable
from clitellum.core.messageparser import MessageParser
from clitellum.endpoints import gateways

__author__ = 'Sergio'

## @package clitellum.processors
#  Este paquete contiene las clases que encapsulan la relacion del los mensajes con sus manejadores


## Crea un agente desde la configuracion
# Ej:
# {
#   input_gateway : ...
#   output_gateway : ...
# }
def create_agent_from_config(identification, cfg):
    # Creamos el receiver gateway
    rg = gateways.CreateReceiverFromConfig(cfg["receiver_gateway"])
    sg = gateways.CreateSenderFromConfig(cfg["sender_gateway"])
    return AgentProcessor(identification, rg, sg)

## Clase que representa la interfaz para poder comunicar con el BUS
class Bus:

    def __init__(self):
        pass

    @property
    def identification(self):
        return None

    def send(self, message, key):
        pass


## Clase que implementa el procesamiento de los mensajes
class AgentProcessor(Startable, Bus):

    def __init__(self, identification, receiver_gateway, sender_gateway):
        Startable.__init__(self)
        Bus.__init__(self)
        self._receiver_gateway = receiver_gateway
        self._senderGateway = sender_gateway
        self._identification = identification
        self._receiver_gateway.OnMessageReceived += self.__on_message_received
        self._handler_manager = None

    @property
    def identification(self):
        return self._identification

    def configure(self, handler_manager):
        self._handler_manager = handler_manager

    def __on_message_received(self, sender, args):
        message_bus = serialization.loads(args.message)
        context = message_bus['Header']['CallContext']

        handler = self._handler_manager.get_handler(message_bus['Header']['BodyType'])
        handler.initialize(self, context)

        body_message = serialization.loads(message_bus['Body'])
        handler.handle_message(message_bus['Body'])
        pass

    def _invokeOnStart(self):
        Startable._invokeOnStart(self)
        self._receiver_gateway.start()
        self._senderGateway.connect()

    def _invokeOnStopped(self):
        Startable._invokeOnStopped(self)
        self._receiver_gateway.stop()
        self._senderGateway.close()

    def send(self, message, key):
        message_bus = MessageBus.create(message, key, self.identification.id, self.identification.type)
        message_str = serialization.dumps(message_bus)
        self._senderGateway.send(message_str)

    def __del__(self):
        Startable.__del__(self)