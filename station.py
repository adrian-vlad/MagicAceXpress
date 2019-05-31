import logging.config
from logging import getLogger

import config
import officers
from officers.Captain import Agent as Captain


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s (%(process)d) [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'DEBUG',
            "formatter": "standard",
            'class': 'logging.FileHandler',
            'filename': config.LOG_FILE_PATH,
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
})

l = getLogger(__name__)


def main():
    try:
        officers.shift_start()

        Captain(config.station_name_get()).perform()
    except Exception as e:
        l.error(e, exc_info=True)

    try:
        officers.shift_end()
    except Exception as e:
        l.error(e, exc_info=True)

    l.info("Stopped")


if __name__ == "__main__":
    main()
