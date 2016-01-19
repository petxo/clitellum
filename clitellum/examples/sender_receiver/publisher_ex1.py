from config import Config
from clitellum import publishers
import logging
import logging.config

import yaml

logcfg = yaml.load(open('logging.yml', 'r'))
logging.config.dictConfig(logcfg)

cfg = Config("publisher.cfg")
pb = publishers.create_agent_from_config(cfg)
print "Publicando el mensaje de saludo"
msg = {'Mensaje' : 'Hola soy el publicador'}

for i in range(0, 1):
    pb.publish(msg, "Saludos.MensajeSaludo")




