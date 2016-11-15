"""
    Plugin Name : Utility
    Plugin Version : 3.0

    Description:
        Provides basic utility commands, e.g., random selectors
        and user info.

    Contributors:
        - Popguin / Euklyd

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *
import discord
import logging
import random

logger = logging.getLogger(__name__)


class Utility(Plugin):
    async def activate(self):
        pass

    @command(
        "^pick(?:[- ]one)? (.*)", access=-1, name='pick',
        doc_brief=("`pick one <list of items>`: Selects one item out of a"
                   "list of space-separated items.")
    )
    async def pick_one(self, msg, arguments):
        """`pick one <list of items>`: Selects one item out of a list of space-separated items."""
        # args = arguments[0]
        # items = args.split(' ')
        items = arguments[0].split(' ')
        choice = random.choice(items)
        await self.send_message(
            msg.channel,
            "<@!{}>, your selection is **{}**!".format(msg.author.id, choice)
        )

    @command(
        "^avatar <@!?([0-9]*)>$", access=-1, name='avatar',
        doc_brief="`avatar @<user>`: posts a link to `<user>`'s avatar"
    )
    async def get_avatar(self, msg, arguments):
        """`avatar @<user>`: posts a link to `<user>`'s avatar"""
        user = await self.core.get_user_info(arguments[0])
        reply = "**Avatar for {}#{}:**\n{}".format(
            user.name,
            user.discriminator,
            user.avatar_url
        )
        await self.send_message(msg.channel, reply)

    # @command("^(?:get[- ])?info <@!?([0-9]*)>$", access=50)
    @command(
        "^info <@!?([0-9]*)>$", access=50, name='info',
        doc_brief=("`info @<user>`: Gets assorted info about the specified "
                   "<user>.")
    )
    async def get_info(self, msg, arguments):
        user = msg.server.get_member(arguments[0])
        # user = await self.core.get_member(arguments[0])
        if (user is None):
            user = await self.core.get_user_info(arguments[0])
            reply =  "**Info for {}#{}**".format(user.name, user.discriminator)
            if (user.bot is True):
                reply += u"\u00A0`\u200B\U0001F1E7\u200B\U0001F1F4\u200B\U0001F1F9`"
            reply += "\n\t`ID:          \u00A0`{}".format(user.id)
            reply += "\n\t`Created:     \u00A0`{}".format(user.created_at)
        else:
            reply =  "**Info for {}#{}**".format(user.name, user.discriminator)
            if (user.bot is True):
                reply += u"\u00A0`\u200B\U0001F1E7\u200B\U0001F1F4\u200B\U0001F1F9`"
            if (user.nick != user.name):
                reply += "\n\t`Nick:        \u00A0`{}".format(user.nick)
            reply += "\n\t`ID:          \u00A0`{}".format(user.id)
            reply += "\n\t`Created:     \u00A0`{}".format(user.created_at)
            reply += "\n\t`Joined:      \u00A0`{}".format(user.joined_at)
            if (user.color != discord.Colour.default):
                reply += "\n\t`Color:       \u00A0`{} (`{}`)".format(
                    user.color.to_tuple(), str(user.color)
                )
            if (user.top_role.name != "@everyone"):
                # print(user.top_role)
                # print(user.top_role == "@everyone")
                # print(type(user.top_role))
                # print(type(user.top_role.name))
                reply += "\n\t`Role:        \u00A0`{}".format(user.top_role)
            else:
                reply += "\n\t`Role:        \u00A0`{}".format(u"@\u200Beveryone")
        reply += "\n\t`Avatar:`\n{}".format(user.avatar_url)
        await self.send_message(msg.channel, reply)
