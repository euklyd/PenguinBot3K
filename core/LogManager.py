"""
    Class Name : LogManager
    Module Version : 1.0.1

    Description:
        Provides server-by-server, channel-by-channel logging of messages,
        using the logging stdlib module.
        Information about where logging folders and files are is stored in
        databases/servers.json and databases/channels.json
        Does not handle info, warning, or debug messages for the bot itself.

        Structure of self.channel_map and self.server_map (and their
        corresponding JSON files) can be found in LogManager.md

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
        self.logger = logging.getLogger(__name__)

    def close(self):
        for logger in self.logger_map:
            logger.info(self.format_system(
                content="Logger closed at {name} shutdown.".format(
                    name=self.core.config.username
                )
            ))

    def update_info(self):
        """
            Summary:
                Initializes self.channel_map and self.server_map to
                their last known state, and updates to their latest
                unknown information.

            Args:
                None

            Returns:
                None
        """
        try:
            server_fp = open("databases/servers.json", 'r')
            self.server_map = json.load(server_fp)
        except FileNotFoundError:
            # Create a blank file if doesn't exist.
            server_fp = open("databases/servers.json", 'w')
            server_fp.write("None")
            server_fp.close()
        try:
            channel_fp = open("databases/channels.json", 'r')
            self.channel_map = json.load(channel_fp)
        except FileNotFoundError:
            # Create a blank file if doesn't exist.
            channel_fp = open("databases/channels.json", 'w')
            channel_fp.write("None")
            channel_fp.close()
        self.init_log_tree()

    def init_log_tree(self):
        """
            Summary:
                For all channels and servers the bot is connected to,
                update the info about them to their current states.
                If a new server or channel has been added, then add those
                to the maps and filetree as appropriate.
                Finally, write the new dictionaries to disk.

            Args:
                None

            Returns:
                None
        """
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
        """
            Summary:
                Update the server map if a server has been modified
                or created. If modified, then moves and renames
                directories as appropriate.

            Args:
                server (discord.Server):
                    The server whose entry in self.server_map is
                    to be updated.

            Returns:
                None
        """
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
        """
            Summary:
                Update the channel map if a channel has been modified
                or created. If modified, then moves and renames log files
                and directories as appropriate.

            Args:
                channel (discord.Channel):
                    The channel whose entry in self.channel_map is
                    to be updated .

            Returns:
                None
        """
        if (self.channel_map.get(channel.id) is None):
            # Create an entry for an unknown channel
            self.channel_map[channel.id] = {
                'name': channel.name,
                'server_id': channel.server.id,
                'server_name': channel.server.name
            }
        if (channel.name != self.channel_map[channel.id]['name']):
            # If the channel's name has changed, update the stored filename
            # and move the channel's log directory.
            old_channel = self.channel_map[channel.id]
            # """update filetree here"""
            for log in os.listdir(
                "logs/servers/{old_server}-{srv_id}/{old_channel}-{ch_id}".format(
                    old_server=old_channel['server_name'],
                    srv_id=old_channel['server_id'],
                    old_channel=old_channel['name'],
                    ch_id=channel.id
                )
            ):
                # Move the logs to the new directory.
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
            # Delete the old directory.
            os.rmdir(
                "logs/servers/{old_server}-{srv_id}/{old_channel}-{ch_id}".format(
                    old_server=old_channel['server_name'],
                    srv_id=old_channel['server_id'],
                    old_channel=old_channel['name'],
                    ch_id=channel.id
                )
            )

            # Update channel map.
            # """update channel here"""
            self.channel_map[channel.id]['name'] = channel.name
            self.channel_map[channel.id]['server_name'] = self.server_map[old_channel['server_id']]['name']

    def update_jsons(self, smod=False, cmod=False):
        """
            Summary:
                Writes self.server_map and/or self.channel_map to their
                config files.

            Args:
                cmod (bool): Update the channels config?
                smod (bool): Update the servers config?

            Returns:
                None
        """
        if (smod is True):
            server_fp = open("databases/servers.json", 'w')
            json.dump(self.server_map, server_fp)
        if (cmod is True):
            channel_fp = open("databases/channels.json", 'w')
            json.dump(self.channel_map, channel_fp)

    def update_channel(self, after):
        """
            Summary:
                Updates everything corresponding to the specified channel.
                This includes:
                1)  If the name has changed, log a message reflecting that to
                    the old output file.
                2)  Update the logger in self.logger_map
                3)  Update the channel map and log the new one to the
                    config file.

            Args:
                after (Discord.channel):
                    The new Channel object that things need to be updated
                    to match.

            Returns:
                None
        """
        if (self.channel_map[after.id]['name'] != after.name):
            # 1) log message to logfile
            if (after.server is not None and self.logger_map.get(after.id) is not None):
                self.logger_map[after.id]['logger'].info(self.format_system(
                    name="System", discriminator="0000",
                    content="Channel name changed from #{oldname} to #{newname}.".format(
                        oldname=self.channel_map[after.id]['name'],
                        newname=after.name
                    ))
                )
            # 2) change logger handler
                self.update_logger(after)
            # 3) update channel_map
            self.update_channel_map(after)
            self.update_jsons(cmod=True)
        else:
            pass

    def setup_handler(self, channel):
        """
            Summary:
                Returns a logger handler configured to the specified channel.

            Args:
                channel (Discord.channel):
                    The Channel object corresponding to the handler that
                    is to be configured.

            Returns:
                (logging.Handler):  A configured handler.
        """
        formatter = logging.Formatter(
            "[%(asctime)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S %Z"
        )
        formatter.converter = time.gmtime

        log_dir = "logs/servers/{server}-{srv_id}/{channel}-{ch_id}".format(
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
        """
            Summary:
                Returns a logger configured to the specified channel.

            Args:
                channel (Discord.channel):
                    The Channel object corresponding to the logger that
                    is to be configured.

            Returns:
                (logging.Logger):   A configured logger.
        """
        logger = logging.getLogger(channel.id)

        file_handler = self.setup_handler(channel)

        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.propagate = False

        return logger

    def create_logger(self, channel):
        """
            Summary:
                Creates a logger for the specified channel and adds it
                to self.logger_map

            Args:
                channel (Discord.channel):
                    The Channel object corresponding to the logger that
                    is to be created.

            Returns:
                None
        """
        self.logger.info("Creating logger for {name} CID: {id}".format(
            name=channel.name,
            id=channel.id
        ))
        self.logger_map[channel.id] = {
            'logger': self.setup_logger(channel),
            'date': dt.utcnow()
        }

    def update_logger(self, channel):
        """
            Summary:
                Updates the logger for the specified channel.

            Args:
                channel (Discord.channel):
                    The Channel object corresponding to the logger that
                    is to be updated.

            Returns:
                None
        """
        file_handler = self.setup_handler(channel)
        self.logger_map[channel.id]['logger'].handlers = []
        self.logger_map[channel.id]['logger'].addHandler(file_handler)
        self.logger_map[channel.id]['date'] = dt.utcnow()

    def log_message(self, msg):
        """
            Summary:
                Logs a message to the corresponding output file.

            Args:
                msg (discord.Message):  The Message object to be logged.

            Returns:
                None
        """
        self.logger.info(
            "Message Recieved: [Name:{}][UID:{}][CID:{}][CName:{}]: {}".format(
                msg.author.name,
                msg.author.id,
                msg.channel.id,
                msg.channel.name,
                msg.content
            )
        )
        if (msg.server is None):
            # Discard private messages.
            return
        if (self.logger_map.get(msg.channel.id) is None):
            # If a logger isn't open for that channel yet, create one.
            self.create_logger(msg.channel)
        self.logger.debug(
            "\n\tdate: {utcdate}\n\tlogger['{cid}']['date']: {logdate}".format(
                utcdate=dt.utcnow().date(),
                cid=msg.channel.id,
                logdate=self.logger_map[msg.channel.id]['date'].date()
            )
        )
        if (dt.utcnow().date() != self.logger_map[msg.channel.id]['date'].date()):
            # If it's not the same day as when the logger was created, open
            # a new log file.
            self.logger.info("Updating with new date")
            # self.update_channel(msg.channel)
            self.update_logger(msg.channel)
        self.logger_map[msg.channel.id]['logger'].info(self.format_message(msg))
        self.logger.info("Message logged")

    def format_message(self, msg):
        """
            Summary:
                Formats a Message object into a log message string.
                Format is
                    "<name#discriminator> content",
                e.g.,
                    "<euklyd#1234> This is an example message."
                (quotes not included). This is then fed to a logger object,
                so the line in the file will look something like
                    [2016-11-10 04:14:09 GMT] <euklyd#1234> This is an example message.

            Args:
                msg (discord.Message):  The message which is to be logged.

            Returns:
                (str):  The formatted message string.
        """
        log_string = "<{name}#{discriminator}> {content}".format(
            name=msg.author.name,
            discriminator=msg.author.discriminator,
            content=msg.content
        )
        return log_string

    def format_system(self, name="System", discriminator="0000", content="<null>"):
        """
            Summary:
                Like `format_message(msg)`, but it takes up to three str
                rather than a single discord.Message.
                The default is to output a sytem message for events such
                as the channel name changing, but one can customize the
                name and discriminator if desired.

            Args:
                name (str):             Username.
                discriminator (str):    4-digit discriminator.
                content (str):          The content of the message itself.

            Returns:
                (str):  The formatted message string.
        """
        log_string = "<{name}#{discriminator}> {content}".format(
            name=name,
            discriminator=discriminator,
            content=content
        )
        return log_string
