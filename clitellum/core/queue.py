# author = sbermudel
# package description
from datetime import datetime
import os
import struct
import threading

from time import sleep, time
from pymongo import *

try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident


## Crea una cola desde un objeto de configuracion
#  { type : "MongoDb"
#     host: "mongodb://db1.example.net,db2.example.net:2500/?replicaSet=test&connectTimeoutMS=300000&maxPoolSize=20",
#     database: "MiBaseDeDatos",
#     collection: "MiColeccion" }
def CreateQueueFromConfig(config):
    if config.get("type").lower() == "mongodb":
        return MongoQueue(connection=config["host"], dbName=config['database'], collection=config['collection'])
    else:
        return MongoQueue(connection=config["host"], dbName=config['database'], collection=config['collection'])


def CreateMongoDbQueue(host, dbName, collection, auto_purge=True):
    return MongoQueue(host, dbName, collection, auto_purge=auto_purge)


## Clase que base que contiene los metodos basicos de cola
# con persistencia
class PersistenceQueue:
    def __init__(self, connection):
        self.__connection = connection

    @property
    def count(self):
        return 0

    @property
    def connectionString(self):
        return self.__connection

    def purge(self):
        pass

    def append(self, obj):
        pass

    def popleft(self, sleep_wait=True):
        pass

    def task_done(self):
        pass

    def task_not_done(self):
        pass

    def peek(self):
        pass


class MongoQueue(PersistenceQueue):
    def __init__(self, connection, dbName, collection, auto_purge=True):
        PersistenceQueue.__init__(self, connection)
        self._connectionString = connection
        self._colName = collection
        self._dbName = dbName

        #self._conn = MongoClient(self._connectionString)
        self._conn = Connection(self._connectionString)
        if not self._colName in self._conn[self._dbName].collection_names():
            self._conn[self._dbName].create_collection(self._colName)

        self._collection = self._conn[self._dbName][self._colName]
        if auto_purge:
            self._collection.ensure_index( [("ProcessedAt", 1), ], name='_idx_Processed', expireAfterSeconds=3600)
            #else:
            #TODO: Eliminar el indice si no tiene auto_purge

        self._collection.ensure_index( [("Status", 1), ], name='_idx_Status')
        self._collection.update({"Status":1}, { "$set": {"Status":0, "ProcessedAt": None}}, multi=True)

        self._localStorage = threading.local()

    @property
    def count(self):
        return self._collection.count({"Status" : 0})

    @property
    def path(self):
        return self._connectionString

    def purge(self):
        self._collection.drop()

    def append(self, obj):
        self._collection.insert({ "Value" : obj, "Status" : 0, "ProcessedAt": None})

    def popleft(self, sleep_wait=True, timeout=-1):
        keep_pooling = True
        wait = 0.1
        max_wait = 2
        tries = 0

        start = time()

        while keep_pooling:
            rec = self._collection.find_and_modify(query={"Status" : 0}, update={ "$set": {"Status":1}})
            if not rec is None:
                self._localStorage.rec = rec['_id']
                return rec["Value"]
            else:
                if not sleep_wait:
                    keep_pooling = False
                    continue
                runningTime = time() - start
                if 0 < timeout < runningTime:
                    keep_pooling = False
                    continue
                tries += 1
                sleep(wait)
                wait = min(max_wait, tries/10 + wait)

        return None

    def task_done(self):
        self._collection.find_and_modify(query={"_id" : self._localStorage.rec},
                                    update={ "$set": {"Status":2, "ProcessedAt": datetime.utcnow()}})

    def task_not_done(self):
        self._collection.find_and_modify(query={"_id" : self._localStorage.rec},
                                    update={ "$set": {"Status":0, "ProcessedAt": None}})
    def peek(self):
        rec = self._collection.find_one(query={"Status" : 0})
        if not rec is None:
            return rec["Value"]
        else:
            return None

    def __del__(self):
        self._conn.close()

class FileQueue(PersistenceQueue):
    def __init__(self, connection):
        PersistenceQueue.__init__(self, connection)
        self.__connection = os.path.abspath(connection)
        if not os.path.exists(os.path.dirname(self.__connection)):
            os.makedirs(os.path.dirname(self.__connection))

        self.__fileReader = open(self.__connection, "r+b")
        self.__fileWriter = open(self.__connection, "wb")
        self.__fileAck = open(self.__connection, "r+b")

        self._localStorage = threading.local()
        self.__writerLock = threading.Lock()
        self.__readerLock = threading.Lock()
        self.__ackLock = threading.Lock()

    @property
    def count(self):
        return 0

    @property
    def connectionString(self):
        return self.__connection

    def purge(self):
        pass

    def append(self, obj):
        self.__writerLock.acquire()
        item = str(datetime.datetime.now())
        buffer = struct.pack('!I%ds' % (len(item),), len(item), item)
        self.__fileWriter.write(buffer)
        self.__fileWriter.flush()
        self.__writerLock.release()

    def popleft(self, sleep_wait=True, timeout=-1):
        keep_pooling = True
        wait = 0.1
        max_wait = 2
        tries = 0

        start = time()

        while keep_pooling:
            rec = self.__readFromQueue()
            if not rec is None:
                self._localStorage.rec = rec['_id']
                return rec["Value"]
            else:
                if not sleep_wait:
                    keep_pooling = False
                    continue
                runningTime = time() - start
                if 0 < timeout < runningTime:
                    keep_pooling = False
                    continue
                tries += 1
                sleep(wait)
                wait = min(max_wait, tries/10 + wait)

        return None

    def __readFromQueue(self):
        self.__readerLock.acquire()
        item = None
        itemPos = self.__fileReader.tell()
        while True:
            buffer = self.__fileReader.read(4)
            if buffer != '':
                length = struct.unpack('>I', buffer)[0]
                item = self.__fileReader.read(length).strip('\0')

                if item != '':
                    break
            else:
                break

        self.__readerLock.release()
        return { "Id": itemPos, "Value": item }

    def task_done(self):
        self.__ackLock.acquire()
        self.__fileAck.seek(self._localStorage.rec)
        buffer = self.__fileAck.read(4)
        if buffer != '':
            length = struct.unpack('>I', buffer)[0]
            empty = struct.pack('!%ds'%length, "")
            self.__fileAck.write(empty)
            self.__fileAck.flush()

        self.__ackLock.release()

    def task_not_done(self):
        self.__readerLock.acquire()
        self.__fileReader.seek(self._localStorage.rec)
        self.__readerLock.release()

    def peek(self):
        pass

    def __del__(self):
        self.__fileReader.close()
        self.__fileWriter.close()
        self.__fileAck.close()
