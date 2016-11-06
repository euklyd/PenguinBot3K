"""
    Class Name : LogManager
    Module Version : 0.2.0

    Description:
        Provides server-by-server, channel-by-channel logging of messages,
        using the logging stdlib module.
        Information about where logging folders and files are is stored in
        databases/servers.json and databases/channels.json

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import json
import logging
import os
from os import path
import shutil
import time
from datetime import datetime as dt


class LogManager():
    def __init__(self, core):
        self.logger_map = {}
        self.server_map = {}
        self.channel_map = {}
        self.core = core
        """
        Structure of servers.json and channels.json will look like this:
        """
        """
        {
            <server.id>: {
                'name': server.name
            }

            ...
        }
        """
        """
        {
            <channel.id>: {
                'name': channel.name
                'server_id': server.id (of parent); should never change
                'server_name': server.name (of parent)
            }

            ...
        }
        """
    def update_info(self):
        try:
            server_fp = open("databases/servers.json", 'r')
            self.server_map = json.load(server_fp)
        except FileNotFoundError:
            server_fp = open("databases/servers.json", 'w')
            server_fp.write("None")
            server_fp.close()
        try:
            channel_fp = open("databases/channels.json", 'r')
            self.channel_map = json.load(channel_fp)
        except FileNotFoundError:
            channel_fp = open("databases/channels.json", 'w')
            channel_fp.write("None")
            channel_fp.close()
        self.init_log_tree()

    def init_log_tree(self):
        self.core.logger.info("Initializing chatlog tree.")
        self.core.logger.debug("Servers: {}".format(self.core.servers))
        self.core.logger.debug("Channels: {}".format(self.core.get_all_channels()))
        for server in self.core.servers:
            self.core.logger.info(server.name)
            self.update_server_map(server)

        for server in self.core.servers:
            for channel in server.channels:
                self.core.logger.info(channel.name)
                self.update_channel_map(channel)

        self.update_jsons(smod=True, cmod=True)

    def update_server_map(self, server):
        if (self.server_map.get(server.id) is None):
            self.server_map[server.id] = {
                'name': server.name
            }
        if (server.name != self.server_map[server.id]['name']):
            """update filetree here"""
            # os.rename(
            # for log in os.listdir("logs/servers/{oldname}-{srv_id}".format(
            #     oldname=self.server_map[server.id]['name'],
            #     srv_id=server.id
            # )):
            #     self.core.logger.info(log)
            #     shutil.move(
            #         log,
            #         "logs/servers/{newname}-{srv_id}".format(
            #             newname=server.name,
            #             srv_id=server.id
            #         )
            #     )

            shutil.move(
                "logs/servers/{oldname}-{srv_id}".format(
                    oldname=self.server_map[server.id]['name'],
                    srv_id=server.id
                ),
                "logs/servers/{newname}-{srv_id}".format(
                    newname=server.name,
                    srv_id=server.id
                )
            )
            """update server here"""
            self.server_map[server.id]['name'] = server.name

    def update_channel_map(self, channel):
        if (self.channel_map.get(channel.id) is None):
            self.channel_map[channel.id] = {
                'name': channel.name,
                'server_id': channel.server.id,
                'server_name': channel.server.name
            }
        if (channel.name != self.channel_map[channel.id]['name']):
            old_channel = self.channel_map[channel.id]
            """update filetree here"""
            for log in os.listdir(
                "logs/servers/{old_server}-{srv_id}/{old_channel}-{ch_id}".format(
                    old_server=old_channel['server_name'],
                    srv_id=old_channel['server_id'],
                    old_channel=old_channel['name'],
                    ch_id=channel.id
                )
            ):
                shutil.move(
                    "logs/servers/{old_server}-{srv_id}/{old_channel}-{ch_id}/{log}".format(
                        old_server=old_channel['server_name'],
                        srv_id=old_channel['server_id'],
                        old_channel=old_channel['name'],
                        ch_id=channel.id,
                        log=log
                    ),
                    "logs/servers/{new_server}-{srv_id}/{new_channel}-{ch_id}".format(
                        new_server=self.server_map[old_channel['server_id']]['name'],
                        srv_id=channel.server.id,
                        new_channel=channel.name,
                        ch_id=channel.id
                    )
                )
            os.rmdir(
                "logs/servers/{old_server}-{srv_id}/{old_channel}-{ch_id}".format(
                    old_server=old_channel['server_name'],
                    srv_id=old_channel['server_id'],
                    old_channel=old_channel['name'],
                    ch_id=channel.id
                )
            )
            # os.rename(
            # shutil.move(
            #     "logs/servers/{old_server}-{srv_id}/{old_channel}-{ch_id}".format(
            #         old_server=old_channel['server_name'],
            #         srv_id=old_channel['server_id'],
            #         old_channel=old_channel['name'],
            #         ch_id=channel.id
            #     ),
            #     "logs/servers/{new_server}-{srv_id}/{new_channel}-{ch_id}".format(
            #         new_server=self.server_map[old_channel['server_id']]['name'],
            #         srv_id=channel.server.id,
            #         new_channel=channel.name,
            #         ch_id=channel.id
            #     )
            # )
            """update channel here"""
            self.channel_map[channel.id]['name'] = channel.name
            self.channel_map[channel.id]['server_name'] = self.server_map[old_channel['server_id']]['name']

    def update_jsons(self, smod=False, cmod=False):
        if (smod is True):
            server_fp = open("databases/servers.json", 'w')
            json.dump(self.server_map, server_fp)
        if (cmod is True):
            channel_fp = open("databases/channels.json", 'w')
            json.dump(self.channel_map, channel_fp)

    def update_channel(self, after):
        if (self.channel_map[after.id]['name'] != after.name):
            # 1) log message to logfile
            if (after.server is not None and self.logger_map.get(after.id) is not None):
                log_string = "<{name}#{discriminator}> {content}".format(
                    name="System",
                    discriminator="0000",
                    content="Channel name changed from #{oldname} to #{newname}.".format(
                        oldname=self.channel_map[after.id]['name'],
                        newname=after.name
                    )
                )
                self.logger_map[after.id]['logger'].info(log_string)
            # 2) change logger handler
                self.update_logger(after)
            # 3) update channel_map
            self.update_channel_map(after)
            self.update_jsons(cmod=True)
        else:
            pass

    def setup_handler(self, channel):
        formatter = logging.Formatter(
            "[%(asctime)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S %Z"
        )
        formatter.converter = time.gmtime

        # if (msg.server is None):
        #     # This should never happen, I don't care about logging DMs
        #     log_dir = "logs/private_messages/{channel}".format(
        #         # channel=msg.channel.id
        #         channel=msg.channel.name
        #     )
        #     if (path.isdir(log_dir) is False):
        #         os.makedirs(log_dir)
        #     log_file = "{dir}/{date}_{name}.txt".format(
        #         dir=log_dir,
        #         date=dt.utcnow().strftime("%Y-%m-%d"),
        #         name=msg.author.name
        #     )
        #
        #     self.update_maps(msg, log_dir) ##FIX
        # else:
        #     log_dir = "logs/servers/{server}/{channel}".format(
        #         server=server.id,
        #         channel=channel.id
        #     )
        #     if (path.isdir(log_dir) is False):
        #         os.makedirs(log_dir)
        #     log_file = "{dir}/{date}_{name}.txt".format(
        #         dir=log_dir,
        #         date=dt.utcnow().strftime("%Y-%m-%d"),
        #         name=channel.name
        #     )
        log_dir = "logs/servers/{server}-{srv_id}/{channel}-{ch_id}".format(
            # server=channel.server.id,
            # channel=channel.id
            server=channel.server.name,
            srv_id=channel.server.id,
            channel=channel.name,
            ch_id=channel.id
        )
        if (path.isdir(log_dir) is False):
            os.makedirs(log_dir)
        log_file = "{dir}/{date}_{name}.txt".format(
            dir=log_dir,
            date=dt.utcnow().strftime("%Y-%m-%d"),
            name=channel.name
        )
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(formatter)

        return file_handler

    def setup_logger(self, channel):
        logger = logging.getLogger(channel.id)

        file_handler = self.setup_handler(channel)

        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.propagate = False

        return logger

    def create_logger(self, channel):
        self.logger_map[channel.id] = {
            'logger': self.setup_logger(channel),
            'date': dt.utcnow()
        }

    # def update_logger(self, msg):
    #     file_handler = self.setup_handler(msg)
    #     self.logger_map[msg.channel.id]['logger'].handlers = []
    #     self.logger_map[msg.channel.id]['logger'].addHandler(file_handler)
    #     self.logger_map[msg.channel.id]['date'] = dt.utcnow()
    def update_logger(self, channel):
        file_handler = self.setup_handler(channel)
        self.logger_map[channel.id]['logger'].handlers = []
        self.logger_map[channel.id]['logger'].addHandler(file_handler)
        self.logger_map[channel.id]['date'] = dt.utcnow()

    def log_message(self, msg):
        if (msg.server is None):
            return
        if (self.logger_map.get(msg.channel.id) is None):
            self.create_logger(msg.channel)
        if (dt.utcnow().date() != self.logger_map[msg.channel.id]['date'].date()):
            # self.update_logger(msg) ##
            self.update_channel(msg.channel)
        log_string = "<{name}#{discriminator}> {content}".format(
            name=msg.author.name,
            discriminator=msg.author.discriminator,
            content=msg.content
        )

        self.logger_map[msg.channel.id]['logger'].info(log_string)
