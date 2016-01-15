import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../../../../'))

from clitellum.core import loadbalancers, queue
from clitellum.endpoints.channels.amqpchannels import OutBoundAmqpChannel
from clitellum.endpoints.gatewaysqueue import SenderGatewayQueue

__author__ = 'sergio'

rabbit_server = "localhost"

from clitellum.endpoints.channels.tcpsocket import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - (%(threadName)-10s) %(message)s', )
#loggerManager.getlogger().setLevel(logging.DEBUG)

lb = loadbalancers.CreateRouterFromConfig(None)
q = queue.CreateMongoDbQueue(host="mongodb://localhost", dbName="Gateway", collection="Queue")
channels = list()
for i in range(0,20):
    channels.append(OutBoundAmqpChannel(host='amqp://%s:5672/MyExch/MyQueue.Input/MyQueueInputKey' % rabbit_server, useAck=True))

amqpGateway = SenderGatewayQueue(lb, q, channels=channels, numExtractors=len(channels))
amqpGateway.connect()
amqpGateway.start()

def received_message(sender,args):
    amqpGateway.send(args.message)

server = '0.0.0.0'
try:
    inbound = InBoundChannelTcp(host='tcp://%s:5556' % server, receptionTimeout=5,
                                compressor= compressors.CreateCompressor("gzip", 9), useAck=True)

    inbound.OnMessageReceived += received_message
    inbound.start()

    raw_input('Pulsa Enter para finalizar')
    print "Parando ..."

    amqpGateway.stop()
    inbound.stop()
    inbound.close()
    amqpGateway.close()
except Exception as ex:
    print ex

