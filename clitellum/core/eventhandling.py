# coding=utf-8
## @package clitellum.core.eventhandling
#  Este paquete contiene las clases para la gestion de eventos
__author__ = 'sergio'


## Clase que implementa event handling
class EventHook(object):
    ## Crea una instancia del contralador de eventos
    #
    def __init__(self):
        self.__handlers = []

    ## Permite añadir un handler al controlador de eventos
    # @param handler Funcion a la que se llama cuando se lance el evento
    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    ## Elimina un handler del controlador de eventos
    # @param handler Funcion a la que se llama cuando se lance el evento
    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    ## Dispara todos los handelrs asociados
    # @param args Argumentos del evento
    # @param keywargs Argumentos del evento
    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    ## Elimina un handler especificado del contraldor de eventos
    # @param inObject Handler que se quiere eliminar
    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler

    ## Elimina todos los handlers del controlador de eventos
    def clear(self):
        for theHandler in self.__handlers:
            self -= theHandler

    ## Destructor de clase, elimina todos los handlers del controlador de eventos
    #
    def __del__(self):
        self.clear()

