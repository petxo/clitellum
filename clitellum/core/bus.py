# author = sbermudel
# package description

from collections import OrderedDict
from clitellum.core import serialization


class Context:

    _instance = None
    @classmethod
    def Create(cls):
        cls._instance = Context()

    @classmethod
    def Instance(cls):
        if cls._instance is None:
           cls.Create()
        return cls._instance

class Identification:
    @classmethod
    def Create(cls, id, type):
        identification = dict()
        identification['Id'] = id
        identification['Type'] = type
        return identification

class MessageHeader:
    @classmethod
    def Create(cls, bodyType, id, type):
        header = dict()
        header['BodyType'] = bodyType
        header['EncodingCodePage'] = 65001
        header['ReinjectionNumber'] = 0
        header['Priority'] = 0
        header['Type'] = 0
        header['CreatedAt'] = '1353929212203' # TODO: Falta calcular los ticks en formato .NET (ticks desde el 1/1/1)
        header['CallContext'] = cls.CreateCallContext()
        header['CallStack'] = cls.CreateCallStack(id, type)
        header['IdentificationService'] = Identification.Create(id, type)
        return header

    @classmethod
    def CreateCallContext(cls):
        callContext = dict()
        callContext['User'] = serialization.dumps(Context.Instance().User.toDic())
        callContext['Application'] = serialization.dumps(Context.Instance().Application.toDic())

        return callContext

    @classmethod
    def CreateCallStack(cls, id, type):
        callStack = OrderedDict()
        callStack['_array'] = list()

        item = OrderedDict()
        item['__type'] = 'CallerContext:#Mrwesb.Core.Messages'
        item['Identification'] = Identification.Create(id, type)
        callStack['_array'].append(item)

        callStack['_size'] = len(callStack['_array'])
        callStack['_version'] = 1

        return callStack

class MessageBus:
    @classmethod
    def Create(cls, body, bodyType, id, type):
        message = dict()
        message['Body'] = body
        message['Header'] = MessageHeader.Create(bodyType, id, type)
        return message

