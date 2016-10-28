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
# from core.Message import *
# from core.Loop import Loop

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

        # Set websocket to nonblocking so we can exit a thread reading from the socket if we need to
        self.socket.sock.setblocking(0)
        self.connected = True

        self.logger.info("Succesful login to Discord")
        self.core.event.notify('connect')

        # Create and start threads
        # self.keep_alive_thread = threading.Thread(target=self._keep_alive, name="keep_alive_thread")
        # self.keep_alive_thread.daemon = True
        # self.keep_alive_thread.start()
        #
        # self.message_consumer_thread = threading.Thread(target=self._message_consumer, name="message_consumer_thread")
        # self.message_consumer_thread.daemon = True
        # self.message_consumer_thread.start()

        # self.loop = Loop()
        # self.loop.start

    def disconnect(self):
        self.core.event.notify('disconnect')
        self.connected = False

        # Join threads if they exist
        # if isinstance(self.keep_alive_thread, threading.Thread):
        #     self.keep_alive_thread.join()
        #
        # if isinstance(self.message_consumer_thread, threading.Thread):
        #     self.message_consumer_thread.join()

        self.logger.debug('Joined message_consumer and keep_alive threads')

        # Close websocket if it is established
        if isinstance(self.socket, websocket.WebSocket):
            self.socket.close()

        self.logger.info("Disconnected from Discord")

    def say(self, channel, msg, mentions=[]):
        """
            Summary:
                Posts a message to a channel.

            Args:
                channel (Channel): The Channel object to post to.
                msg (str): The message to post.
                mentions (list[str]): The list of user ids to mention.
        """
        self.logger.debug("Sending message to channel " + channel.id)

        for user in mentions:
            message = "<@{}> ".format(user) + msg

        endpoint = "channels/{}/messages".format(channel.id)
        data     = {
            "content":  u"\u200B{}".format(msg),    # zero-width space to potential triggers
            "mentions": mentions
        }

        try:
            self.request("POST", endpoint, data=data, headers=self.auth_headers)
        except:
            self.logger.warning('Send message to channel \'{}\' failed'.format(channel.id))
            self.logger.info('Send message to channel \'{}\' failed'.format(channel.id))

    def reply(self, user, channel, message):
        """
            Summary:
                Replies to a user in a channel.

            Args:
                user (User): The User object to reply to.
                channel (Channel): The Channel object to post to.
                msg (str): The message to post.
                mentions (list[str]): The list of user ids to mention.
        """
        self.logger.debug("Sending reply to " + user.id)

        endpoint = "channels/{}/messages".format(channel.id)
        data     = {
            "content":  u"\u200B<@{}> {}".format(user.id, message),
            "mentions": [user.id]
        }

        try:
            self.request("POST", endpoint, data=data, headers=self.auth_headers)
        except:
            self.logger.warning('Reply to user \'{}\' in channel \'{}\' failed'.format(user.id, channel.id))

    # def get_messages(self, msg, number):
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

    def delete_message(self, msg):
        self.logger.debug("Deleting message with ID: {} from channel: {}".format(msg.id, msg.channel))

        endpoint = "channels/{0}/messages/{1}".format(msg.channel, msg.id)
        try:
            self.request("DELETE", endpoint, headers=self.auth_headers)
        except:
            self.logger.warning('Deletion of message \'{}\' in channel \'{}\' failed'.format(msg.id, msg.channel))

    def delete_messages(self, msg_array):
        self.logger.debug("Bulk deleting {} messages from channel: {}".format(len(msg_array), msg_array[0].channel))

        endpoint = "channels/{0}/messages/bulk-delete".format(msg_array[0].channel)
        data     = {
            'messages': []
        }
        for msg in msg_array:
            data['messages'].append(msg.message['id'])
        # self.logger.info(data)
        # self.logger.info(endpoint)
        try:
            self.request("POST", endpoint, data=data, headers=self.auth_headers)
        except:
            self.logger.warning('Deletion of message \'{}\' in channel \'{}\' failed'.format(msg.id, msg.channel))

    def ban_user(self, server_id, user_id, delete_msgs=0):
        self.logger.info("Banning user `{}` from server `{}`".format(user_id, server_id))

        endpoint = "guilds/{0}/bans/{1}".format(server_id, user_id)
        data     = {
            "delete-message-days": delete_msgs
        }
        self.logger.debug(endpoint)
        self.logger.debug(data)

        try:
            self.request("PUT", endpoint, data=data, headers=self.auth_headers)
        except:
            self.logger.warning('Ban of user \'{}\' in server \'{}\' failed'.format(user_id, server_id))

    def whisper(self, user, message):
        self.logger.debug("Sending reply to " + user)

        channel = self.get_private_channel(user)
        endpoint = "channels/{}/messages".format(channel)
        data     = {
            "content": "{}".format(message)
        }

        try:
            self.request("POST", endpoint, data=data, headers=self.auth_headers)
        except:
            self.logger.warning('Reply to user \'{}\' in channel \'{}\' failed'.format(user, channel))

    def upload(self, channel, file):
        self.logger.debug('Sending file to channel ' + channel)

        endpoint = "channels/{}/messages".format(channel)
        files    = {'file': open(file, 'rb')}

        try:
            self.request('POST', endpoint,  files=files, headers={"authorization": self.token})
        except:
            self.logger.warning('Upload file \'{}\' to channel {} failed'.format(file, channel))

    def getUsers(self):
        pass

    @ttl_cache(300)
    def getUser(self, userID):
        user = self.request("GET", "users/{}".format(userID), headers={"authorization": self.token})

        return {
            'user': user,
            'name': user['username'],
            'id': user['id'],
            'expires': time.time() + 600
        }

    def get_channel(self, msg):
        channel = self.request("GET", "channels/{}".format(msg.channel), headers={"authorization": self.token})
        return channel

    def get_server(self, msg):
        channel = self.get_channel(msg)
        server = self.request("GET", "guilds/{}".format(channel['guild_id']), headers={"authorization": self.token})
        return server

    # Discord Specific
    def leave_guild(self, guild_id):
        self.request("DELETE", "users/@me/guilds/{}".format(guild_id), headers={"authorization": self.token})

    def get_servers(self):
        return self.request("GET", "users/@me/guilds", headers={"authorization": self.token})

    def get_private_channel(self, user):
        for channel in self.connectorCache['private_channels']:
            if channel['recipient']['id'] == user:
                return channel['id']
        else:
            channel = self.request("POST", "users/@me/channels", data={"recipient_id": "{}".format(user)}, headers={"authorization": self.token})
            self.connectorCache['private_channels'].append(channel)
            return channel['id']

    def set_status(self, status):
        self._write_socket({
            "op":3,
            "d":{
                "idle_since":None,
                "game": {
                    "name": status
                }
            }
        })

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

    def avatar(self):
        with open("conf/avatar.png", "rb") as avatarImage:
            rawImage = avatarImage.read()

        raw = base64.b64encode(rawImage)
        with open("test", "wb") as file:
            file.write(raw)

        return

        self.request("PATCH", "users/@me", data={"username": "Arcbot", "avatar": "data:image/png;base64," + base64.b64encode(rawImage).decode('ascii')}, headers={"authorization": self.token})

    # Thread Methods
    def _keep_alive(self):
        self.logger.debug("Spawning keep_alive thread at interval: " + str(self.connectorCache['heartbeat_interval']))

        last_heartbeat = time.time()
        heartbeat_interval = self.connectorCache['heartbeat_interval'] / 1000

        while self.connected:
            now = time.time()

            if (now - last_heartbeat) >= heartbeat_interval - 1:
                self._write_socket({"op":1,"d": time.time()})
                self.logger.debug("Keep Alive")

                last_heartbeat = time.time()

            time.sleep(1)

    def _message_consumer(self):
        self.logger.debug("Spawning message_consumer thread")

        while self.connected:
            # Sleep is good for the body; also so we don't hog the CPU polling the socket
            time.sleep(0.5)

            # Read data off of socket
            rawMessage = self._read_socket()
            if not rawMessage: continue

            # Parse raw message
            message = self._parse_message(rawMessage)
            if not message: continue

            # Have worker thread take it from here
            self.core.workers.queue(self._handleMessage, message)

    # Handler Methods
    async def _handleMessage(self, message):
        self.logger.info(message.type)
        # If incoming message is a MESSAGE text
        if message.type == discord.MessageType.default:
            self.core.event.notify("message",  message=message)
            await self.core.command.check(message)

        # If incoming message is PRESSENCE update
        elif type == discord.MessageType.PRESSENCE:
            self.core.event.notify("pressence", message=message)

        # should check for other message types?

    # Socket Methods
    def _write_socket(self, data):
        try:
            self.socket.send(json.dumps(data))
        except socket_error as e:
            if e.errno == 104:
                if not self.connected:
                    return

                self.logger.warning("Connection reset by peer.")
                self.connected = False

            else:
                raise
        except websocket.WebSocketConnectionClosedException:
            if not self.connected:
                return
            self.logger.warning("Websocket unexpectedly closed.")
            self.connected = False

    def _read_socket(self):
        data = ""
        while True:
            try:
                data += self.socket.recv()

                if data:
                    return json.loads(data.rstrip())
                else:
                    return None

            except ValueError as e:
                continue
            except SSLError as e:
                # Raised when we can't read the entire buffer at once
                if e.errno == 2:
                    return None
                raise
            except socket_error as e:
                # Raised when connection reset by peer
                if e.errno == 104:
                    if not self.connected:
                        return

                    self.logger.warning("Connection reset by peer.")
                    self.connected = False
                    return None

                # Raised when send buffer is full; we must try again
                if e.errno == 11:
                    return None
                raise
            except websocket.WebSocketConnectionClosedException:
                if not self.connected:
                    return
                self.logger.warning("Websocket unexpectedly closed.")
                self.connected = False

    # Parser Methods
    def _parse_message(self, message):
        type = content = sender = sender_name = channel = content = timestamp = None

        if message["t"] == "MESSAGE_CREATE":
            type = messageType.MESSAGE
            id = message["d"]['id']
            sender = message["d"]['author']['id']
            sender_name = message["d"]['author']['username']
            channel = message["d"]['channel_id']
            content = message["d"]['content']

            self.logger.info("Message Recieved: [Name:{}][UID:{}][CID:{}]: {}".format(sender_name, sender, channel, content))
        else:
            return None

        if sender == self.connectorCache['self']['id']:
            return None

        return Message(type, id, sender, channel, message, content=content, sender_name=sender_name, timestamp=time.time())

    def _parse_discord_message(self, message):
        type = messageType.MESSAGE
        id = message['id']
        sender = message['author']['id']
        sender_name = message['author']['username']
        channel = message['channel_id']
        content = message['content']

        self.logger.debug("Message Parsed: [Name:{}][UID:{}][CID:{}]: {}".format(sender_name, sender, channel, content))

        return Message(type, id, sender, channel, message, content=content, sender_name=sender_name, timestamp=time.time())
