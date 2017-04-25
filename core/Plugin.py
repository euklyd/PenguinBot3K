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
import discord
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
        # self.core.plugin.plugin_list[name] = self
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

    async def deactivate(self):
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

    async def send_reply(self, message, message_str=None, embed=None):
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
        sent = await self.core.send_message(
            message.channel, "<@!{}>: {}".format(
                message.author.id, message_str, embed=embed)
        )
        return sent

    async def send_message(self, destination, message_str=None, embed=None):
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
        sent = await self.core.send_message(
            destination, message_str, embed=embed
        )
        return sent

    async def send_whisper(self, user, message_str=None, embed=None):
        """
            Summary:
                Wrapper method calling the discord.Client's send_message method.
                Will send a private message that only the recipent can see.

            Args:
                user (User): User object of the intended recipent
                message_str (str): String form of message to send to channel

            Returns:
                None
        """
        sent = await self.core.send_message(user, message_str, embed=embed)
        return sent

    async def get_messages(self, channel, limit, before=None):
        """
            Summary:
                Wrapper method calling the discord.Client's logs_from method.
                Retrieves some number of messages from a channel.

            Args:
                channel (Channel): Channel object to read messages from
                limit (int): Number of messages to Retrieves
                before (Message): Message to start reading from (exclusive)

            Returns:
                None
        """
        # msg_iterator = await self.core.logs_from(channel, limit, before=before)
        msg_list = []
        async for message in self.core.logs_from(channel, int(limit), before=before):
            msg_list.append(message)
        return msg_list

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
        self.logger.info(
            "deleting [ID:{msg_id}][User:{uname}]: {content}".format(
                msg_id=msg.id, uname=msg.author.name, content=msg.content)
        )
        deleted = await self.core.delete_message(msg)
        return deleted

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
        if (type(destination) == discord.Channel):
            self.logger.info("Sending {file} to {channel} (CID: {cid})".format(
                    file=filename,
                    channel=destination.name,
                    cid=destination.id
            ))
        elif (type(destination) == discord.User):
            self.logger.info(
                "Sending {file} to {user}#{discriminator} (UID: {uid})".format(
                    file=filename,
                    user=destination.name,
                    discriminator=destination.discriminator,
                    uid=destination.id
                )
            )
        sent = await self.core.send_file(destination, filepath,
                                         filename=filename,
                                         content=content, tts=tts)
        return sent

    async def add_reaction(self, msg, emoji):
        """
            Wrapper for discord.Client.add_reaction()
            emoji can be a string or discord.Emoji
        """
        self.logger.info("Plugin.add_reaction invoked")
        await self.core.add_reaction(msg, emoji)
        return msg

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

    def get_role_info(self, role_id, server):
        """
            Summary:
                Gets info about a role for a specific server

            Args:
                role_id (str): ID of role to get info about.
                server (discord.Server): Server on which role resides

            Returns:
                discord.Role object
        """
        role = None
        for r in server.roles:
            if (r.id == role_id):
                role = r
                break
            pass
        return role

    async def ban_user(self, user, server, delete_message_days=0):
        """
            Summary:
                Bans any User from a server, bypassing discord.py's requirement
                that it be a discord.Member
        """
        await self.core.http.ban(user.id, server.id, delete_message_days)
