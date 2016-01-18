import socket
from time import sleep

__author__ = 'sergio'

for i in range(0, 1000):
    try:
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        _socket.connect(('10.17.148.13', 5550))
    except Exception as ex:
        print ex

raw_input('Pulsa Enter para finalizar')
print "Parando ..."
