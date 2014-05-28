# author = sbermudel
# package description
import re
import socket
import struct
import threading
from time import sleep

from clitellum.core import compressors, loggerManager
from clitellum.endpoints.channels import reconnectiontimers
from clitellum.endpoints.channels.basechannels import OutBoundChannel, Channel, InBoundChannel
from clitellum.endpoints.channels.exceptions import ConnectionError, SendError


class BaseChannelTcp:
    Ack_Message = "Ack"

    ## Crea una instancia de OutBoundChannelTcp
    # @param reconnectionTimer Temporizador de reconexion
    # @param maxReconnections Numero maximo de reconexiones
    # @param host Nombre del host ej: tcp://server:port
    def __init__(self, host=""):
        match = re.search('^(\w+)://(.*):(\d+)', host)
        if match:
            self._protocol = match.group(1)
            self._server = match.group(2)
            self._port = int(match.group(3))
        else:
            raise NameError("Invalid host name", host)

        self._address = socket.getaddrinfo(self._server, self._port)

        self._options = socket.IPPROTO_TCP
        if self._protocol == "udp":
            self._options = socket.IPPROTO_UDP

    def _create_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=self._options)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    def _close_point(self):
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
            sleep(5)
            self._socket = None
        except Exception as ex:
            loggerManager.get_endPoints_logger().error(
                "Error al desconectar del host %s:%i : %s" % (self._server, self._port, ex.message))
        finally:
            del self._socket


class OutBoundChannelTcp(OutBoundChannel, BaseChannelTcp):
    ## Crea una instancia de OutBoundChannelTcp
    # @param reconnectionTimer Temporizador de reconexion
    # @param maxReconnections Numero maximo de reconexiones
    # @param host Nombre del host ej: tcp://server:port
    def __init__(self, host="", reconnectionTimer=reconnectiontimers.CreateLogarithmicTimer(),
                 maxReconnections=Channel.MAX_RECONNECTIONS, compressor=compressors.DefaultCompressor(), useAck=False):
        OutBoundChannel.__init__(self, host, reconnectionTimer, maxReconnections,
                                 compressor=compressor, useAck=useAck)
        BaseChannelTcp.__init__(self, host)

    def _connect_point(self):
        try:
            self._create_socket()
            self._socket.connect((self._server, self._port))
        except socket.error, msg:
            raise ConnectionError(msg)

    def _close_point(self):
        BaseChannelTcp._close_point(self)

    def _send(self, message):
        buff = ''
        try:
            buff = struct.pack('!I%ds' % (len(message),), len(message), message)
            self._socket.send(buff)
        except socket.error as ex:
            raise SendError("Error al enviar el mensaje %s: %s" % (message, ex))
        finally:
            del buff

    def _waitForAck(self):
        try:
            message = ''
            bytesReceived = self._socket.recv(4)
            if not len(bytesReceived) == 4:
                return False

            messageLength = struct.unpack('>I', bytesReceived)[0]
            while len(message) < messageLength:
                chunk = self._socket.recv(messageLength)
                message += chunk

            del bytesReceived, messageLength
            return message == BaseChannelTcp.Ack_Message

        except:
            return False

