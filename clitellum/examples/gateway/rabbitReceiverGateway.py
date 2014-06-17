import logging
import logging.config
import os
from config import Config
import yaml
from clitellum.endpoints import gateways

__author__ = 'sergio'

def message_received(sender, args):
    # print args.message
    pass

filecfg = os.path.join(os.path.dirname(__file__), 'rabbitGateways.cfg')
cfg = Config(filecfg)

logcfg = yaml.load(open('logging.yml', 'r'))
logging.config.dictConfig(logcfg)

recv = gateways.CreateReceiverFromConfig(cfg['receiverGateway'])

recv.connect()
recv.OnMessageReceived += message_received
recv.start()

input('Pulsa Enter para finalizar')
print "Parando ..."

recv.stop()
recv.close()
