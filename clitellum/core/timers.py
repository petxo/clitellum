# author = sbermudel
# package description
import time


## Temoraizador de espera hasta que se cumple la condicion del predicado
def waitUntil(somepredicate, timeout, *args):
    period = 0.25
    mustEnd = time.time() + timeout
    while time.time() < mustEnd:
        if somepredicate(args): return True
        time.sleep(period)
    return False
