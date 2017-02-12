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
        user = msg.server.get_member(arguments[0])
        em = discord.Embed(color=user.color)
        em.set_author(
            name="{}#{}".format(user.name, user.discriminator),
            url=user.avatar_url
        )
        em.set_thumbnail(url=user.avatar_url)
        if (user.nick is None):
            nick = user.name
        else:
            nick = user.nick
        if (".gif" in user.avatar_url):
            nitro = "Yes"
        else:
            nitro = "maybe? maybe not? 👀"
        em.add_field(name="Nickname", value=nick)
        em.add_field(name="Nitro", value=nitro)
        await self.send_message(msg.channel, embed=em)

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
            role = "None"
            game = "None"
            em.set_footer(text="Created on {}".format(user.created_at))
        em.set_author(
            name="{}#{}".format(user.name, user.discriminator),
            icon_url=user.avatar_url
        )
        em.add_field(name="Nickname", value=nick,    inline=True)
        em.add_field(name="ID",       value=user.id, inline=True)
        em.add_field(name="Color",    value=color,   inline=True)
        em.add_field(name="Status",   value=status,  inline=True)
        em.add_field(name="Top Role", value=role,    inline=True)
        em.add_field(name="Game",     value=game,    inline=True)
        em.set_thumbnail(url=user.avatar_url)

        await self.send_message(msg.channel, embed=em)
