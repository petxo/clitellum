# author = sbermudel
# package description
from datetime import date
import datetime


class Context:
    def __init__(self):
        pass

    _instance = None

    @classmethod
    def create(cls):
        cls._instance = Context()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls.create()
        return cls._instance


class Identification:
    def __init__(self):
        pass

    @classmethod
    def create(cls, id_service, type_service):
        identification = dict()
        identification['Id'] = id_service
        identification['Type'] = type_service
        return identification


class MessageHeader:
    def __init__(self):
        pass

    @classmethod
    def create(cls, body_type, id_service, type_service):
        header = dict()
        header['BodyType'] = body_type
        header['Priority'] = 0
        header['CreatedAt'] = datetime.datetime.now().isoformat()
        header['CallContext'] = dict()
        header['IdentificationService'] = Identification.create(id_service, type_service)
        return header


class MessageBus:
    def __init__(self):
        pass

    ## Devuelve un diccionario del mensaje que se enviara al bus
    @classmethod
    def create(cls, body, body_type, id_service, type_service):
        message = dict()
        message['Body'] = body
        message['Header'] = MessageHeader.create(body_type, id_service, type_service)
        return message

