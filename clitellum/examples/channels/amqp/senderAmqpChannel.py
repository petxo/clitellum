from clitellum.core import compressors
from clitellum.endpoints.channels.amqpchannels import OutBoundAmqpChannel

__author__ = 'sergio'

sender = OutBoundAmqpChannel(host='amqp://localhost:5672/exhTest/queueTest/key',
                            compressor = compressors.CreateCompressor("gzip"), useAck=False)
sender.connect()
for i in range(0,100000):
    sender.send("Test Message")
sender.close()