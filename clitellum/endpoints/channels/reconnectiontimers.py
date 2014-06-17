from time import sleep
import math

__author__ = 'sergio'
## @package clitellum.endpoints.channels.reconnectiontimers
#  Este paquete contiene las clases para los temporizadores de reconexion
#


## Metodo factoria que crea una instancia de un temporizador
# instantaneo
def CreateInstantTimer():
    return InstantReconnectionTimer()


## Metodo factoria que crea una instancia de un temporizador
# logaritmico
def CreateLogarithmicTimer():
    return LogarithmicReconnectionTimer()

## Metodo factoria que crear una instancia de un temporizador de tiempo constante
def CreateConstantTimer(waiting_time=5):
    return ConstantReconnectionTimer(waiting_time=waiting_time)


## Crea una temporizador en funcion del tipo especificado
# @param type Tipo de temporizador "Instant", "Logarithmic"
def CreateTimerFormType(type):
    if type == "Instant":
        return CreateInstantTimer()
    elif type == 'Constant':
        return ConstantReconnectionTimer()
    else:
        return CreateLogarithmicTimer()

## Crea un temporizador a partir de una configuracion
# { type :'Instant' }
# { type :'Constant', time : 10 }
# { type :'Logarithmic' }
def CreateTimerFormConfig(config):
    if config['type'] == "Instant":
        return CreateInstantTimer()
    elif config['type'] == 'Constant':
        if not config.get['time'] is None:
            return ConstantReconnectionTimer(config['time'])
        else:
            return ConstantReconnectionTimer()
    else:
        return CreateLogarithmicTimer()



## Clase base que proporciona la estructura basica de un temporizador de reconexion
class ReconnectionTimer:
    ## Crea una instancia del temporizador de reconexion
    def __init__(self):
        pass

    ## Se espera una vuelta del ciclo antes de continuar
    def wait(self):
        pass

    ## Reinicia el temporizador
    def reset(self):
        pass


## Clase que proporciona un temporizador de reconexion instantaneo,
# no hay tiempo de espera entre un ciclo y el siguiente
class InstantReconnectionTimer(ReconnectionTimer):
    ## Crea una instancia del temporizador instantaneo
    def __init__(self):
        ReconnectionTimer.__init__(self)

    ## Convierte la instancia a string
    def __str__(self):
        return "Instant Reconnection Timer"


## Define un temporizador de reconexion en el que el tiempo de espera entre un ciclo
# y el siguiente es logaritmico, .
class LogarithmicReconnectionTimer(ReconnectionTimer):
    def __init__(self):
        ReconnectionTimer.__init__(self)
        self.__seed = 1

    def wait(self):
        waitingTime = ((1 + (1 / self.__seed)) ^ self.__seed) * (1 + math.log10(self.__seed))
        if waitingTime < 0:
            waitingTime = 0
        sleep(waitingTime)
        self.__seed += 1

    def reset(self):
        self.__seed = 1

    ## Convierte la instancia a string
    def __str__(self):
        return "Logarithmic Reconnection Timer, seed: %s" % self.__seed


## Define un temporizador de reconexion en el que el tiempo de espera entre un ciclo
# y el siguiente es logaritmico, .
class ConstantReconnectionTimer(ReconnectionTimer):
    def __init__(self, waiting_time=5):
        ReconnectionTimer.__init__(self)
        self.__waiting_time = waiting_time

    def wait(self):
        sleep(self.__waiting_time)

    def reset(self):
        pass

    ## Convierte la instancia a string
    def __str__(self):
        return "Constant Reconnection Timer, seed: %s" % self.__waiting_time