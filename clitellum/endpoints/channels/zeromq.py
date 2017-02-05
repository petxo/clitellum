## @package pylightesb.endpoints.channels.zeromq
#  Este paquete contiene las clases para la comunicacion de tipo zeromq
import zmq
from clitellum.endpoints.channels.basechannels import *


## Clase que establece una conexion de salida de tipo ZeroMq con el host
class OutBoundChannelZeroMq(OutBoundChannel):

    ## Crea una instancia de OutBoundChannelZeroMq
    # @param reconnectionTimer Temporizador de reconexion
    # @param maxReconnections Numero maximo de reconexiones
    # @param host Nombre del host
    def __init__(self, host="", reconnectionTimer=reconnectiontimers.CreateLogarithmicTimer(),
                 maxReconnections=Channel.MAX_RECONNECTIONS, compressor = compressors.DefaultCompressor()):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUSH)
#        self._socket.setsockopt(28, 10)

        OutBoundChannel.__init__(self, host, reconnectionTimer, maxReconnections,  compressor = compressor)

    def _connect_point(self):
        self._socket.connect(self._host)

    def _close_point(self):
        self._socket.close()
        self._context.destroy()

    def _send(self, message, routingKey=''):
        self._socket.send(message)


## Clase que establece una conexion de entrada de tipo ZeroMq con el host
class InBoundChannelZeroMq(InBoundChannel):
    ## Crea una instancia de InBoundChannelZeroMq
    # @param reconnectionTimer Temporizador de reconexion
    # @param maxReconnections Numero maximo de reconexiones
    # @param host Nombre del host
    # @param receptionTimeout Timeout de recepcion de mensaje en milisegudos por defecto 20000
    def __init__(self, host="", reconnectionTimer=reconnectiontimers.CreateLogarithmicTimer(),
                 maxReconnections=Channel.MAX_RECONNECTIONS, receptionTimeout = 20000,  compressor = compressors.DefaultCompressor()):
        InBoundChannel.__init__(self, host, reconnectionTimer, maxReconnections, compressor = compressor)
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PULL)
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)
        self._receptionTimeout = receptionTimeout

    def _connect_point(self):
        self._socket.bind(self._host)

    def _close_point(self):
        self._poller.unregister(self._socket)
        self._socket.close()
        self._context.destroy()

    def _startReceive(self):
        evts = self._poller.poll(self._receptionTimeout)
        if len(evts) > 0:
            message = self._socket.recv()
            self._processMessage(message, self._socket)
            del message
