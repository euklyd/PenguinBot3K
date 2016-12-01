"""
    Plugin Name : Moderation
    Plugin Version : 3.0

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
import discord

ACCESS = {
    'pushPop': 300,
    'ban': 900,
    'anonymous': 900,
    'debug': 1000
}


class Moderation(Plugin):
    async def activate(self):
        self.saved_messages = {}
        pass

    @command("^repeat (.*)", access=ACCESS['anonymous'], name='repeat',
             doc_brief=("`repeat <message>`: Sends `<message>` to the channel "
             "anonymously."))
    async def repeat(self, msg, arguments):
        await self.send_message(msg.channel, arguments[0])
        await self.delete_message(msg)

    @command("^announce <#([0-9]*)> (.*)", access=ACCESS['anonymous'],
             name='announce',
             doc_brief=("`announce #<channel> <message>`: Sends `<message>` "
             "to `<channel>` anonymously."))
    async def announce(self, msg, arguments):
        channel = self.core.get_channel(arguments[0])
        await self.send_message(channel, arguments[1])

    @command("^announce -d <#([0-9]*)> (.*)", access=ACCESS['anonymous'],
             name='announce', doc_brief=("`announce -d #<channel> <message>`: "
             "Sends `<message>` to `<channel>` anonymously, and "
             "deletes command message."))
    async def announce_delete(self, msg, arguments):
        channel = self.core.get_channel(arguments[0])
        await self.send_message(channel, arguments[1])
        await self.delete_message(msg)

    @command("^list roles$", access=500, name='list roles',
             doc_brief="`list roles`: Lists all roles on the current "
             "server in an IM.")
    async def list_all_roles(self, msg, arguments):
        roles = msg.server.roles
        roles.sort(key=lambda role: role.position, reverse=True)
        role_block = "**List of roles on {}:**".format(msg.server.name)
        for role in roles:
            role_block += "\n{n}) {name} ({color}): `{mention}`, `{permissions}`".format(
                n=role.position,
                name=role.name,
                color=role.color,
                mention=role.mention,
                permissions=role.permissions
            )
            if (len(role_block) >= 1700):
                self.logger.info(role_block)
                try:
                    await self.send_whisper(msg.author, role_block)
                except discord.HTTPException:
                    self.logger("well fuck: discord.HTTPException")
                role_block = "**List of roles on {}:**".format(msg.server.name)
        self.logger.info(role_block)
        try:
            if (role_block.count('\n') > 1):
                await self.send_whisper(msg.author, role_block)
        except discord.HTTPException:
            self.logger("well fuck: discord.HTTPException")
        except:
            # await self.core.start_private_message(msg.author)
            await self.send_whisper(msg.author, "sup")
            await self.send_message(msg.channel, role_block)

    @command("^ban <@!?([0-9]+)>", access=ACCESS['ban'], name='ban',
             doc_brief="`ban @<user>`: bans `<user>` from the current server.")
    async def server_ban(self, msg, arguments):
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

    @command("^nuke <@!?([0-9]+)> ([1-7])$", access=ACCESS["ban"], name='nuke',
             doc_brief=("`nuke @<user> <days>`: bans `<user>` from the current "
             "server and deletes their messages from the past <`days`> "
             "days."))
    async def nuke(self, msg, arguments):
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

    @command("^push ([0-9]+)$", access=ACCESS['pushPop'], name='push',
             doc_brief=("`push <number>`: saves the last `<number>` messages "
             "from the current channel to the stack."))
    async def copy_messages(self, msg, arguments):
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
            msg.author.id, n_msgs, len(self.saved_messages[msg.author.id]))
        )

    @command("^push -d ([0-9]+)$", access=ACCESS['pushPop'], name='push',
             doc_brief=("`push -d <number>`: saves the last `<number>` "
             "messages from the current channel to the stack, and deletes "
             "them from the channel."))
    async def push_messages(self, msg, arguments):
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

    @command("^pop <#([0-9]*)>$", access=ACCESS['pushPop'], name='pop',
             doc_brief=("`pop #<channel>`: posts all the messages on the stack to "
             "`<channel>`, and clears the stack."))
    async def pop_messages(self, msg, arguments):
        # channel = await self.core.get_channel(arguments[0])
        channel = self.core.get_channel(arguments[0])
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

    @command("^pop here$", access=ACCESS['pushPop'], name='pop',
             doc_brief=("`pop here`: posts all the messages on the stack to the "
             "current channel, and clears the stack."))
    async def pop_here(self, msg, arguments):
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

    @command("^pop clear$", access=ACCESS['pushPop'], name='pop',
             doc_brief="`pop clear`: clears all the messages on your stack.")
    async def pop_clear(self, msg, arguments):
        # clear the stack
        self.saved_messages[msg.author.id] = []

    @command("^pop all stacks$", access=ACCESS['ban'], name='pop',
             doc_brief=("`pop all stacks`: clears all the messages on the stack "
             "for **all** users with stacks."))
    async def pop_all(self, msg, arguments):
        self.saved_messages = {}

    @command("^push debug$", access=ACCESS['debug'], name='push')
    async def push_debug(self, msg, arguments):
        self.saved_messages[msg.author.id].append(msg)

    @command("^pop debug$", access=ACCESS['debug'], name='pop')
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
