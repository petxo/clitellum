import re
import socket
import threading

import amqp

from clitellum.core import compressors, loggerManager
from clitellum.endpoints.channels import reconnectiontimers
from clitellum.endpoints.channels.basechannels import OutBoundChannel, Channel, InBoundChannel
from clitellum.endpoints.channels.exceptions import ConnectionError, SendError


__author__ = 'sergio'


## Clase base de un canal amqp
class BaseAmqpChannel:

    ## Crea una intancia de BaseAmqpChannel
    def __init__(self, host, user='guest', password='guest'):
        match = re.search('^amqp://(.*):(\d+)/(.*)/(.*)/(.*)', host)
        if match:
            self._server = match.group(1)
            self._port = int(match.group(2))
            self._exchange = match.group(3)
            self._queue = match.group(4)
            self._key = match.group(5)
            self._user = user
            self._password = password
            self._connection = None
        else:
            raise NameError("Invalid host name", host)

    def _connect_point(self):
        try:
            if not self._connection is None and self._connection.connected:
                self._connection.close()

            self._connection = amqp.Connection(host=self._server, heartbeat=60, userid=self._user,
                                               password=self._password)
            self._channel = self._connection.channel()

            self._channel.exchange_declare(exchange=self._exchange, durable=True, type='direct', auto_delete=False)
            self._channel.queue_declare(queue=self._queue, durable=True, auto_delete=False)
            self._channel.queue_bind(queue=self._queue, exchange=self._exchange, routing_key=self._key)

        except Exception as ex:
            raise ConnectionError(ex)

    def _close_point(self):
        if self._connection.connected:
            self._connection.close()


## Clase que implementa un canal de salida con el protocolo amqp
class OutBoundAmqpChannel(OutBoundChannel, BaseAmqpChannel):

    ## Crea una instancia de OutBoundAmqpChannel
    # @param reconnectionTimer Temporizador de reconexion
    # @param maxReconnections Numero maximo de reconexiones
    # @param host Nombre del host ej: amqp://server:port/exchange/queue/key
    def __init__(self, host="", reconnectionTimer=reconnectiontimers.CreateLogarithmicTimer(),
                 maxReconnections=Channel.MAX_RECONNECTIONS, compressor = compressors.DefaultCompressor(), useAck=False,
                 user='guest', password='guest'):

        BaseAmqpChannel.__init__(self, host, user, password)
        OutBoundChannel.__init__(self, host, reconnectionTimer, maxReconnections, compressor, useAck=useAck)

    def _connect_point(self):
        BaseAmqpChannel._connect_point(self)
        if self._useAck:
            self._channel.confirm_delivery()

    def _close_point(self):
        BaseAmqpChannel._close_point(self)

    def _send(self, message, routingKey=''):
        try:
            msg = amqp.Message(message, content_type='text/plain', delivery_mode=2)
            if routingKey == '':
                return self._channel.basic_publish(msg, exchange=self._exchange, routing_key=self._key)
            else:
                return self._channel.basic_publish(msg, exchange=self._exchange, routing_key=routingKey)

        except amqp.AMQPError as ex:
            loggerManager.get_endPoints_logger().error("Error: %s" % ex)
            raise ConnectionError("Se ha perdido la conexcion con el servidor AMPQ")
        except socket.error as ex:
            loggerManager.get_endPoints_logger().error("Error: %s" % ex)
            raise ConnectionError("Se ha perdido la conexcion con el servidor AMPQ")
        except Exception as ex:
            loggerManager.get_endPoints_logger().error("Error: %s" % ex)
            raise SendError('Error al enviar el elemento %s' % ex)


class InBoundAmqpChannel(InBoundChannel, BaseAmqpChannel):

    ## Crea una instancia de InBoundAmqpChannel
    # @param reconnectionTimer Temporizador de reconexion
    # @param maxReconnections Numero maximo de reconexiones
    # @param host Nombre del host ej: amqp://server:port/queue
    # @param receptionTimeout Timeout de recepcion de mensaje en milisegudos por defecto 20000
    def __init__(self, host="", reconnectionTimer=reconnectiontimers.CreateLogarithmicTimer(),
                 maxReconnections=Channel.MAX_RECONNECTIONS, receptionTimeout = 10, compressor = compressors.DefaultCompressor(),
                 useAck=False, user='guest', password='guest', max_threads=1):

        BaseAmqpChannel.__init__(self, host, user, password)
        InBoundChannel.__init__(self, host, reconnectionTimer, maxReconnections, compressor= compressor,
            useAck=useAck)
        self._receptionTimeout = receptionTimeout
        self.__isConsuming = False
        self.__semaforo = threading.Semaphore(max_threads)

    def _connect_point(self):
        BaseAmqpChannel._connect_point(self)
        self._channel.basic_qos(prefetch_size=0, prefetch_count=10000, a_global=False)
        # self._connection.add_timeout(self._receptionTimeout, self._stopReceive)

    def _close_point(self):
        BaseAmqpChannel._close_point(self)

    def __readMessage(self, msg):
        self.__semaforo.acquire()
        threading.Thread(target=self.__worker, kwargs={"msg" : msg}).start()

    def __worker(self, msg):
        self._processMessage(msg.body, 0, { "channel" : msg.channel, "delivery_tag": msg.delivery_tag })
        self.__semaforo.release()

    def _startReceive(self):
        self._channel.basic_consume(callback=self.__readMessage, queue=self._queue, no_ack=False)
        while self.isRunning:
            self._channel.wait()

    def _stopReceive(self):
        self._channel.stop_consuming()

    def _sendAck(self, object, idMessage):
        object["channel"].basic_ack(delivery_tag=object["delivery_tag"])

