import logging
import logging.config

import yaml

from clitellum.endpoints.channels.amqpchannels import InBoundAmqpChannel, OutBoundAmqpChannel


__author__ = 'sergio'

sender = OutBoundAmqpChannel(host='amqp://192.168.4.128:5672/Mrw.Gestion3.Exch/Operativa.UI.Bulto.Input2/Operativa.UI.BultoInputKey2', useAck=False)

def received_message(s,args):
    # print args.message
    sender.send(args.message)
    pass

logcfg = yaml.load(open('logging.yml', 'r'))
logging.config.dictConfig(logcfg)
sender.connect()

inbound = InBoundAmqpChannel(host='amqp://192.168.4.128:5672/Mrw.Gestion3.Exch/Operativa.UI.Bulto.Input/Operativa.UI.BultoInputKey',
                             receptionTimeout=10, useAck=True)
inbound.OnMessageReceived += received_message
inbound.start()


input('Pulsa Enter para finalizar')
print "Parando ..."

inbound.stop()
inbound.close()
sender.close()
