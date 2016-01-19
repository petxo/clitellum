import logging

__author__ = 'sergio'


def getlogger():
    return logging.getLogger("clitellum")


def get_core_logger():
    return logging.getLogger("clitellum.core")


def get_endPoints_logger():
    return logging.getLogger("clitellum.endpoints")


def get_processors_logger():
    return logging.getLogger("clitellum.processors")
