"""
    Class Name : Discord Connector

    Description:
        Provides functionality for connecting to Discord chat server
        This class is a subclass of core/Connector.py and implements the
            required methods so the rest of the bot can talk to Discord

    Contributors:
        - Patrick Hennessy
        - Aleksandr Tihomirov
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from platform import system
from ssl import *

import asyncio
import base64
import discord
import json
import logging
import threading
import time
import websocket

from core.Connector import Connector
from core.Decorators import ttl_cache


class Discord(Connector):
    def __init__(self, core, token):
        super(Discord, self).__init__()
        self.core   = core
        self.logger = logging.getLogger("connector." + __name__)
        self.name   = __name__

        # Authentication / Connection Data
        self.connectorCache = {
            "heartbeat_interval": 41250,
            "session_id":"",
            "self":{},
            "private_channels":[],
            "guilds":[]
        }

        self.connected = False              # Boolean for handling connection state
        self.token     = token              # Token used to authenticate api requests
        self.socket    = None               # Websocket connection handler to Discord

        self.auth_headers = {"authorization": self.token}

        # Internal threads
        self.keep_alive_thread = None
        self.message_consumer_thread = None

        # Events that this connector publishes
        self.core.event.register("connect")
        self.core.event.register("disconnect")
        self.core.event.register("message")
        self.core.event.register("pressence")

    def connect(self):
        # Connect to Discord, post login credentials
        self.logger.info("Attempting connection to Discord servers")

        # Request a WebSocket URL
        socket_url = self.request("GET", "gateway", headers=self.auth_headers)["url"]

        self.socket = websocket.create_connection(socket_url)

        # Immediately pass message to server about your connection
        initData = {
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": system(),
                    "$browser":"",
                    "$device":"Python",
                    "$referrer":"",
                    "$referring_domain":""
                },
            },
            "v": 4
        }
        self._write_socket(initData)

        login_data = self._read_socket()
        self.connectorCache['heartbeat_interval'] = login_data['d']['heartbeat_interval']
        self.connectorCache['session_id']         = login_data['d']['session_id']
        self.connectorCache['self']               = login_data['d']['user']
        self.connectorCache['private_channels']   = login_data['d']['private_channels']
        self.connectorCache['guilds']             = login_data['d']['guilds']

        self.connected = True

        self.logger.info("Succesful login to Discord")
        self.core.event.notify('connect')

    def disconnect(self):
        self.core.event.notify('disconnect')
        self.connected = False

        self.logger.debug('Joined message_consumer and keep_alive threads')

        self.logger.info("Disconnected from Discord")

    def get_messages(self, channel, limit, before=None):
        """
            Summary:
                Replies to a user in a channel.

            Args:
                channel (Channel): The Channel object to post to.
                limit (int): The quantity of messages to retrieve.
            Optional:
                before (Message): The Message object to start at.
        """
        self.logger.debug("Getting the messages from CID: {}".format(channel.id))

        endpoint = "channels/{}/messages".format(channel.id)
        data     = {
            'limit': int(limit)
        }
        if (before is not None):
            data['before'] = before.id

        self.logger.info(data)
        self.logger.info(endpoint)

        try:
            raw_messages = self.request("GET", endpoint, data=data, headers=self.auth_headers)
            # self.logger.info("raw:\n{}".format(raw_messages))
            messages = []
            for raw_message in raw_messages:
                messages.append(self._parse_discord_message(raw_message))
            # self.logger.info("snowflake:\n{}".format(messages))
            return messages
        except:
            self.logger.warning('Retrieval of messages in CID \'{}\' failed'.format(channel.id))

    # def delete_message(self, msg):
    #     self.logger.debug("Deleting message with ID: {} from channel: {}".format(msg.id, msg.channel))
    #
    #     endpoint = "channels/{0}/messages/{1}".format(msg.channel, msg.id)
    #     try:
    #         self.request("DELETE", endpoint, headers=self.auth_headers)
    #     except:
    #         self.logger.warning('Deletion of message \'{}\' in channel \'{}\' failed'.format(msg.id, msg.channel))
    #
    # def delete_messages(self, msg_array):
    #     self.logger.debug("Bulk deleting {} messages from channel: {}".format(len(msg_array), msg_array[0].channel))
    #
    #     endpoint = "channels/{0}/messages/bulk-delete".format(msg_array[0].channel)
    #     data     = {
    #         'messages': []
    #     }
    #     for msg in msg_array:
    #         data['messages'].append(msg.message['id'])
    #     # self.logger.info(data)
    #     # self.logger.info(endpoint)
    #     try:
    #         self.request("POST", endpoint, data=data, headers=self.auth_headers)
    #     except:
    #         self.logger.warning('Deletion of message \'{}\' in channel \'{}\' failed'.format(msg.id, msg.channel))

    # def ban_user(self, server_id, user_id, delete_msgs=0):
    #     self.logger.info("Banning user `{}` from server `{}`".format(user_id, server_id))
    #
    #     endpoint = "guilds/{0}/bans/{1}".format(server_id, user_id)
    #     data     = {
    #         "delete-message-days": delete_msgs
    #     }
    #     self.logger.debug(endpoint)
    #     self.logger.debug(data)
    #
    #     try:
    #         self.request("PUT", endpoint, data=data, headers=self.auth_headers)
    #     except:
    #         self.logger.warning('Ban of user \'{}\' in server \'{}\' failed'.format(user_id, server_id))

    # def whisper(self, user, message):
    #     self.logger.debug("Sending reply to " + user)
    #
    #     channel = self.get_private_channel(user)
    #     endpoint = "channels/{}/messages".format(channel)
    #     data     = {
    #         "content": "{}".format(message)
    #     }
    #
    #     try:
    #         self.request("POST", endpoint, data=data, headers=self.auth_headers)
    #     except:
    #         self.logger.warning('Reply to user \'{}\' in channel \'{}\' failed'.format(user, channel))

    # def upload(self, channel, file):
    #     self.logger.debug('Sending file to channel ' + channel)
    #
    #     endpoint = "channels/{}/messages".format(channel)
    #     files    = {'file': open(file, 'rb')}
    #
    #     try:
    #         self.request('POST', endpoint,  files=files, headers={"authorization": self.token})
    #     except:
    #         self.logger.warning('Upload file \'{}\' to channel {} failed'.format(file, channel))

    # def getUsers(self):
    #     pass
    #
    # @ttl_cache(300)
    # def getUser(self, userID):
    #     user = self.request("GET", "users/{}".format(userID), headers={"authorization": self.token})
    #
    #     return {
    #         'user': user,
    #         'name': user['username'],
    #         'id': user['id'],
    #         'expires': time.time() + 600
    #     }

    # def get_channel(self, msg):
    #     channel = self.request("GET", "channels/{}".format(msg.channel), headers={"authorization": self.token})
    #     return channel
    #
    # def get_server(self, msg):
    #     channel = self.get_channel(msg)
    #     server = self.request("GET", "guilds/{}".format(channel['guild_id']), headers={"authorization": self.token})
    #     return server

    # Discord Specific
    # def leave_guild(self, guild_id):
    #     self.request("DELETE", "users/@me/guilds/{}".format(guild_id), headers={"authorization": self.token})
    #
    # def get_servers(self):
    #     return self.request("GET", "users/@me/guilds", headers={"authorization": self.token})
    #
    # def get_private_channel(self, user):
    #     for channel in self.connectorCache['private_channels']:
    #         if channel['recipient']['id'] == user:
    #             return channel['id']
    #     else:
    #         channel = self.request("POST", "users/@me/channels", data={"recipient_id": "{}".format(user)}, headers={"authorization": self.token})
    #         self.connectorCache['private_channels'].append(channel)
    #         return channel['id']

    # def set_status(self, status):
    #     self._write_socket({
    #         "op":3,
    #         "d":{
    #             "idle_since":None,
    #             "game": {
    #                 "name": status
    #             }
    #         }
    #     })

    # User Management
        # Set roles
        # Ban
        # Sync Roles
    # Channel Management
        # Add / remove Channel
        # Apply premissions to Channel

    def gatherFacts(self):

        self.connectorDict['self'] = self.request("GET", "users/@me", headers={"authorization": self.token})
        self.connectorDict['direct_messages'] = self.request("GET", "users/@me/channels", headers={"authorization": self.token})
        self.connectorDict['guilds'] = self.request("GET", "users/@me/guilds", headers={"authorization": self.token})

        print(json.dumps(self.connectorDict))

    # def avatar(self):
    #     with open("conf/avatar.png", "rb") as avatarImage:
    #         rawImage = avatarImage.read()
    #
    #     raw = base64.b64encode(rawImage)
    #     with open("test", "wb") as file:
    #         file.write(raw)
    #
    #     return
    #
    #     self.request("PATCH", "users/@me", data={"username": "Arcbot", "avatar": "data:image/png;base64," + base64.b64encode(rawImage).decode('ascii')}, headers={"authorization": self.token})

    # Handler Methods
    async def _handleMessage(self, message):
        self.logger.debug(message.type)
        # If incoming message is a MESSAGE text
        if message.type == discord.MessageType.default:
            self.core.event.notify("message",  message=message)
            await self.core.command.check(message)

        # If incoming message is PRESSENCE update
        elif type == discord.MessageType.PRESSENCE:
            self.core.event.notify("pressence", message=message)

        # should check for other message types?
