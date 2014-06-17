import logging
import logging.config
import os
from config import Config
import yaml
from clitellum.endpoints import gateways

__author__ = 'sergio'

filecfg = os.path.join(os.path.dirname(__file__), 'rabbitGateways.cfg')
cfg = Config(filecfg)

logcfg = yaml.load(open('logging.yml', 'r'))
logging.config.dictConfig(logcfg)

sender = gateways.CreateSenderFromConfig(cfg['senderGateway'])

sender.connect()

for i in range(0, 100000):
    sender.send('HolaMundo')

sender.close()
