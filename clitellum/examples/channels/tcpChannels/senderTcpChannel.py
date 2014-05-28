import logging
from time import sleep

from clitellum.core import compressors
from clitellum.endpoints.channels.tcpsocket import OutBoundChannelTcp


__author__ = 'sergio'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - (%(threadName)-10s) %(message)s', )
#loggerManager.getlogger().setLevel(logging.DEBUG)

def OnMessageSent(sender, args):
    print args.message

server = '192.168.254.28'

outbound = OutBoundChannelTcp(host='tcp://%s:80' % server, compressor= compressors.CreateCompressor("gzip", 9), useAck=True)
outbound.OnMessageSent += OnMessageSent
outbound.connect()
for i in range(0,100000):
    outbound.send("Patricioooo 1940:%i" % i)

sleep(3)

outbound.close()

