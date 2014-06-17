# author = sbermudel
# package description
from clitellum.core import compressors
from clitellum.endpoints.channels import reconnectiontimers
from clitellum.endpoints.channels.amqpchannels import OutBoundAmqpChannel, InBoundAmqpChannel
from clitellum.endpoints.channels.basechannels import Channel
from clitellum.endpoints.channels.tcpsocket import OutBoundChannelTcp, InBoundChannelTcp
from clitellum.endpoints.channels.zeromq import OutBoundChannelZeroMq, InBoundChannelZeroMq


## Crea un canal a partir de una configuracion
# { type : 0Mq,
#   timer : Logarithmic,
#   host : tcp://server:8080,
#   maxReconnections : 20,
#   compressor: { type="gzip", compressionLevel: 9 },
#   useAck : False}
def CreateOutBoundChannelFromConfig(config):
    timer = reconnectiontimers.CreateTimerFormType(config["timer"])
    compressor = compressors.CreateCompressorFromConfig(config["compressor"])

    maxReconnections = Channel.MAX_RECONNECTIONS
    if not config.get("maxReconnections") is None:
        maxReconnections = int(config.get("maxReconnections"))

    useAck = False
    if not config.get("useAck") is None:
        useAck = bool(config.get("useAck"))

    if config.get("type").lower() == "0mq":
        channel = OutBoundChannelZeroMq(config["host"], reconnectionTimer=timer,
                                        maxReconnections=maxReconnections, compressor=compressor)
    elif config.get("type").lower() == "tcp":
        channel = OutBoundChannelTcp(config["host"], reconnectionTimer=timer,
                                     maxReconnections=maxReconnections, compressor=compressor, useAck=useAck)
    elif config.get("type").lower() == "amqp":
        channel = OutBoundAmqpChannel(config["host"], reconnectionTimer=timer,
                                      maxReconnections=maxReconnections, compressor=compressor, useAck=useAck)
    else:
        channel = OutBoundChannelTcp(config["host"], reconnectionTimer=timer,
                                     maxReconnections=maxReconnections, compressor=compressor, useAck=useAck)
    return channel


def CreateInBoundChannelFromConfig(config):
    timer = reconnectiontimers.CreateTimerFormType(config["timer"])
    compressor = compressors.CreateCompressorFromConfig(config["compressor"])

    maxReconnections = Channel.MAX_RECONNECTIONS
    if not config.get("maxReconnections") is None:
        maxReconnections = int(config.get("maxReconnections"))

    useAck = False
    if not config.get("useAck") is None:
        useAck = bool(config.get("useAck"))

    if config.get("type").lower() == "0mq":
        channel = InBoundChannelZeroMq(config["host"], reconnectionTimer=timer,
                                       maxReconnections=maxReconnections, compressor=compressor)
    elif config.get("type").lower() == "tcp":
        channel = InBoundChannelTcp(config["host"], reconnectionTimer=timer,
                                    maxReconnections=maxReconnections, compressor=compressor, useAck=useAck)
    elif config.get("type").lower() == "amqp":
        user = 'guest'
        password = 'guest'

        if not config['user'] is None:
            user = config['user']
        if not config['password'] is None:
            password = config['password']

        channel = InBoundAmqpChannel(config["host"], reconnectionTimer=timer,
                                     maxReconnections=maxReconnections, compressor=compressor, useAck=useAck,
                                     user=user, password=password)
    else:
        channel = InBoundChannelTcp(config["host"], reconnectionTimer=timer,
                                    maxReconnections=maxReconnections, compressor=compressor, useAck=useAck)
    return channel