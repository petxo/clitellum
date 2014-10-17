import json
from clitellum.core.compressors import GzipCompressor

__author__ = 'lfernandm'


class MessageParser:
    def __init__(self):
        pass

    @classmethod
    def _byterize(cls, value, numBytes):
        displacements = range(0, numBytes * 8, 8)
        return [value >> i & 0xff for i in displacements]

    @classmethod
    def _unByterize(cls, byterizedValue):
        displacements = range(0, (len(byterizedValue)) * 8, 8)
        return sum(0x00000000000000000000000000000000 + byterizedValue[i] << displacements[i] for i in range(0, len(byterizedValue)))

    @classmethod
    def ToBytes(cls, message):
        serializedMessage = json.dumps(message)
        bytesMessage = GzipCompressor().compress(serializedMessage)
        bytesBodyType = message['Header']['BodyType'].encode('utf-8')
        callerContext = None
        callerContextL = len(message['Header']['CallStack']['_array'])
        if callerContextL > 0:
            callerContext = message['Header']['CallStack']['_array'][callerContextL - 1]
        idBytes = bytearray()
        typeBytes = bytearray()
        if callerContext is not None:
            idBytes = callerContext['Identification']['Id'].encode('utf-8')
            typeBytes = callerContext['Identification']['Type'].encode('utf-8')
        bMessage = bytearray()
        bMessage.append(message['Header']['Type'])
        bMessage.append(message['Header']['Priority'])
        bMessage.append(0)
        ticks = int(message['Header']['CreatedAt'])
        bMessage.extend(cls._byterize(ticks, 8))
        bMessage.extend(cls._byterize(len(bytesBodyType), 4))
        bMessage.extend(bytesBodyType)
        bMessage.extend(cls._byterize(len(bytesMessage), 4))
        bMessage.extend(bytesMessage)
        bMessage.extend(cls._byterize(len(idBytes), 4))
        if callerContext is not None:
            bMessage.extend(idBytes)
            bMessage.extend(cls._byterize(len(typeBytes), 4))
            bMessage.extend(typeBytes)
        return bMessage

    @classmethod
    def GetMessageFromBytes(cls, binMessage):
        compressor = GzipCompressor()
        bodyTypeLength = cls._unByterize(binMessage[11:15])
        messagePosition = 15 + bodyTypeLength
        messageLength = cls._unByterize(binMessage[messagePosition:messagePosition + 4])
        return compressor.decompress(binMessage[messagePosition + 4:messagePosition + 4 + messageLength])