## Clase que establece una conexion de entrada de tipo TCP con el host
class InBoundChannelTcp(InBoundChannel, BaseChannelTcp):
    ## Crea una instancia de InBoundChannelTcp
    # @param reconnectionTimer Temporizador de reconexion
    # @param maxReconnections Numero maximo de reconexiones
    # @param host Nombre del host
    # @param receptionTimeout Timeout de recepcion de mensaje en milisegudos por defecto 20000
    def __init__(self, host="", reconnectionTimer=reconnectiontimers.CreateLogarithmicTimer(),
                 maxReconnections=Channel.MAX_RECONNECTIONS, receptionTimeout=10,
                 compressor=compressors.DefaultCompressor(),
                 maxConnectionRequests=100, useAck=False):
        InBoundChannel.__init__(self, host, reconnectionTimer, maxReconnections, compressor=compressor,
                                useAck=useAck)
        BaseChannelTcp.__init__(self, host)
        self._maxConnectionRequests = maxConnectionRequests
        self.__receptionTimeout = receptionTimeout
        self.__thReadData = list()

    def _create_socket(self):
        BaseChannelTcp._create_socket(self)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.settimeout(self.__receptionTimeout)
        socket.setdefaulttimeout(self.__receptionTimeout)

    def _connect_point(self):
        try:
            self._create_socket()
            self._socket.bind((self._server, self._port))
            self._socket.listen(self._maxConnectionRequests)
        except Exception as ex:
            loggerManager.get_endPoints_logger().error(
                "Error al conectar con el host %s:%i" % (self._server, self._port))
            loggerManager.get_endPoints_logger().error("Socket de mierda: %s" % self._socket.fileno)
            raise ConnectionError(ex)

    def _close_point(self):
        BaseChannelTcp._close_point(self)

    def _startReceive(self):
        try:
            loggerManager.get_endPoints_logger().debug("Aceptando conexiones")
            (clientSocket, address) = self._socket.accept()
            loggerManager.get_endPoints_logger().info("Conexion establecida con el cliente %s:%i." % (address[0], address[1]))
            th = threading.Thread(target=InBoundChannelTcp.__readData, args=(self, clientSocket), name="TCP client %s:%i" % (address[0], address[1]))
            loggerManager.get_endPoints_logger().debug('Iniciando hilo de lectura %s' % th.getName())
            th.start()
        except socket.timeout as ex:
            loggerManager.get_endPoints_logger().debug("Timeout de aceptacion de conexiones : %s." % ex.message)
            pass
        except Exception as ex:
            loggerManager.get_endPoints_logger().error("Error al aceptar conexiones : %s." % ex.message)
            raise ex

    def __readData(self, clientSocket):
        clientSocket.settimeout(self.__receptionTimeout)
        while self.isRunning:
            try:
                loggerManager.get_endPoints_logger().debug("Leyendo mensaje...")
                message = ''
                idMessage = ''
                messageLength = 0
                bytesReceived = ''
                bytesReceived = clientSocket.recv(4)
                if not len(bytesReceived) == 4:
                    raise Exception("Error al leer cabecera")
                loggerManager.get_endPoints_logger().debug("Cabecera leida.")
                messageLength = struct.unpack('>I', bytesReceived)[0]
                message = clientSocket.recv(messageLength)
                if not len(message) == messageLength:
                    raise Exception("Error de longitud del mensaje : Expected length %s - Actual length %i" % (messageLength, len(message)))
                idMessage = clientSocket.recv(36)
                if not len(idMessage) == 36:
                    raise Exception("Error de identificacion del mensaje : Msg length %i - Msg Id length %i" % (len(message), len(idMessage)))
                self._processMessage(message, idMessage, clientSocket)
            except socket.timeout as ex:
                loggerManager.get_endPoints_logger().error("Error de recepcion : %s." % ex.message)
                break
            except socket.error as ex:
                loggerManager.get_endPoints_logger().error("Error de socket : %s." % ex.message)
                break
            except Exception as ex:
                loggerManager.get_endPoints_logger().error(ex.message)
                break
            finally:
                del message, bytesReceived, messageLength, idMessage
        try:
            clientSocket.shutdown(socket.SHUT_RDWR)
            clientSocket.close()
            clientSocket = None
        except Exception as ex:
            loggerManager.get_endPoints_logger().error("Error al desconectar del cliente : %s" % ex.message)
        finally:
            del clientSocket

    def _sendAck(self, object, idMessage):
        buff = struct.pack('!I%ds' % (len(idMessage),), len(idMessage), idMessage)
        try:
            object.send(buff)
        except Exception as ex:
            loggerManager.get_endPoints_logger().error("Error al enviar el ACK %s" % ex.message)
            raise ex
        finally:
            del buff


