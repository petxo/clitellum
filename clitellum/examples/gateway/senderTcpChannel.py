import os
import sys
import signal
from clitellum.core import loadbalancers

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../../../../'))

from clitellum.endpoints.channels.amqpchannels import OutBoundAmqpChannel
from clitellum.endpoints.gatewaysqueue import SenderGatewayQueue

__author__ = 'sergio'

rabbit_server = "192.168.4.28"

from clitellum.endpoints.channels.tcpsocket import *


class AgencySender:
    def __init__(self, cfg):
        signal.signal(signal.SIGTERM, self.signal_handler)

        lb = loadbalancers.CreateRouterFromConfig(None)
        q = queue.CreateQueueFromConfig(cfg['senderGateway']['queue'])
        channels = list()
        for i in range(0,int(cfg['senderGateway']['channel']['number'])):
            channels.append(OutBoundAmqpChannel(host = cfg['senderGateway']['channel']['url'],
                                                useAck=bool(cfg['senderGateway']['channel']['useAck'])))
        self.amqpGateway = SenderGatewayQueue(lb, q, channels=channels, numExtractors=len(channels))
        self.amqpGateway.connect()

    def signal_handler(self, signal, frame):
        loggerManager.getlogger().debug('Parando...')
        self.amqpGateway.stop()
        self.amqpGateway.close()
        loggerManager.getlogger().debug('Parado')
        sys.exit(0)

    def start(self):
        self.amqpGateway.start()

        signal.pause()







