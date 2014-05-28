# coding=utf-8
# author = sbermudel
## @package clitellum.core.loadbalancers
# Este paquete contiene los balanceadores de carga
import itertools
import threading


## Devuelve el balanceador de carga por defecto
def __defaultLoadBalancer():
    return RoundRobinLoadBalancer()


## Crea un balanceador de carga desde una configuracion
# { type: "RoundRobin" }
def CreateRouterFromConfig(config):
    if config is None:
        return __defaultLoadBalancer()

    if config.get("type") == "RoundRobin":
        return RoundRobinLoadBalancer()
    else:
        return __defaultLoadBalancer()


## Clase que contiene la informacion necesaria para balancear la carga de un canal
class LoadBalancerItem:
    def __init__(self, item, balancingInfo):
        self.item = item
        self.balancingInfo = balancingInfo


## Clase base que define el comportamiento de un balanceador de carga.
# El balanceador de carga es el encargado de distribuir el mensaje en los diferentes canales.
# El tipo de balanceamiento puede ser "Round Robin", etc.
# Al añadir un canal al balanceador, se le indica la informacion de balanceo, especifica para cada
# motor de balanceo.
class LoadBalancer:
    ## Crea una instancia de Router
    def __init__(self):
        self._items = list()
        self._initialized = threading.Event()
        self._load()

    ## Añade un canal con la informacion especifica en al router.
    # @param channel Instancia de OutBoundChannel
    # @param routingInfo Informacion de enrutamiento especifica de cada tipo de motor
    # @param resetAfter Indica si despues de añadir el canal se debe hacer un reset del router
    def addChannel(self, channel, balancingInfo=None, resetAfter=True):
        item = LoadBalancerItem(channel, balancingInfo)
        self._items.append(item)
        if resetAfter:
            self.reset()

    ## Devuelve el siguiente canal al que se le debe enviar el mensaje
    def next(self):
        self._initialized.wait()
        return self._next()

    ## Reinicia el router
    def reset(self):
        self._initialized.clear()
        self._load()
        self._initialized.set()

    ## Metodo que debe ser sobre escrito por cada motor de enrutamiento para reiniciar el router
    def _load(self):
        pass

    ## Metodo que debe ser sobre escrito por cada motor de enrutamiento para enrutar el mensaje
    def _next(self):
        pass


## Clase que implementa un balanceador de carga de tipo round robin
class RoundRobinLoadBalancer(LoadBalancer):

    ## Crea una instancia de RoundRobinLoadBalancer
    def __init__(self):
        LoadBalancer.__init__(self)

    def _load(self):
        self._ciclo = itertools.cycle(self._items)

    def _next(self):
        return self._ciclo.next().item
