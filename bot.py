"""
    Class Name : Main

    Description:
        Entry point for loading Arcbot

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

# from core.Core import Bot
from core.Penguin import PenguinBot
import logging
import time
import sys

logger = logging.getLogger(__name__)

def main():
    try:
        # bot = Bot()
        bot = PenguinBot()
        bot.login()
        # bot.watchdog.start()
        bot.run()

    except KeyboardInterrupt:
        logger.info("Caught SIGINT from keyboard. Exiting")
        bot.exit()
        logger.debug(u"\U0001F60E I'll be back \U0001F60E")
        sys.exit(0)
    except:
        logger.info("Caught error. Exiting")
        bot.exit()
        sys.exit(1)

if __name__ == '__main__':
    main()
