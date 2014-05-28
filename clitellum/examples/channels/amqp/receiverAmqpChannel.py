import logging
import logging.config

import yaml

from clitellum.endpoints.channels.amqpchannels import InBoundAmqpChannel


__author__ = 'sergio'


def received_message(sender,args):
    # print args.message
    pass

logcfg = yaml.load(open('logging.yml', 'r'))
logging.config.dictConfig(logcfg)

inbound = InBoundAmqpChannel(host='amqp://localhost:5672/exhTest/queueTest/key', receptionTimeout=10, useAck=True)
inbound.OnMessageReceived += received_message
inbound.start()

input('Pulsa Enter para finalizar')
print "Parando ..."

inbound.stop()
inbound.close()
