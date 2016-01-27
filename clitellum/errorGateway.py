import traceback

__author__ = 'sergio'


def create_error_message(message, exception):
    error_message = dict()
    error_message['message'] = message
    error_message['exception'] = dict()
    error_message['exception']['message'] = exception.message
    error_message['exception']['traceback'] = traceback.format_exc()
    return error_message
