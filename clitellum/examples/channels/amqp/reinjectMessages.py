import logging
import logging.config

import yaml

from clitellum.endpoints.channels.amqpchannels import InBoundAmqpChannel, OutBoundAmqpChannel


__author__ = 'sergio'

output = OutBoundAmqpChannel(host='amqp://192.168.3.186:5672/Mrw.Gestion3.Exch/Mrw.Integracion.Clientes.Sincronizador.Input/Mrw.Integracion.Clientes.SincronizadorInputKey', useAck=False)


def received_message(sender, args):
    output.send(args.message)
    pass


logcfg = yaml.load(open('logging.yml', 'r'))
logging.config.dictConfig(logcfg)

inbound = InBoundAmqpChannel(host='amqp://172.31.5.114:5672/Mrw.Gestion3.Exch/Mrw.Integracion.Clientes.Sincronizador.Input/Mrw.Integracion.Clientes.SincronizadorInputKey', receptionTimeout=10, useAck=True,
                             max_threads=1)
inbound.OnMessageReceived += received_message
output.connect()
inbound.start()

input('Pulsa Enter para finalizar')
print "Parando ..."

inbound.stop()
inbound.close()
output.close()
