__author__ = 'sbermudel'
## @package clitellum.endpoints.channels.exceptions
#  Este paquete contiene las clases de error de los channels


## Excepion que se produce cuando hay un error en la conexion
class ConnectionError(Exception):

    ## Crea una instancia de ConnectionError
    # @param message Descripcion del error
    def __init__(self, message):
        self.message = message

    ## Conviente la instancia a string
    def __str__(self):
        return repr(self.message)

## Excepion que se produce cuando hay un error en el envio de mensajes
class SendError(Exception):

    ## Crea una instancia de SendError
    # @param message Descripcion del error
    def __init__(self, message):
        self.message = message

    ## Conviente la instancia a string
    def __str__(self):
        return repr(self.message)
