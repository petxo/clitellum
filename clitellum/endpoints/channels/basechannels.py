## @package pylightesb.endpoints.channels.basechannels
#  Este paquete contiene las clases para la comunicacion entre componentes
import threading

from clitellum.core import compressors, loggerManager
from clitellum.endpoints.channels.events import *
from clitellum.endpoints.channels.exceptions import *
from clitellum.core.eventhandling import EventHook
from clitellum.core.fsm import Startable
from clitellum.endpoints.channels import reconnectiontimers

## Clase base que gestiona que define un punto de conexion con un host, y que gestiona
# las reconexiones mediante un temporizador
class Channel:
    INFINITE_RECONNECTIONS = -1
    MAX_RECONNECTIONS = INFINITE_RECONNECTIONS


    ## Crea una instancia de un punto de conexion, y estable el temporizador
    # de la reconexion
    # @param host Nombre del host
    # @param reconnectionTimer Temporizador de la reconexion (ReconnectionTimer) por defecto Logaritmico
    # @param maxReconnections Numero maximo de reconexiones por defecto 10
    # @param useCompression Indica si el punto de conexion usa compresion
    def __init__(self, host="", reconnectionTimer=reconnectiontimers.CreateLogarithmicTimer(),
                 maxReconnections=MAX_RECONNECTIONS, compressor=compressors.DefaultCompressor(), useAck=False):
        self._isConnected = False
        self._reconnectionTimer = reconnectionTimer
        self._reconnectionNumber = 0
        self._maxReconnections = maxReconnections
        self.OnConnectionError = EventHook()
        self._host = host
        self._useAck = useAck
        self._compressor = compressor

    ## Establece la conexion con el host, en el caso de no establecerse
    # se procede a la reconexion hasta que el temporizador llegue a su limite de intentos
    # de reconexion
    def connect(self):
        try:
            self._reconnect()
        except ConnectionError:
            self._invokeOnConnectionError()

    ## Indica si el punto de conexion esta conectado con el host
    def is_connected(self):
        return self._isConnected

    ## Devuelve el nombre del host del punto de conexion
    def getHost(self):
        return self._host

    ## Cierra la conexion con el host
    def close(self):
        try:
            if self._isConnected:
                self._close_point()
        except:
            pass

        self._isConnected = False


    ## Metodo que realiza la conexion fisica con el host
    # @exception ConnectException Se lanza en el caso de que no sea posible la conexion
    def _connect_point(self):
        raise ConnectionError("Error de conexion, clase base")

    ## Cierra la conexion fisica con el host
    def _close_point(self):
        raise ConnectionError("Error de conexion, clase base")

    ## Realiza la reconexion en el caso de que se produca una excepcion
    # @exception ConnectException Se lanza en el caso de que se haya llegado al limite de
    # intentos de reconexion
    def _reconnect(self):
        # Si ya esta conectado no reconecta
        if self._isConnected:
            return

        self._reconnectionNumber = 0
        self._reconnectionTimer.reset()
        self._isConnected = False

        while True:
            try:
                loggerManager.get_endPoints_logger().debug("Conectando al host: %s", self._host)
                self._connect_point()
                break
            except ConnectionError as ex:
                loggerManager.get_endPoints_logger().error("Error al conectar: %s" % ex)
                if self._maxReconnections != Channel.INFINITE_RECONNECTIONS and self._reconnectionNumber >= self._maxReconnections:
                    loggerManager.get_endPoints_logger().error("Se ha alcanzado el maximo numero de reconexiones")
                    raise ConnectionError("Se ha alcanzado el maximo numero de reconexiones")
                else:
                    loggerManager.get_endPoints_logger().error("Intentado reconectar... %d, Host: %s" % (self._reconnectionNumber, self._host))
                    self._reconnectionNumber += 1
                    self._reconnectionTimer.wait()
        self._isConnected = True

    ## Lanza el evento OnConnectionError
    def _invokeOnConnectionError(self):
        args = ConnectionErrorArgs(channel=self, maxReconnections=self._maxReconnections,
                                   numReconnections=self._reconnectionNumber, timer=self._reconnectionTimer)
        self.OnConnectionError.fire(self, args)
        del args

    ## Destructor, si la conexion esta abierta la cierra y libera todos los handler del
    # controlador de eventos
    def __del__(self):
        if self.is_connected():
            self.close()
        self.OnConnectionError.clear()


