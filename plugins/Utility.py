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

    @command("^pick(?:[- ]one)? (.*)", access=-1, name='pick',
             doc_brief="`pick one <list of items>`: Selects one item out of "
             "a list of space-separated items.")
    async def pick_one(self, msg, arguments):
        items = arguments[0].split(' ')
        choice = random.choice(items)
        await self.send_message(
            msg.channel,
            "<@!{}>, your selection is **{}**!".format(msg.author.id, choice)
        )

    @command("^avatar <@!?([0-9]*)>$", access=-1, name='avatar',
             doc_brief="`avatar @<user>`: posts a link to `<user>`'s avatar")
    async def get_avatar(self, msg, arguments):
        """`avatar @<user>`: posts a link to `<user>`'s avatar"""
        user = await self.core.get_user_info(arguments[0])
        reply = "**Avatar for {}#{}:**\n{}".format(
            user.name,
            user.discriminator,
            user.avatar_url
        )
        await self.send_message(msg.channel, reply)

    @command("^info <@!?([0-9]*)>$", access=50, name='info',
             doc_brief="`info @<user>`: Gets assorted info about the "
             "specified <user>.")
    async def get_info(self, msg, arguments):
        user = msg.server.get_member(arguments[0])
        if (user is None):
            # discord.Server.get_member() returns None if the specified user
            # isn't a part of that server.
            user = await self.core.get_user_info(arguments[0])
        if (type(user) == discord.Member):
            # If the user isn't on this server, then they're a discord.User
            # rather than discord.Member, and so are missing a lot of fields.
            em = discord.Embed(color=user.color)
            nick = user.nick
            color = "{} ({})".format(user.color.to_tuple(), user.color)
            status = user.status
            game = user.game
            role = user.top_role
            em.set_footer(text="Joined on {}".format(user.joined_at))
        else:
            em = discord.Embed()
            nick = "None"
            color = "None"
            status = "None"
            game = "None"
            role = "None"
            em.set_footer(text="Created on {}".format(user.created_at))
        em.set_author(
            name="{}#{}".format(user.name, user.discriminator),
            icon_url=user.avatar_url
        )
        em.add_field(name="Nickname", value=nick, inline=True)
        em.add_field(name="ID", value=user.id, inline=True)
        em.add_field(
            name="Color",
            value=color,
            inline=True
        )
        em.add_field(name="Status", value=status, inline=True)
        em.add_field(name="Game", value=game, inline=True)
        em.add_field(
            name="Top Role",
            value=role,
            inline=True
        )

        await self.send_message(msg.channel, embed=em)

    @command('^find emoji "([0-9A-Za-z\_]+)"$', access=-1, name='find emoji',
             doc_brief='`find emoji "emoji_name"`: tries to find an emoji with'
             'the specified name on the current server.')
    async def get_avatar(self, msg, arguments):
        emoji = self.core.emoji.emoji(msg, [arguments[0]])
        reply = "`{em}`: {em}".format(em=emoji)
        await self.send_message(msg.channel, reply)
