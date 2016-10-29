"""
    Plugin Name : Moderation
    Plugin Version : 2.0

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
    async def activate(self):
        self.saved_messages = {}
        pass

    @command("^ban <@!?([0-9]+)>", access=ACCESS['ban'])
    async def server_ban(self, msg, arguments):
        """`ban @<user>`: bans `<user>` from the current server."""
        user = self.core.get_member(arguments[0])
        user.server = msg.server
        if (int(self.core.ACL.getAccess(msg.author)) <= int(self.core.ACL.getAccess(user))):
            await self.send_message(
                msg.channel,
                "Nice try, <@!{}>. <@!100165629373337600> has been notified."
            )
            return
        else:
            mtg_banish = {'grip_of_desolation': "http://i.imgur.com/vgbxZsH.png",
                          'vindicate': "http://i.imgur.com/ZVXcGmu.jpg"}
            banish = mtg_banish[random.choice(list(mtg_banish.keys()))]

            # self.core.connection.ban_user(server, user, delete_msgs=0) ##FIX?
            await self.core.ban(user, delete_message_days=0)
            await self.send_message(msg.channel, banish) ##CHANGE? to upload
            await self.send_message(
                msg.channel,
                "Geeeeeet **dunked on**, <@!{}>!".format(user)
            )

    @command("^nuke <@!?([0-9]+)> ([1-7])$", access=ACCESS["ban"])
    async def nuke(self, msg, arguments):
        """`nuke @<user> <days>`: bans `<user>` from the current server and deletes their messages from the past <`days`> days."""
        user = self.core.get_member(arguments[0])
        user.server = msg.server
        delete_days = int(arguments[1])
        if (int(self.core.ACL.getAccess(msg.author)) <= int(self.core.ACL.getAccess(user))):
            await self.send_message(
                msg.channel,
                "Nice try, <@!{}>. <@!100165629373337600> has been notified."
            )
            return
        else:
            mtg_banish = {'merciless_eviction': "http://i.imgur.com/wm9hbzi.png"}
            banish = mtg_banish[random.choice(list(mtg_banish.keys()))]

            await self.core.ban(user, delete_message_days=delete_days)
            await self.send_message(msg.channel, banish) ##CHANGE? to upload
            await self.send_message(msg.channel, "Geeeeeet **dunked on**, <@!{}>!".format(user))

    @command("^push ([0-9]*)$", access=ACCESS['pushPop'])
    async def copy_messages(self, msg, arguments):
        """`push <number>`: saves the last `<number>` messages from the current channel to the stack."""
        if (self.saved_messages.get(msg.author.id)) is None:
            self.saved_messages[msg.author.id] = []
        n_msgs = arguments[0]
        messages = await self.get_messages(msg.channel, n_msgs, before=msg)
        self.logger.info("return type: {}".format(type(messages)))
        self.logger.debug("{} messages: {}".format(n_msgs, messages))
        for message in messages:
            self.logger.debug(message)
            self.saved_messages[msg.author.id].append(message)
        self.saved_messages[msg.author.id].sort(
            key=lambda message: message.timestamp
        )
        self.logger.info("UID: {} pushed {} messages. Total: {}".format(
            msg.author, n_msgs, len(self.saved_messages[msg.author.id]))
        )

    @command("^push -d ([0-9]*)$", access=ACCESS['pushPop'])
    async def push_messages(self, msg, arguments):
        """`push -d <number>`: saves the last `<number>` messages from the current channel to the stack, and deletes them from the channel."""
        if (self.saved_messages.get(msg.author.id)) is None:
            self.saved_messages[msg.author.id] = []
        n_msgs = arguments[0]
        messages = await self.core.purge_from(
            msg.channel,
            limit=n_msgs+1
        )
        # self.logger.debug("{} messages: {}".format(n_msgs, messages))
        for message in messages:
            self.logger.debug(message)
            self.saved_messages[msg.author.id].append(message)
        self.saved_messages[msg.author.id].sort(
            key=lambda message: message.timestamp
        )

        self.logger.info(
            "UID: {} pushed+deleted {} messages. Total: {}".format(
                msg.author.id, n_msgs, len(self.saved_messages[msg.author.id])
            )
        )

    # Internal command for use by pop functions.
    def get_longest_sender(self, user_id):
        longest_name = ""
        for message in self.saved_messages[user_id]:
            sender = message.author.name
            if (len(sender) > len(longest_name)):
                longest_name = sender
        return "<{}>".format(longest_name)

    # Internal command for use by pop functions.
    def format_message_log(self, message, width):
        timestamp = message.timestamp.strftime("[%Y-%m-%d, %H:%M:%S UTC%z]")
        sender = "<{}>".format(message.author.name)
        reply_line = "`{timestamp} {sender:<{width}}` {content}\n".format(
            timestamp=timestamp, sender=sender, width=width,
            content=message.content
        )
        return reply_line

    @command("^pop <#([0-9]*)>$", access=ACCESS['pushPop'])
    async def pop_messages(self, msg, arguments):
        """`pop #<channel>`: posts all the messages on the stack to `<channel>`, and clears the stack."""
        channel = await self.core.get_channel(arguments[0])
        if (len(self.saved_messages[msg.author.id]) == 0):
            await self.send_message(
                msg.channel,
                "<@!{}>: There are no messages on the stack!".format(
                    msg.author.id
                )
            )
        else:
            longest_name = self.get_longest_sender(msg.author.id)
            reply = "**Messages transferred from <#{}>:**\n".format(
                self.saved_messages[msgmsg.author.id][0].channel.id
            )
            for message in self.saved_messages[msg.author.id]:
                reply_line = self.format_message_log(message, len(longest_name))
                if (len(reply) + len(reply_line) > 2000):
                    await self.send_message(channel, reply)
                    reply = "**Messages transferred from <#{}>:**\n".format(
                        self.saved_messages[msg.author.id][0].channel.id
                    )
                reply += reply_line
            await self.send_message(channel, reply)

            # clear the stack
            self.saved_messages[msg.author.id] = []

    @command("^pop here$", access=ACCESS['pushPop'])
    async def pop_here(self, msg, arguments):
        """`pop here`: posts all the messages on the stack to the current channel, and clears the stack."""
        if (len(self.saved_messages[msg.author.id]) == 0):
            await self.send_message(
                msg.channel,
                "<@!{}>: There are no messages on the stack!".format(
                    msg.author.id
                )
            )
        else:
            longest_name = self.get_longest_sender(msg.author.id)
            reply = "**Messages transferred from <#{}>:**\n".format(
                self.saved_messages[msg.author.id][0].channel.id
            )
            for message in self.saved_messages[msg.author.id]:
                reply_line = self.format_message_log(message, len(longest_name))
                if (len(reply) + len(reply_line) > 2000):
                    await self.send_message(msg.channel, reply)
                    reply = "**Messages transferred from <#{}>:**\n".format(
                        self.saved_messages[msg.author.id][0].channel.id
                    )
                reply += reply_line
            await self.send_message(msg.channel, reply)

            # clear the stack
            self.saved_messages[msg.author.id] = []

    @command("^pop clear$", access=ACCESS['pushPop'])
    async def pop_clear(self, msg, arguments):
        """`pop clear`: clears all the messages on your stack."""
        # clear the stack
        self.saved_messages[msg.author.id] = []

    @command("^pop all stacks$", access=ACCESS['ban'])
    async def pop_all(self, msg, arguments):
        """`pop all stacks`: clears all the messages on the stack for **all** users with stacks."""
        self.saved_messages = {}

    @command("^push debug$", access=ACCESS['debug'])
    async def push_debug(self, msg, arguments):
        self.saved_messages[msg.author.id].append(msg)

    @command("^pop debug$", access=ACCESS['debug'])
    async def pop_debug(self, msg, arguments):
        self.logger.info(self.saved_messages)
        longest_name = self.get_longest_sender(msg.author.id)
        if (len(self.saved_messages[msg.author.id]) == 0):
            source = None
        else:
            source = self.saved_messages[msg.author.id][0].channel
        reply = "**Messages transferred from <#{}>:**\n".format(source)
        for message in self.saved_messages[msg.author.id]:
            line = self.format_message_log(message, len(longest_name))
            self.logger.info(line)
            reply += line
        self.logger.info(reply)