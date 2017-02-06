from clitellum.core import compressors
from clitellum.endpoints.channels.amqpchannels import OutBoundAmqpChannel

__author__ = 'sergio'

sender = OutBoundAmqpChannel(host='amqp://localhost:5672/exhTest',
                             compressor=compressors.CreateCompressor("gzip"), useAck=False)
sender.connect()
for i in range(0, 1):
    sender.send("Test Message", 'key')
sender.close()