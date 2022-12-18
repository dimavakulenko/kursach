import logging.config

from app.config import config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s::%(asctime)s:%(name)s.%(funcName)s:\n%(message)s\n',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'json': {
            'format': '%(levelname)s::%(asctime)s:%(name)s.%(funcName)s:\n%(message)s\n',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'json_ensure_ascii': False,
        },
    },
    'handlers': {
        'console': {
            'level': config.LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        config.APP_NAME: {
            'level': config.LOG_LEVEL,
            'handlers': (['console']),
        },
    },
}


def init_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
