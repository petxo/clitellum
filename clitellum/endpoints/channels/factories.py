# author = sbermudel
# package description
from clitellum.core import compressors
from clitellum.endpoints.channels import reconnectiontimers
from clitellum.endpoints.channels.amqpchannels import OutBoundAmqpChannel
from clitellum.endpoints.channels.basechannels import Channel
from clitellum.endpoints.channels.tcpsocket import OutBoundChannelTcp
from clitellum.endpoints.channels.zeromq import OutBoundChannelZeroMq


## Crea un canal a partir de una configuracion
# { type : 0Mq,
#   timer : Logarithmic,
#   host : tcp://server:8080,
#   maxReconnections : 20,
#   compressor: { type="gzip", compressionLevel: 9 },
#   useAck : False}
def CreateOutBoundChannelFromConfig(config):
    timer = reconnectiontimers.CreateTimerFormType(config["timer"])
    compressor = compressors.CreateCompressorFromConfig(config["compresor"])

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