import sys
import traceback

from .logger import get_logger, LogLevel


def register_uncaught_exception_handler():
    log = get_logger('Exception logger')

    def log_uncaught_exception(exctype, value, tb):
        trace = "\t".join(traceback.format_tb(tb))
        log_message = f'Uncaught exception: {exctype}\nValue: {value}\nTraceback: \n\t{trace}\n\n'

        log(log_message, LogLevel.ERROR)
        log.flush()

    sys.excepthook = log_uncaught_exception
