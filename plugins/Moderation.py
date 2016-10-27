"""
    Plugin Name : Moderation
    Plugin Version : 0.1

    Description:
        Provides some moderation commands, e.g., banning users.

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *

import random
import re
import string

ACCESS = {
    'pushPop': 300,
    'ban': 900,
    'debug': 1000
}


class Moderation(Plugin):
    def activate(self):
        self.saved_messages = {}
        pass

    @command("^ban <@!?([0-9]+)>", access=ACCESS['ban'])
    def server_ban(self, msg):
        """`ban @<user>`: bans `<user>` from the current server."""
        user = msg.arguments[0]
        server = self.core.connection.get_server(msg)['id']
        if (int(self.core.ACL.getAccess(msg.sender)) <= int(self.core.ACL.getAccess(user))):
            self.say(msg.channel, "Nice try, <@!{}>. <@!100165629373337600> has been notified.")
            return
        else:
            mtg_banish = {'grip_of_desolation': "http://i.imgur.com/vgbxZsH.png",
                          'vindicate': "http://i.imgur.com/ZVXcGmu.jpg"}
            banish = mtg_banish[random.choice(list(mtg_banish.keys()))]

            self.core.connection.ban_user(server, user, delete_msgs=0)
            self.say(msg.channel, banish)
            self.say(msg.channel, "Geeeeeet **dunked on**, <@!{}>!".format(user))

    @command("^nuke <@!?([0-9]+)> ([1-7])$", access=ACCESS["ban"])
    def nuke(self, msg):
        """`nuke @<user> <days>`: bans `<user>` from the current server and deletes their messages from the past <`days`> days."""
        user = msg.arguments[0]
        delete_days = int(msg.arguments[1])
        server = self.core.connection.get_server(msg)['id']
        if (int(self.core.ACL.getAccess(msg.sender)) <= int(self.core.ACL.getAccess(user))):
            self.say(msg.channel, "Nice try, <@!{}>. <@!100165629373337600> has been notified.")
            return
        else:
            mtg_banish = {'merciless_eviction': "http://i.imgur.com/wm9hbzi.png"}
            banish = mtg_banish[random.choice(list(mtg_banish.keys()))]

            self.core.connection.ban_user(server, user, delete_msgs=delete_days)
            self.say(msg.channel, banish)
            self.say(msg.channel, "Geeeeeet **dunked on**, <@!{}>!".format(user))

    @command("^push ([0-9]*)$", access=ACCESS['pushPop'])
    def copy_messages(self, msg):
        """`push <number>`: saves the last `<number>` messages from the current channel to the stack."""
        if (self.saved_messages.get(msg.sender)) is None:
            self.saved_messages[msg.sender] = []
        n_msgs = msg.arguments[0]
        messages = self.core.connection.get_messages(msg, n_msgs)
        self.logger.debug("{} messages: {}".format(n_msgs, messages))
        for message in messages:
            self.logger.debug(message)
            self.saved_messages[msg.sender].append(message)
        self.saved_messages[msg.sender].sort(
            key=lambda message: message.message['timestamp']
        )
        self.logger.debug("UID: {} pushed {} messages. Total: {}".format(
            msg.sender, n_msgs, len(self.saved_messages[msg.sender]))
        )

    @command("^push -d ([0-9]*)$", access=ACCESS['pushPop'])
    def push_messages(self, msg):
        """`push -d <number>`: saves the last `<number>` messages from the current channel to the stack, and deletes them from the channel."""
        if (self.saved_messages.get(msg.sender)) is None:
            self.saved_messages[msg.sender] = []
        n_msgs = msg.arguments[0]
        messages = self.core.connection.get_messages(msg, n_msgs)
        self.logger.debug("{} messages: {}".format(n_msgs, messages))
        for message in messages:
            self.logger.debug(message)
            self.saved_messages[msg.sender].append(message)
        self.saved_messages[msg.sender].sort(
            key=lambda message: message.message['timestamp']
        )
        self.core.connection.delete_messages(messages)
        self.logger.info("UID: {} pushed+deleted {} messages. Total: {}".format(
            msg.sender, n_msgs, len(self.saved_messages[msg.sender]))
        )

    # Internal command for use by pop functions.
    def get_longest_sender(self, user_id):
        longest_name = ""
        for message in self.saved_messages[user_id]:
            sender = message.message['author']['username']
            if (len(sender) > len(longest_name)):
                longest_name = sender
        return "<{}>".format(longest_name)

    # Internal command for use by pop functions.
    def format_message_log(self, message, width):
        # Timestamp has format 2016-03-24T23:15:59.605000+00:00
        regex = "([0-9]{4}-[0-9]{2}-[0-9]{2})T([0-9]{2}:[0-9]{2}:[0-9]{2})"
        match = re.search(regex, message.message['timestamp'])
        timestamp = "[{date}, {time}]".format(date=match.group(1), time=match.group(2))
        sender = "<{}>".format(message.message['author']['username'])
        reply_line = "`{timestamp} {sender:<{width}}` {content}\n".format(
            timestamp=timestamp, sender=sender, width=width,
            content=message.content
        )
        return reply_line

    @command("^pop <#([0-9]*)>$", access=ACCESS['pushPop'])
    def pop_messages(self, msg):
        """`pop #<channel>`: posts all the messages on the stack to `<channel>`, and clears the stack."""
        if (len(self.saved_messages[msg.sender]) == 0):
            self.say(msg.channel, "<@!{}>: There are no messages on the stack!".format(msg.sender))
        else:
            longest_name = self.get_longest_sender(msg.sender)
            reply = "**Messages transferred from <#{}>:**\n".format(self.saved_messages[msg.sender][0].channel)
            for message in self.saved_messages[msg.sender]:
                reply_line = self.format_message_log(message, len(longest_name))
                if (len(reply) + len(reply_line) > 2000):
                    self.say(msg.arguments[0], reply)
                    reply = "**Messages transferred from <#{}>:**\n".format(self.saved_messages[msg.sender][0].channel)
                reply += reply_line
            self.say(msg.arguments[0], reply)

            # clear the stack
            self.saved_messages[msg.sender] = []

    @command("^pop here$", access=ACCESS['pushPop'])
    def pop_here(self, msg):
        """`pop here`: posts all the messages on the stack to the current channel, and clears the stack."""
        if (len(self.saved_messages[msg.sender]) == 0):
            self.say(msg.channel, "<@!{}>: There are no messages on the stack!".format(msg.sender))
        else:
            longest_name = self.get_longest_sender(msg.sender)
            reply = "**Messages transferred from <#{}>:**\n".format(self.saved_messages[msg.sender][0].channel)
            for message in self.saved_messages[msg.sender]:
                reply_line = self.format_message_log(message, len(longest_name))
                if (len(reply) + len(reply_line) > 2000):
                    self.say(msg.channel, reply)
                    reply = "**Messages transferred from <#{}>:**\n".format(self.saved_messages[msg.sender][0].channel)
                reply += reply_line
            self.say(msg.channel, reply)

            # clear the stack
            self.saved_messages[msg.sender] = []

    @command("^pop clear$", access=ACCESS['pushPop'])
    def pop_clear(self, msg):
        """`pop clear`: clears all the messages on your stack."""
        # clear the stack
        self.saved_messages[msg.sender] = []

    @command("^pop all stacks$", access=ACCESS['ban'])
    def pop_all(self, msg):
        """`pop all stacks`: clears all the messages on the stack for **all** users with stacks."""
        self.saved_messages = {}

    @command("^push debug$", access=ACCESS['debug'])
    def push_debug(self, msg):
        self.saved_messages[msg.sender].append(msg)

    @command("^pop debug$", access=ACCESS['debug'])
    def pop_debug(self, msg):
        self.logger.info(self.saved_messages)
        longest_name = self.get_longest_sender(msg.sender)
        if (len(self.saved_messages[msg.sender]) == 0):
            source = None
        else:
            source = self.saved_messages[msg.sender][0].channel
        reply = "**Messages transferred from <#{}>:**\n".format(source)
        for message in self.saved_messages[msg.sender]:
            line = self.format_message_log(message, len(longest_name))
            self.logger.info(line)
            reply += line
        self.logger.info(reply)
