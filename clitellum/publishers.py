from clitellum.core.bus import MessageBus
from clitellum.core.messageparser import MessageParser
from clitellum.endpoints import gateways
from clitellum.server import Identification

__author__ = 'Sergio'


def create_agent_from_config(cfg):
    identification = Identification(cfg['identification']['id'], cfg['identification']['type'])
    sg = gateways.CreateSenderFromConfig(cfg["sender_gateway"])
    return Publisher(identification, sg)


class Publisher:

    def __init__(self, identification, sender_gateway):
        self._identification = identification
        self._senderGateway = sender_gateway

    @property
    def identification(self):
        return self._identification

    def publish(self, message, key):
        message_bus = MessageBus.Create(message, key, self.identification.id, self.identification.type)
        message_bytes = MessageParser.ToBytes(message_bus)
        self._senderGateway.send(message_bytes)