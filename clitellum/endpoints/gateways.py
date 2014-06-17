# coding=utf-8
import threading

from clitellum.core import queue, loadbalancers
from clitellum.core.eventhandling import EventHook
from clitellum.core.fsm import Startable
from clitellum.endpoints.channels import factories
from clitellum.endpoints.channels.events import MessageReceivedArgs


__author__ = 'sergio'


class BaseGateway(Startable):
    ## Crea una instancia de BasicGateway
    # @param channel Canal de comunicacion utilizado por el gateway
    def __init__(self, channels=list()):
        Startable.__init__(self)
        self._channels = list()
        self.OnConnectionError = EventHook()
        for channel in channels:
            self.addChannel(channel)

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

    def _process(self):
        pass

    def _invokeOnStart(self):
        Startable._invokeOnStart(self)
        for ch in self._channels:
            ch.start()

    def _invokeOnStopped(self):
        Startable._invokeOnStopped(self)
        for ch in self._channels:
            ch.stop()

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
#   router : { type: "RoundRobin" }
# }
def CreateSenderFromConfig(config):
    channels = list()
    for ch in config["channels"]:
        if not ch.get('number') is None:
            for index in range(0, ch['number']):
                channel = factories.CreateOutBoundChannelFromConfig(ch)
                channels.append(channel)
        else:
            channel = factories.CreateOutBoundChannelFromConfig(ch)
            channels.append(channel)

    router = loadbalancers.CreateRouterFromConfig(config.get("balancer"))

    return SenderGateway(router, channels)


## Clase que implementa un gateway de salida
class SenderGateway(BaseGateway):
    def __init__(self, loadBalancer, channels=list()):
        self._loadBalancer = loadBalancer
        BaseGateway.__init__(self, channels)

    # TODO: añadir la informacion de enrutamiento, y añadir el canal al router
    def addChannel(self, outBoundChannel):
        BaseGateway.addChannel(self, outBoundChannel)
        self._loadBalancer.addChannel(outBoundChannel)
        outBoundChannel.OnSendError += self._errorSending
        outBoundChannel.OnMessageSent += self._onMessageSent

    def send(self, message):
        outBoundChannel = self._loadBalancer.next()
        outBoundChannel.send(message)

    def _errorSending(self, sender, args):
        # TODO: Tratamiento de los mensajes y lanzar un evento
        pass

    def _onMessageSent(self, sender, args):
        # TODO: Lanzar un evento
        pass


## Crea un SenderGateway desde un config
# { channels : [
#               { type : 0Mq, timer : Logarithmic, host : tcp://server:8080, maxReconnections : 20 }
#               { type : tcp, timer : Logarithmic, host : tcp://server:8082, maxReconnections : 20 }
#               { type : 0Mq, timer : Logarithmic, host : tcp://server:8083, maxReconnections : 20 }
#               ],
#   numExtractors: 4
# }
def CreateReceiverFromConfig(config):
    channels = list()
    for ch in config["channels"]:
        if not ch.get('number') is None:
            for index in range(0, ch['number']):
                channel = factories.CreateInBoundChannelFromConfig(ch)
                channels.append(channel)
        else:
            channel = factories.CreateInBoundChannelFromConfig(ch)
            channels.append(channel)

    if not config.get('numThreads') is None:
        return ReceiverGateway(channels, config['numThreads'])
    else:
        return ReceiverGateway(channels)


## Clase que implementa un gateway de entrada
class ReceiverGateway(BaseGateway):
    def __init__(self, channels=list(), numThreads=4):
        BaseGateway.__init__(self, channels)
        self.OnMessageReceived = EventHook()
        self._semaphore = threading.Semaphore(numThreads)

    def addChannel(self, channel):
        BaseGateway.addChannel(self, channel)
        channel.OnMessageReceived += self._messageReceivedChannel

    def _messageReceivedChannel(self, sender, args):
        self._semaphore.acquire()
        threading.Thread(target=self._invokeOnReceivedMessage, kwargs={"message": args.message}).start()

    def __del__(self):
        BaseGateway.__del__(self)
        self.OnMessageReceived.clear()

    def _invokeOnReceivedMessage(self, message):
        args = MessageReceivedArgs(message=message)
        self.OnMessageReceived.fire(self, args)
        self._semaphore.release()