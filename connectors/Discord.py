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
        # self.connectorCache = {
        #     "heartbeat_interval": 41250,
        #     "session_id":"",
        #     "self":{},
        #     "private_channels":[],
        #     "guilds":[]
        # }

        self.connected = False              # Boolean for handling connection state
        # self.token     = token              # Token used to authenticate api requests
        # self.socket    = None               # Websocket connection handler to Discord

        # self.auth_headers = {"authorization": self.token}

        # Internal threads
        # self.keep_alive_thread = None
        # self.message_consumer_thread = None

        # Events that this connector publishes
        self.core.event.register("connect")
        self.core.event.register("disconnect")
        self.core.event.register("message")
        self.core.event.register("pressence")

    def connect(self):
        # Connect to Discord, post login credentials
        self.logger.info("Attempting connection to Discord servers")

        # Request a WebSocket URL
        # socket_url = self.request("GET", "gateway", headers=self.auth_headers)["url"]

        # self.socket = websocket.create_connection(socket_url)

        # Immediately pass message to server about your connection
        # initData = {
        #     "op": 2,
        #     "d": {
        #         "token": self.token,
        #         "properties": {
        #             "$os": system(),
        #             "$browser":"",
        #             "$device":"Python",
        #             "$referrer":"",
        #             "$referring_domain":""
        #         },
        #     },
        #     "v": 4
        # }
        # self._write_socket(initData)

        # login_data = self._read_socket()
        # self.connectorCache['heartbeat_interval'] = login_data['d']['heartbeat_interval']
        # self.connectorCache['session_id']         = login_data['d']['session_id']
        # self.connectorCache['self']               = login_data['d']['user']
        # self.connectorCache['private_channels']   = login_data['d']['private_channels']
        # self.connectorCache['guilds']             = login_data['d']['guilds']

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

    # def gatherFacts(self):
    #
    #     self.connectorDict['self'] = self.request("GET", "users/@me", headers={"authorization": self.token})
    #     self.connectorDict['direct_messages'] = self.request("GET", "users/@me/channels", headers={"authorization": self.token})
    #     self.connectorDict['guilds'] = self.request("GET", "users/@me/guilds", headers={"authorization": self.token})
    #
    #     print(json.dumps(self.connectorDict))

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
