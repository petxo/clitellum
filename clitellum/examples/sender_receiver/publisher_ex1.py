from config import Config
from clitellum import publishers

__author__ = 'Sergio'

cfg = Config("publisher.cfg")
pb = publishers.create_agent_from_config(cfg)
print "Publicando el mensaje de saludo"
pb.publish("Hola soy el publicador", "MensajeSaludo")