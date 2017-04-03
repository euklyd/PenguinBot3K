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

    @command("^flip$", access=-1, name='flip',
             doc_brief="`flip`: Flips a coin that will come up either heads "
             "or tails. Images of many types of coins are included.")
    async def flip(self, msg, arguments):
        coin = random.randint(0, 10)
        user = msg.server.get_member(self.core.user.id)
        em = discord.Embed(color=user.color)
        em.set_footer(
            text="",
            icon_url=user.avatar_url
        )
        if (coin % 2 == 0):
            em.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/a/a0/2006_Quarter_Proof.png")
        else:
            tails = random.randint(0, 10)
            if (tails % 10 == 0):
                em.set_thumbnail(url="http://i.imgur.com/jiLvSSL.png")
            else:
                em.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/4/4e/COBREcentavosecuador2000-2.png")
        await self.send_message(msg.channel, embed=em)

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

    @command("^(?:r|roll) ([0-9]{1,4})d([0-9]{1,4})", access=-1, name='roll',
             doc_brief="`r XdY`: Rolls X Y-sided dice.")
    async def roll(self, msg, arguments):
        roll = 0
        for i in range(0, int(arguments[0])):
            roll += random.randint(1, int(arguments[1]))
        await self.send_message(
            msg.channel,
            "{user}, you rolled `{x}d{y}` and got **{roll}**".format(
                user=msg.author.mention,
                x=arguments[0], y=arguments[1],
                roll=roll)
        )

    @command("^shuffle (.*)", access=-1, name='shuffle',
             doc_brief="`shuffle <list of items>`: Returns the list in a "
             "random order.")
    async def shuffle(self, msg, arguments):
        items = arguments[0].split(' ')
        random.shuffle(items)
        await self.send_message(msg.channel, items)

    @command("^avatar <@!?([0-9]*)>$", access=-1, name='avatar',
             doc_brief="`avatar @<user>`: posts a link to `<user>`'s avatar")
    async def get_avatar(self, msg, arguments):
        """`avatar @<user>`: posts a link to `<user>`'s avatar"""
        user = msg.server.get_member(arguments[0])
        if (user is None):
            # discord.Server.get_member() returns None if the specified user
            # isn't a part of that server.
            user = await self.core.get_user_info(arguments[0])
            em = discord.Embed()
            nick = user.name
        else:
            em = discord.Embed(color=user.color)
            if (user.nick is None):
                nick = user.name
            else:
                nick = user.nick
        em.set_author(
            name="{}#{}".format(user.name, user.discriminator),
            url=user.avatar_url
        )
        em.set_thumbnail(url=user.avatar_url)
        if (".gif" in user.avatar_url):
            nitro = "Yes"
        else:
            nitro = "maybe? maybe not? 👀"
        em.add_field(name="Nickname", value=nick)
        em.add_field(name="Nitro", value=nitro)
        em.add_field(name="URL", value="(Click the title!)", inline=False)
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
