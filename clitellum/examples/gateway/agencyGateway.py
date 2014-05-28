# author = sbermudel
# package description
import logging
import logging.config
from optparse import OptionParser

import yaml
from config import Config

from clitellum.examples.gateway import senderTcpChannel


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="configfile",default="gateway.cfg",
                      help="Configuration File", metavar="FILE")

    (options, args) = parser.parse_args()

    cfg = Config(options.configfile)

    logcfg = yaml.load(open('logging.yml', 'r'))
    logging.config.dictConfig(logcfg)

    snd= senderTcpChannel.AgencySender(cfg)
    snd.start()
    #rcv = receiverTcpChannel.AgencyReceiver(cfg)

    #rcv.launch()