## Clase que implementa un un punto de conexion de salida
class OutBoundChannel(Channel):
    ## Crea una instancia de OutBoundChannel
    # @param reconnectionTimer Temporizador de reconexion
    # @param maxReconnections Numero maximo de reconexiones
    # @param host Nombre del host
    def __init__(self, host="", reconnectionTimer=reconnectiontimers.CreateLogarithmicTimer(),
                 maxReconnections=Channel.MAX_RECONNECTIONS, compressor=compressors.DefaultCompressor(), useAck=False):
        Channel.__init__(self, host, reconnectionTimer, maxReconnections, compressor, useAck)
        self.OnSendError = EventHook()
        self._mutex = threading.Lock()
        self.OnMessageSent = EventHook()

    ## Lanza el evento
    def _invokeOnSendError(self, message):
        args = SendErrorArgs(channel=self, message=message)
        self.OnSendError.fire(self, args)
        del args

    ## Lanza el evento de mensaje enviado
    def _invokeOnMessageSent(self, message):
        args = SentMessageArgs(channel=self, message=message)
        self.OnMessageSent.fire(self, args)
        del args


    ## Envia un mensaje al punto de conexion
    def send(self, message, routingKey=''):
        ret = True
        self._mutex.acquire()
        while True:
            try:
                #loggerManager.get_endPoints_logger().debug("Enviando mensaje %s" % message)
                msg = self._compressor.compress(message)
                ret = self._send(msg, routingKey)
                if not ret:
                    self.__checkMessageSent(message)
                else:
                    self._invokeOnMessageSent(message)

                del msg
                break
            except ConnectionError as ex:
                loggerManager.get_endPoints_logger().error("Error de conexion al enviar el mensaje %s" % ex)
                # Intentamos reconectar
                try:
                    self.close()
                    self._reconnect()
                except ConnectionError as ex2:
                    loggerManager.get_endPoints_logger().error(
                        "No se ha podido reconectar al enviar el mensaje %s" % ex2)
                    self._invokeOnSendError(message)
                    break
            except SendError as ex:
                loggerManager.get_endPoints_logger().error("Error de envio %s" % ex)
                self._invokeOnSendError(message)
                break
            except Exception:
                raise

        self._mutex.release()
        return ret

    ## Envia un mensaje al punto de conexion
    # @param message Buffer a enviar
    # @param routingKey Clave de enrutamiento
    # @exception ConnectionError
    def _send(self, message, routingKey=''):
        raise SendError("Metodo no implementado")

    ## Espera el acuse de recibo del mensaje enviado
    def _waitForAck(self):
        return True

    ## Realiza la comprobacion de que el mensaje a sido enviado y lanza los eventos
    def __checkMessageSent(self, message):
        if self._useAck:
            ret = self._waitForAck()
            if ret:
                self._invokeOnMessageSent(message)
            else:
                self._invokeOnSendError(message)
            return ret
        else:
            self._invokeOnMessageSent(message)
            return True

    def __del__(self):
        self.OnMessageSent.clear()
        self.OnSendError.clear()
        Channel.__del__(self)


## Clase que implementa un un punto de conexion de salida
class InBoundChannel(Channel, Startable):
    ## Crea una instancia de InBoundChannel
    # @param reconnectionTimer Temporizador de reconexion
    # @param maxReconnections Numero maximo de reconexiones
    # @param host Nombre del host
    def __init__(self, host="", reconnectionTimer=reconnectiontimers.CreateLogarithmicTimer(),
                 maxReconnections=Channel.MAX_RECONNECTIONS, compressor=compressors.DefaultCompressor(), useAck=False):
        Channel.__init__(self, host, reconnectionTimer, maxReconnections, compressor, useAck)
        Startable.__init__(self)
        self._thReceive = threading.Thread(target=self.__workReceive)
        self.OnMessageReceived = EventHook()
        self.OnStart += self.__beginReceive
        self.OnStopped += self.__endReceive

    ## Lanza el evento Message Received
    def __invokeOnMessageReceived(self, message):
        args = MessageReceivedArgs(message=message)
        self.OnMessageReceived.fire(self, args)
        del args

    ## Lanza el inicio de la recepcion de mensajes
    def __beginReceive(self):
        if not self._isConnected:
            self.connect()
        self._initializeReceive()
        self._thReceive.start()

    ## Propiedad que indica si el punto de conexion esta recibiendo mensajes
    @property
    def isRunning(self):
        return self.state == Startable.RUNNING

    ## Metodo del hilo en el que se ejecuta la recepcion de mensajes
    def __workReceive(self):
        while True:
            try:
                if self.isRunning:
                    self._startReceive()
                else:
                    self._stopReceive()
                    break
            except Exception as ex:
                # Intentamos reconectar
                try:
                    loggerManager.get_endPoints_logger().error("Error en la recepcion de mensajes %s" % ex)
                    self.close()
                    self._reconnect()
                except ConnectionError:
                    self.stop()
                    self._invokeOnConnectionError()
                    break

    ## Finaliza la recepcion de mensajes
    def __endReceive(self):
        self._thReceive.join()
        self._terminateReceive()

    ## Metodo al que las clases hijas deben llamar cuando se recibe un mensaje
    def _processMessage(self, message, idMessage, object):
        try:
            msg = self._compressor.decompress(message)
            self.__invokeOnMessageReceived(msg)
        except Exception as ex:
            loggerManager.get_endPoints_logger().exception("Error al procesar el mensaje")
            raise ex
        finally:
            if self._useAck:
                loggerManager.get_endPoints_logger().debug("Enviando ACK %s" % message)
                self._sendAck(object, idMessage)


    ## Metodo que se las clases hijas deben sobrescribir para realizar la recepcion
    # No se debe dejar bloqueado el hilo
    def _startReceive(self):
        pass

    ## Metodo al que se llama para inicializar la recepcion, sobrescribir en caso que sea necesario
    def _initializeReceive(self):
        pass

    ## Metodo al que se llama para liberar recursos de la recepcion, sobrescribir  en caso que sea necesario
    def _terminateReceive(self):
        pass

    ## Metodo para mandar el ack una vez que el mensaje se ha leido
    def _sendAck(self, object, idMessage):
        pass

    ## Metodo para detener la recepcion de mensajes
    def _stopReceive(self):
        pass