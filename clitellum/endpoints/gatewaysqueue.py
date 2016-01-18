# coding=utf-8
## @package clitellum.endpoints.gateways
#  Este paquete contiene las clases que encapsulan el acceso al sistema de mensajeria con el
# resto de la aplicacion
# Estos gateways contienen amortiguadores, el SenderGateway, antes de enviar un mensaje al sistema
# de mensajeria, lo almacena en una cola en base de datos o bien en fichero. Y el Receiver Gateway
# cuando recibe del sistema de mensajeria, antes de procesarlo, lo almacena en un cola.
# Este tipo de gateways son utiles en la comunicaciones entre los sistemas de mensajeria y sistemas externos.

import threading

from clitellum.core import queue, loadbalancers
from clitellum.core.eventhandling import EventHook
from clitellum.core.fsm import Startable
from clitellum.endpoints.channels import factories
from clitellum.endpoints.channels.events import MessageReceivedArgs


__author__ = 'sergio'


## Clase que expone los metodos basicos para la encapsulacion del sistema de mensajeria
class BaseGatewayQueue(Startable):

    ## Crea una instancia de BasicGateway
    # @param channel Canal de comunicacion utilizado por el gateway
    def __init__(self, queue, channels=list(), numExtractors=4):
        Startable.__init__(self)
        self._channels = list()
        self._queue = queue
        self.OnConnectionError = EventHook()
        for channel in channels:
            self.addChannel(channel)

        self._thExtractors = list()
        for count in range(0, numExtractors):
            self._thExtractors.append(threading.Thread(target=self._process_queue))

    ## Añade un nuevo canal al gateway
    def addChannel(self, channel):
        self._channels.append(channel)
        channel.OnConnectionError += self._invokeOnConnectionError

    ## Realiza la conexion del canal
    def connect(self):
        for channel in self._channels:
            channel.connect()

    ## Cierra la conexion del canal
    def close(self):
        for channel in self._channels:
            channel.close()

    ## Indica si el canal esta o no conectado
    @property
    def is_connected(self):
        for channel in self._channels:
            if channel.is_connected():
                return True

        return False

    def _invokeOnConnectionError(self, sender, args):
        #TODO: Es un error de conexion del canal que hay que tratar ademas de disparar
        self.OnConnectionError.fire(self, args)

    def _process_queue(self):
        pass

    def _invokeOnStart(self):
        Startable._invokeOnStart(self)
        for th in self._thExtractors:
            th.start()

    def _invokeOnStopped(self):
        Startable._invokeOnStopped(self)
        for th in self._thExtractors:
            th.join()

    def __del__(self):
        Startable.__del__(self)
        for channel in self._channels:
            del channel

        self.OnConnectionError.clear()


## Crea un SenderGateway desde un config
# { channels : [
#               { type : 0Mq, timer : Logarithmic, host : tcp://server:8080, maxReconnections : 20 }
#               { type : tcp, timer : Logarithmic, host : tcp://server:8082, maxReconnections : 20 }
#               { type : 0Mq, timer : Logarithmic, host : tcp://server:8083, maxReconnections : 20 }
#               ],
#   router : { type: "RoundRobin" },
#   queue : { type : "Berkeley",  path: "./data/queue.db" }
# }
def CreateSenderFromConfig(config):
    channels = list()
    for ch in config["channels"]:
        channel = factories.CreateOutBoundChannelFromConfig(ch)
        channels.append(channel)

    router = loadbalancers.CreateRouterFromConfig(config.get("balancer"))
    cola = queue.CreateQueueFromConfig(config["queue"])

    return SenderGatewayQueue(router, cola, channels)

## Clase que implementa un gateway de salida
class SenderGatewayQueue (BaseGatewayQueue):
    def __init__(self, loadBalancer, queue, channels=list(), numExtractors=4):
        self._loadBalancer = loadBalancer
        BaseGatewayQueue.__init__(self, queue, channels, numExtractors)

    # TODO: añadir la informacion de enrutamiento, y añadir el canal al router
    def addChannel(self, outBoundChannel):
        BaseGatewayQueue.addChannel(self, outBoundChannel)
        self._loadBalancer.addChannel(outBoundChannel)
        outBoundChannel.OnSendError += self._errorSending
        outBoundChannel.OnMessageSent += self._onMessageSent

    def send(self, message, key):
        self._queue.append([key, message])

    def _process_queue(self):
        while self.state == Startable.RUNNING:
#           TODO: controlar cuando no se puede enviar por uno o por ninguno de los channels
            try:
                item = self._queue.popleft(timeout=10)
                if not item is None:
                    outBoundChannel = self._loadBalancer.next()
                    outBoundChannel.send(item)
                del item
            except Exception:
                pass

    def _errorSending(self, sender, args):
        # Reencolamos el mensaje
        self._queue.task_not_done()

    def _onMessageSent(self, sender, args):
        #Eliminamos el mensaje de la cola definitivamente
        self._queue.task_done()

## Crea un SenderGateway desde un config
# { channels : [
#               { type : 0Mq, timer : Logarithmic, host : tcp://server:8080, maxReconnections : 20 }
#               { type : tcp, timer : Logarithmic, host : tcp://server:8082, maxReconnections : 20 }
#               { type : 0Mq, timer : Logarithmic, host : tcp://server:8083, maxReconnections : 20 }
#               ],
#   numExtractors: 4,
#   queue : { type : "Berkeley",  path: "./data/queue.db" }
# }
def CreateReceiverFromConfig(config):
    channels = list()
    for ch in config["channels"]:
        channel = factories.CreateOutBoundChannelFromConfig(ch)
        channels.append(channel)

    cola = queue.CreateQueueFromConfig(config["queue"])

    return ReceiverGatewayQueue(cola, channels, config['numExtractors'])


## Clase que implementa un gateway de entrada
class ReceiverGatewayQueue(BaseGatewayQueue):

    def __init__(self, queue, channels=list(), numExtractors=4):
        BaseGatewayQueue.__init__(self, queue, channels, numExtractors)
        self.OnMessageReceived = EventHook()

    def addChannel(self, channel):
        BaseGatewayQueue.addChannel(self, channel)
        channel.OnMessageReceived += self._messageReceivedChannel

    def _process_queue(self):
        while self.state == Startable.RUNNING:
            item = self._queue.popleft(timeout=10)
            if not item is None:
                #TODO: Crear los hilos del demonio con el control de errores
                pass

    def _messageReceivedChannel(self, sender, args):
        self._queue.append(args.message)

    def __del__(self):
        BaseGatewayQueue.__del__(self)
        self.OnMessageReceived.clear()

    def _invokeOnReceivedMessage(self, message):
        args = MessageReceivedArgs(message= message)
        self.OnMessageReceived.fire(self, args)
