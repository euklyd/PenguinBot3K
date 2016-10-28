"""
    Class Name : Plugin
    Plugin Version : 2.0

    Description:
        Superclass for which all plugins are derived

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import asyncio
import logging
from core.Database import *

class Plugin(object):
    def __init__(self, core, name):
        # Expose core and plugin name for subclasses
        self.core = core
        self.name = name
        self.database = Database(databaseName="databases/" + self.name + ".db")

        # Expose logger for subclasses
        self.logger = logging.getLogger("plugins." + self.name)
        self.core.plugin.plugin_list[name] = self
        self.logger.info("{}.__init__".format(self.name))

    async def activate(self):
        """
            Summary:
                This method is invoked when a plugin is first loaded

            Args:
                None

            Returns:
                None
        """
        pass

    def deactivate(self):
        """
            Summary:
                This method is invoked when a plugin is disabled.
                Should be any nessessary garbage collection

            Args:
                None

            Returns:
                None
        """
        pass

    # Exposed methods for Plugin use:

    async def send_reply(self, message, message_str):
        """
            Summary:
                Directed wrapper method calling the discord.Client's
                send_message method.
                Will send a message in channel that is directed at
                the user who invoked the command.

            Args:
                message (Message): Message object to reply to.
                message_str (str): String form of message to send to channel

            Returns:
                None
        """
        self.logger.info("Plugin.send_reply invoked")
        await self.core.send_message(
            message.channel, "<@!{}>: {}".format(message.author.id, message_str)
        )
    async def send_message(self, destination, message_str):
        """
            Summary:
                Wrapper method calling the discord.Client's send_message method.
                Sends a message to a channel

            Args:
                destination (Channel, Server, or PrivateChannel):
                                    Object to send message to
                message_str (str):  String form of message to send to channel

            Returns:
                None
        """
        self.logger.info("Plugin.send_message invoked")
        await self.core.send_message(destination, message_str)

    async def send_whisper(self, user, message_str):
        """
            Summary:
                Wrapper method calling the connection's whisper method.
                Will send a private message that only the recipent can see.

            Args:
                user (User): User object of the intended recipent
                message_str (str): String form of message to send to channel

            Returns:
                None
        """
        await self.core.send_message(user, message_str)

    async def delete_message(self, msg):
        """
            Summary:
                Wrapper method calling the connection's delete_message method.
                Will delete the message object passed as arguments.

            Args:
                msg (Message): Message object describing message to delete.

            Returns:
                None
        """
        await self.core.delete_message(msg)

    async def send_file(self, destination, filepath, filename=None,
                        content=None, tts=False):
        """
            Summary:
                Wrapper method calling the discord.Client's send_file method
                Uploads a file to a channel

            Args:
                destination (Channel, Server, or PrivateChannel):
                                Object to send file to
                filepath (str): Path of file to upload
                filename (str): Name of file. Defaults to filepath.name.
                tts (bool):     If the file should be sent text-to-speech.

            Returns:
                None
        """
        await self.core.send_file(destination, filepath, filename=filename,
                       content=content, tts=tts)

    async def get_user_info(self, user_id):
        """
            Summary:
                Wrapper method calling the discord.Client's get_user_info method
                Gets info about a user

            Args:
                user_id (str): ID of user to get info about.

            Returns:
                discord.User object
        """
        return await self.core.get_user_info(user_id)


# def reply(self, envelope, message):
#     """
#         Summary:
#             Wrapper method calling the connection's reply method
#             Will send a message in channel that is directed at the user who invoked the command
#
#         Args:
#             envelope (tuple): An object containing information about the sender and channel it came from
#             message (str): String form of message to send to channel
#
#         Returns:
#             None
#     """
#     self.core.connection.reply(envelope.sender, envelope.channel, message)
#
# def say(self, channel, message, mentions=[]):
#     """
#         Summary:
#             Wrapper method calling the connection's send method
#             Sends a message to a channel
#
#         Args:
#             channel (str): Channel id to send message to
#             message (str): String form of message to send to channel
#             mentions (list): List of users to mention in a channel
#
#         Returns:
#             None
#     """
#     self.logger.info("Plugin.say invoked")
#     self.core.connection.say(channel, message, mentions=mentions)
#
# def whisper(self, user, message):
#     """
#         Summary:
#             Wrapper method calling the connection's whisper method
#             Will send a private message that only the recipent can see
#
#         Args:
#             user (str): UserId of the intended recipent
#             message (str): String form of message to send to channel
#
#         Returns:
#             None
#     """
#     self.core.connection.whisper(user, message)
#
# def delete_message(self, msg):
#     """
#         Summary:
#             Wrapper method calling the connection's delete_message method
#             Will delete the message object passed as arguments
#
#         Args:
#             msg (Message): Message object describing message to delete.
#
#         Returns:
#             None
#     """
#     self.core.connection.delete_message(msg)
# def upload(self, channel, file):
#     """
#         Summary:
#             Wrapper method calling the connection's upload method
#             Uploads a file to a channel
#
#         Args:
#             channel (str): Channel id to send message to
#             file (str): Path of file to upload
#
#         Returns:
#             None
#     """
#     self.core.connection.upload(channel, file)
