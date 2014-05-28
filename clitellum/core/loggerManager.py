import logging

__author__ = 'sergio'


def getlogger():
    return logging.getLogger("pyLightEsb")


def get_core_logger():
    return logging.getLogger("pyLightEsb.core")


def get_endPoints_logger():
    return logging.getLogger("pyLightEsb.endpoints")
