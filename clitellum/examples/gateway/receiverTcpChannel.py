import os
import sys
import signal

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../../../../'))

from clitellum.core import loadbalancers, queue
from clitellum.endpoints.channels.amqpchannels import OutBoundAmqpChannel
from clitellum.endpoints.gateways import SenderGateway

__author__ = 'sergio'

rabbit_server = "192.168.4.28"

from clitellum.endpoints.channels.tcpsocket import *


class AgencyReceiver:
    def __init__(self, cfg):
        signal.signal(signal.SIGTERM, self.signal_handler)

        lb = loadbalancers.CreateRouterFromConfig(None)
        q = queue.CreateQueueFromConfig(cfg['senderGateway']['queue'])
        channels = list()
        for i in range(0,int(cfg['senderGateway']['channel']['number'])):
            channels.append(OutBoundAmqpChannel(host = cfg['senderGateway']['channel']['url'],
                                                useAck=bool(cfg['senderGateway']['channel']['useAck'])))

        self.amqpGateway = SenderGateway(lb, q, channels=channels, numExtractors=len(channels))
        self.amqpGateway.connect()

        self.inbound = InBoundChannelTcp(host=cfg['receiverGateway']['url'], receptionTimeout= int(cfg['receiverGateway']['receptionTimeout']),
                                    compressor= compressors.CreateCompressor(cfg['receiverGateway']['compressor']['type'],
                                                                             cfg['receiverGateway']['compressor']['level']),
                                                                            useAck=bool(cfg['receiverGateway']['useAck']))
        self.inbound.OnMessageReceived += self.received_message

    def signal_handler(self, signal, frame):
        loggerManager.getlogger().debug('Parando...')
        self.amqpGateway.stop()
        self.inbound.stop()
        self.inbound.close()
        self.amqpGateway.close()
        loggerManager.getlogger().debug('Parado')
        sys.exit(0)

    def received_message(self, sender,args):
        self.amqpGateway.send(args.message)

    def launch(self):
        self.inbound.start()
        self.amqpGateway.start()

        signal.pause()







