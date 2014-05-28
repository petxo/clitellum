# author = sbermudel
## @package clitellum.core.fsm
#  Este paquete contiene las clases de maquinas de estado
from fluidity import *

from clitellum.core.eventhandling import EventHook



## Implemeta la una maquina de estados start-stop
class StartableStateMachine(StateMachine):

    initial_state = 'Stopped'

    state('Running', enter='_invokeOnStart')
    state('Stopped', enter='_invokeOnStopped')

    transition(from_=['Running','Stopped'], event='start', to='Running')
    transition(from_=['Running','Stopped'], event='stop', to='Stopped')


    ## Crea una isntancia de StartableStateMachine
    def __init__(self):
        self.OnStart = EventHook()
        self.OnStopped = EventHook()
        StateMachine.__init__(self)

    ## Lanza el evento OnStart
    def _invokeOnStart(self):
        self.OnStart.fire()

    ## Lanza el evento OnStopped
    def _invokeOnStopped(self):
        self.OnStopped.fire()

    ## Destructor
    def __del__(self):
        self.OnStart.clear()
        self.OnStopped.clear()


## Esta clase encapsula una maquina de estado capaz de iniciar y parar un proceso
class Startable():

    RUNNING = "Running"
    STOPPED = "Stopped"

    def __init__(self):
        self._statemachine = StartableStateMachine()
        self.OnStart = EventHook()
        self.OnStopped = EventHook()
        self._statemachine.OnStart += self._invokeOnStart
        self._statemachine.OnStopped += self._invokeOnStopped

    ## Devuelve el estado acutal del proceso
    @property
    def state(self):
        return self._statemachine.current_state

    ## Incia el proceso
    def start(self):
        self._statemachine.start()

    ## Termina el proceso
    def stop(self):
        self._statemachine.stop()

    ## Lanza el evento OnStart
    def _invokeOnStart(self):
        self.OnStart.fire()

    ## Lanza el evento OnStopped
    def _invokeOnStopped(self):
        self.OnStopped.fire()

    ## Destructor
    def __del__(self):
        self.OnStart.clear()
        self.OnStopped.clear()