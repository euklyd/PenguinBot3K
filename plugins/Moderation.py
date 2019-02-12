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

import csv
import datetime
import discord
import io
import json
import random
import re
import requests
import string

from datetime import datetime

ACCESS = {
    'query': 200,
    'pushPop': 300,
    'ban': 900,
    'anonymous': 999,
    'debug': 1000
}

GREENTICK = None
REDTICK = None


class Moderation(Plugin):
    async def activate(self):
        self.saved_messages = {}
        global GREENTICK
        global REDTICK
        GREENTICK = self.core.emoji.any_emoji(['greentick'])
        REDTICK   = self.core.emoji.any_emoji(['redtick'])
        pass

    @command("^repeat (.*)", access=ACCESS['anonymous'], name='repeat',
             doc_brief="`repeat <message>`: Sends `<message>` to the channel "
             "anonymously.")
    async def repeat(self, msg, arguments):
        await self.send_message(msg.channel, arguments[0])
        await self.delete_message(msg)

    @command("^(announce <#([0-9]*)> )(.*)", access=ACCESS['anonymous'],
             name='announce',
             doc_brief="`announce #<channel> <message>`: Sends `<message>` "
             "to `<channel>` anonymously.")
    async def announce(self, msg, arguments):
        reply = msg.content[len(arguments[0]):]
        channel = self.core.get_channel(arguments[1])
        await self.send_message(channel, reply)
        await self.add_reaction(msg, GREENTICK)

    @command("^announce -d <#([0-9]*)> (.*)", access=ACCESS['anonymous'],
             name='announce', doc_brief="`announce -d #<channel> <message>`: "
             "Sends `<message>` to `<channel>` anonymously, and "
             "deletes command message.")
    async def announce_delete(self, msg, arguments):
        channel = self.core.get_channel(arguments[0])
        await self.send_message(channel, arguments[1])
        await self.delete_message(msg)

    @command("^(whisper (?:<@!?)?([0-9]+)>? )(.*)", access=ACCESS['debug'],
             name='whisper')
    async def whisper(self, msg, arguments):
        reply = msg.content[len(arguments[0]):]
        user = await self.core.get_user_info(arguments[1])
        await self.send_message(user, reply)
        await self.add_reaction(msg, GREENTICK)

    @command("^imgpost <#([0-9]*)>", access=ACCESS['debug'], name='imgpost')
    async def imgpost(self, msg, arguments):
        dest = '/tmp/imgpost.png'
        channel = self.core.get_channel(arguments[0])
        response = requests.get(msg.embeds[0]['thumbnail']['url'])
        if response.status_code == 200:
            with open(dest, 'wb') as f:
                for chunk in response:
                    f.write(chunk)
            await self.send_file(channel, dest)
        else:
            await self.send_message(msg.channel, "Couldn't download image.")

    @command("^(?:permissions|perms) hex ?(.*)?$", access=-1, name='perms hex',
             doc_brief="`permissions hex <PERM1> <PERM2> ...`: Generate a hex "
             "representation of the permissions associated with the inputs.")
    async def perms_hex(self, msg, arguments):
        perms = arguments[0].upper().split(' ')
        self.logger.info("perms: {}".format(perms))
        with open("resources/permissions_keys.json") as perms_fp:
            perms_map = json.load(perms_fp)
        if (arguments[0] is None):
            reply = "**Permissions keys:**\n"
            for perm in perms_map:
                reply += "`{}`: `{}`\n".format(perm, perm['value'])
            await self.send_message(msg.author, reply)
            return
        invalid_keys = []
        perms_hex = 0
        for perm in perms:
            if (perm in perms_map):
                perms_hex |= int(perms_map[perm]['value'], 0)
                self.logger.info("{}, {}".format(
                    perm, int(perms_map[perm]['value'], 0))
                )
            else:
                invalid_keys.append(perm)
        reply = "**{}**, those permissions have the hex code `{}`".format(
            msg.author.name, hex(perms_hex)
        )
        if (invalid_keys != []):
            reply += "\nInvalid keys: `{}`".format(invalid_keys)
        await self.send_message(msg.channel, reply)

    @command("^(?:perms|permissions) <@!?([\d]+)>$", access=ACCESS['query'],
             name='user perms',
             doc_brief="`perms <@user>`: shows the permissions hex code of "
             "the mentioned user.")
    async def user_perms(self, msg, arguments):
        user = msg.mentions[0]
        reply = (
            "Server permissions for **{}**: `{}`\nPermissions in {}: `{}`"
        ).format(
            user, hex(user.server_permissions.value), msg.channel.mention,
            hex(user.permissions_in(msg.channel).value)
        )
        await self.send_message(msg.channel, reply)

    @command("^stfu <@!?[\d]+>$", access=ACCESS['ban'],
             name='no @everyone',
             doc_brief="`stfu <@user>`: lists which of <users>'s roles can "
             "mention `@everyone`.")
    async def stfu_user(self, msg, arguments):
        user = msg.mentions[0]
        reply = "Roles {} has with `@everyone` permission:\n".format(user)
        for role in user.roles:
            if role.permissions.mention_everyone:
                reply += role.name + "\n"
        await self.send_message(msg.channel, reply)

    @command("^stfu$", access=ACCESS['ban'],
             name='no @everyone',
             doc_brief="`stfu`: lists which roles can mention `@everyone`.")
    async def stfu(self, msg, arguments):
        reply = "Roles with `@everyone` permission:\n"
        for role in msg.server.roles:
            if role.permissions.mention_everyone:
                reply += role.name + "\n"
        await self.send_message(msg.channel, reply)

    @command("^list roles ?(0x[0-9A-Fa-f]*)?$", access=500, name='list roles',
             doc_brief="`list roles`: Lists all roles on the current "
             "server in an IM.")
    async def list_all_roles(self, msg, arguments):
        if (arguments[0] is None):
            search_perms = 0xffffffff
        else:
            search_perms = int(arguments[0], 0)
        roles = msg.server.roles
        roles.sort(key=lambda role: role.position, reverse=True)
        matching_roles = []
        role_block = "**List of roles on {}:**".format(msg.server.name)
        for role in roles:
            if (role.permissions.value & search_perms != 0):
                role_block += ("\n{n}) {name} ({color}): `{mention}`, "
                               "`{permissions}`").format(
                    n=role.position,
                    name=role.name,
                    color=role.color,
                    mention=role.mention,
                    permissions=hex(role.permissions.value)
                )
                matching_roles.append(role)
            if (len(role_block) >= 1700):
                self.logger.info(role_block)
                try:
                    await self.send_whisper(msg.author, role_block)
                except discord.HTTPException:
                    self.logger("well fuck: discord.HTTPException")
                role_block = "**List of roles on {}:**".format(msg.server.name)
        self.logger.info(matching_roles)
        if (len(matching_roles) == 0):
            await self.send_whisper(
                msg.author,
                "No roles found matching `{}`".format(arguments[0])
            )
            return
        try:
            if (role_block.count('\n') > 0):
                await self.send_whisper(msg.author, role_block)
        except discord.HTTPException:
            self.logger("well fuck: discord.HTTPException")
        except:
            await self.send_whisper(msg.author, "sup")
            await self.send_message(msg.channel, role_block)

    @command("^ban <@!?([0-9]+)>", access=ACCESS['ban'], name='ban',
             doc_brief="`ban @<user>`: bans `<user>` from the current server.")
    async def server_ban(self, msg, arguments):
        user = await self.core.get_user_info(arguments[0])
        # user = msg.mentions[0]  # can't do this because they're not a Member
        # user = discord.Member(
        #     user=user,
        #     voice=discord.VoiceState(),
        #     joined_at=datetime.datetime.now(),
        #     status=discord.Status("online"),
        #     server=msg.server,
        #     color=discord.Colour.default()
        # )
        # user.id = arguments[0]
        # user.server = msg.server
        self.logger.info("banbanban")
        # self.logger.info(type(msg.author))
        # self.logger.info(msg.author)
        if (int(self.core.ACL.getAccess(msg.author)) <= int(self.core.ACL.getAccess(user))):
            self.logger.info("{}, {}".format(
                int(self.core.ACL.getAccess(msg.author)),
                int(self.core.ACL.getAccess(user))
            ))
            await self.send_message(
                msg.channel,
                "Nice try, {}. <@!{}> has been notified.".format(
                    msg.author.mention,
                    self.core.config.backdoor
                )
            )
            return
        else:
            mtg_banish = {
                'vindicate': "http://i.imgur.com/ZVXcGmu.jpg",
                'grip of desolation': "http://i.imgur.com/vgbxZsH.png",
                'destruction punch': (
                    "http://i.imgur.com/UkETEEb.png",
                    "I activate my trap card, {}!".format(user.mention)
                ),
                'dark core': "http://i.imgur.com/40v2nK2.png"
            }
            key = random.choice(list(mtg_banish.keys()))
            if (type(mtg_banish[key]) is tuple):
                banish = mtg_banish[key][0]
                reply = mtg_banish[key][1]
            else:
                banish = mtg_banish[key]
                reply = f'Geeeeeet **dunked on**, {user}!'

            em = discord.Embed(color=msg.server.get_member(self.core.user.id).color)
            em.set_image(url=banish)
            await self.send_message(msg.channel, embed=em)
            await self.send_message(
                msg.channel,
                reply
            )
            await self.ban_user(user, msg.server, delete_message_days=0)
            self.logger.info(f'Successfully banned {user}')

    @command("^nuke <@!?([0-9]+)> ([0-7])$", access=ACCESS["ban"], name='nuke',
             doc_brief="`nuke @<user> <days>`: bans `<user>` from the current "
             "server and deletes their messages from the past <`days`> "
             "days.")
    async def nuke(self, msg, arguments):
        user = self.core.get_member(arguments[0])
        user.server = msg.server
        delete_days = int(arguments[1])
        if (int(self.core.ACL.getAccess(msg.author)) <= int(self.core.ACL.getAccess(user))):
            await self.send_message(
                msg.channel,
                f"Nice try, {msg.author.mention}. <@!100165629373337600> has been notified."
            )
            return
        else:
            mtg_banish = {'merciless_eviction': "http://i.imgur.com/wm9hbzi.png"}
            banish = mtg_banish[random.choice(list(mtg_banish.keys()))]

            await self.core.ban(user, delete_message_days=delete_days)
            await self.send_message(msg.channel, banish) ##CHANGE? to upload
            await self.send_message(msg.channel, f'Geeeeeet **dunked on**, {user}!')

    @command("^push ([0-9]+)$", access=ACCESS['pushPop'], name='push',
             doc_brief="`push <number>`: saves the last `<number>` messages "
             "from the current channel to the stack.")
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
             doc_brief="`push -d <number>`: saves the last `<number>` "
             "messages from the current channel to the stack, and deletes "
             "them from the channel.")
    async def push_messages(self, msg, arguments):
        if (self.saved_messages.get(msg.author.id)) is None:
            self.saved_messages[msg.author.id] = []
        n_msgs = int(arguments[0])
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
             doc_brief="`pop #<channel>`: posts all the messages on the stack to "
             "`<channel>`, and clears the stack.")
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
             doc_brief="`pop here`: posts all the messages on the stack to the "
             "current channel, and clears the stack.")
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
             doc_brief="`pop all stacks`: clears all the messages on the stack "
             "for **all** users with stacks.")
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

    @command("^userlist$", access=ACCESS['ban'], name='userlist',
             doc_brief="`userlist`: Exports a list of all users in the server.")
    async def userlist(self, msg, arguments):
        FILENAME = f'/tmp/userlist-{msg.server.name}-{datetime.now()}.csv'

        members = sorted(
            msg.server.members,
            key=lambda x: str(x).lower()
        )
        user_list = ''
        csv_export = [[
            'Discord Name',
            'Server Nickname',
            'Discord ID',
            'Joined (POSIX)',
            'Joined (UTC)',
            'Roles'
        ]]
        def nick_or_blank(nick):
            if nick is None:
                return ''
            return nick
        for member in members:
            csv_export.append([
                str(member),
                nick_or_blank(member.nick),
                member.id,
                member.joined_at.timestamp(),
                member.joined_at.strftime('%m/%d/%Y %H:%M:%S'),
                [role.name for role in member.roles]
            ])
        with open(FILENAME, 'w') as f:
            writer = csv.writer(f, csv.QUOTE_NONNUMERIC)
            writer.writerows(csv_export)
        await self.send_file(
            msg.channel,
            FILENAME,
            content=f'Exported {len(members)} members'
        )
