import socket
import threading
from time import sleep

__author__ = 'sergio'

stop = False

def readData(clientSocket):
    chunk = []
    print ('Conexion establecida')
    while True:
        try:
            chunk = clientSocket.recv(2048)
            print(chunk)
            if stop:
                break
        except Exception as ex:
            print(ex)
            pass
    # clientSocket.close()

_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# _socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
# _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# _socket.settimeout(10)
# socket.setdefaulttimeout(10)
_socket.bind(('10.17.148.13', 5551))
_socket.listen(10000)

def accept():
    while True:
        try:
            if stop:
                break
            (clientSocket, address) = _socket.accept()
            # clientSocket = socket.fromfd(cls.fileno(), socket.AF_INET, socket.SOCK_STREAM)
            th = threading.Thread(target=readData, args=(clientSocket,))
            th.start()
        except socket.timeout as ex:
            pass


for i in range(0, 1):
    th = threading.Thread(target=accept)
    th.start()

input('Pulsa Enter para finalizar')
print ("Parando ...")
stop = True

_socket.close()