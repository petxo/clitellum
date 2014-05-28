__author__ = 'sbermudel'
## @package clitellum.endpoints.channels.events
#  Este paquete contiene las clases que definen los argumentos de los eventos


## Clase que contiene la informacion de un error de conexion
class ConnectionErrorArgs:
    ## Crea una instancia de ConnectionErrorArgs
    # @param host Nombre del host
    # @param numReconnections Numero de reconexiones
    # @param maxReconnections Numero maximo de reconexiones permitidas
    # @param timer Temporizador de reconexiones
    def __init__(self, channel, numReconnections= 0, maxReconnections = 0, timer = None):
        self.maxReconections = maxReconnections
        self.numReconnections = numReconnections
        self.channel = channel
        self.timer = timer

    ## Convierte la instancia a string
    def __str__(self):
        return "Host: %s\nReconnections: %s\n MaxReconnections: %s\n Timer %s " % \
               (self.channel.getHost(), self.numReconnections, self.maxReconections, self.timer)

    def __del__(self):
        del self.maxReconections
        del self.numReconnections


## Clase que contiene la informacion de un error en el envio de un mensaje
class SendErrorArgs:

    ## Crea una instancia de SendError
    def __init__(self, channel, message =""):
        self.channel = channel
        self.message = message

    ## Convierte la instancia a string
    def __str__(self):
        return "Host: %s\nMessage: %s" % \
                       (self.channel.getHost(), self.message)

    def __del__(self):
        del self.message


## Clase que contiene la informacion de un error en el envio de un mensaje
class SentMessageArgs:
    ## Crea una instancia de SendError
    def __init__(self, channel, message =""):
        self.channel = channel
        self.message = message

    ## Convierte la instancia a string
    def __str__(self):
        return "Host: %s\nMessage: %s" %\
               (self.channel.getHost(), self.message)

    def __del__(self):
        del self.message


## Clase que contiene la informacion de un error en el envio de un mensaje
class MessageReceivedArgs:

    ## Crea una instancia de SendError
    def __init__(self, message = None):
        self.message = message

    ## Convierte la instancia a string
    def __str__(self):
        return "Host: %s\nMessage: %s" % \
                       (self.message)

    def __del__(self):
        del self.message
