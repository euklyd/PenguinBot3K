"""
    Class Name : LogManager
    Module Version : 0.1

    Description:
        Provides server-by-server, channel-by-channel logging of messages,
        using the logging stdlib module.

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import logging
import os
from os import path
import time
from datetime import datetime as dt


# class MetaLogger():
#     def __init__(self, logger, date):
#         self.logger = logger
#         self.date = date

class LogManager():
    def __init__(self):
        # self.core = core
        self.logger_map = {}
        # for server in os.listdir():
        #     if (os.path.isdir(server)):
        #         for channel in os.listdir(server):
        #             if (os.path.isdir(channel)):
        #                 logname = "{}_{}".format(
        #                     channel,
        #                     dt.utcnow().strftime("%Y-%m-%d")
        #                 )
        #                 # self.channel_map[channel] = open(logname, 'a')
        #                 self.channel_map[channel] = logging.getLogger(channel)
        #                 log_config = {
        #                     'version': 1,
        #                     'formatters': {
        #                         'verbose': {
        #                             'class':  "logging.Formatter",
        #                             'format': "%(levelname)s %(utctime)s %(module)s %(process)d %(thread)d %(message)s"
        #                         }
        #                         'chatlog': {
        #                             'class':  "logging.Formatter",
        #                             'format': "[{timestamp}] <{username}#{discriminator}> {message}"
        #                         }
        #                     },
        #                     'handlers': {
        #                         'chatlog_file': {
        #                             'class': 'logging.FileHandler',
        #                             'filename': logname,
        #                             'mode': 'a',
        #                             'formatter': 'chatlog',
        #                         }
        #                     },
        #                     'loggers': {
        #                         'chatlog': {
        #                             'handlers': ['chatlog_file']
        #                         }
        #                     }
        #                     # },
        #                     # 'root': {
        #                     #     'level': 'INFO',
        #                     #     'handlers': ['console', 'file', 'errors']
        #                     # }
        #                 }
        #             else:
        #                 pass
        #     else:
        #         pass

    def setup_handler(self, msg):
        formatter = logging.Formatter(
            "[%(asctime)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        formatter.converter = time.gmtime

        if (msg.server is None):
            # this should never happen, I don't care about logging DMs
            log_dir = "logs/private_messages/{channel}".format(
                channel=msg.channel.id
            )
            if (path.isdir(log_dir) is False):
                os.makedirs(log_dir)
            log_file = "{dir}/{date}_{name}.txt".format(
                log_dir,
                date=dt.utcnow().strftime("%Y-%m-%d"),
                name=msg.author.name
            )
        else:
            log_dir = "logs/servers/{server}/{channel}".format(
                server=msg.server.id,
                channel=msg.channel.id
            )
            if (path.isdir(log_dir) is False):
                os.makedirs(log_dir)
            log_file = "{dir}/{date}_{name}.txt".format(
                dir=log_dir,
                date=dt.utcnow().strftime("%Y-%m-%d"),
                name=msg.channel.name
            )
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(formatter)

        return file_handler

    def setup_logger(self, msg):
        logger = logging.getLogger(msg.channel.id)

        # formatter = logging.Formatter(
        #     "[%(asctime)s] %(message)s",
        #     datefmt="%Y-%m-%d %H:%M:%S"
        # )
        # formatter.converter = time.gmtime()
        #
        # if (msg.server is None):
        #     # this should never happen, I don't care about logging DMs
        #     log_file = "logs/private_messages/{channel}/{date}_{name}.txt".format(
        #         channel=msg.channel.id,
        #         date=dt.utcnow().t.strftime("%Y-%m-%d"),
        #         name=msg.author.name
        #     )
        # else:
        #     log_file = "logs/servers/{server}/{channel}/{date}_{name}.txt".format(
        #         server=msg.server.id,
        #         channel=msg.channel.id,
        #         date=dt.utcnow().t.strftime("%Y-%m-%d"),
        #         name=msg.channel.name
        #     )
        # file_handler = logging.FileHandler(log_file, mode='a')
        # file_handler.setFormatter(formatter)

        file_handler = self.setup_handler(msg)

        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        # self.logger_map[msg.channel.id] = logger
        return logger

    def create_logger(self, msg):
        self.logger_map[msg.channel.id] = {
            'logger': self.setup_logger(msg),
            'date': dt.utcnow()
        }

    def update_logger(self, logger_dict, msg):
        file_handler = self.setup_handler(msg)
        logger_dict['logger'].handlers = []
        logger_dict['logger'].addHandler(file_handler)
        logger_dict['date'] = dt.utcnow()

    def log_message(self, msg):
        if (msg.server is None):
            return
        if (self.logger_map.get(msg.channel.id) is None):
            self.create_logger(msg)
        if (dt.utcnow().date() != self.logger_map[msg.channel.id]['date'].date()):
            self.update_logger([msg.channel.id])
        log_message = "<{name}#{discriminator}> {content}".format(
            name=msg.author.name,
            discriminator=msg.author.discriminator,
            content=msg.content
        )

        self.logger_map[msg.channel.id]['logger'].info(log_message)
