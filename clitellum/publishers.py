from clitellum.core import serialization
from clitellum.core.bus import MessageBus
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
        self._senderGateway.connect()

    @property
    def identification(self):
        return self._identification

    def publish(self, message, key):
        body = serialization.dumps(message)
        message_bus = MessageBus.create(body, key, self.identification.id, self.identification.type)
        message_serialized = serialization.dumps(message_bus)
        self._senderGateway.send(message_serialized, key)
