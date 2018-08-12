"""
    Plugin Name : EiMM
    Plugin Version : 0.1

    Description:
        Utilities for the Mafia-spinoff free-for-all game,
        Everyone is Mafia Mafia.

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *

import asyncio
import discord
import json
import logging
import random
import requests
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

path = "resources/eimm/{}"


def get_avatar_image(user):
    response = requests.get(user.avatar_url)
    return Image.open(BytesIO(response.content)).convert('RGBA')

def create_dm_icon(icon1, icon2):
    # Saves a 128x128, bytes-like representation of a combination of
    # icon1 and icon2 to /tmp.
    dest = '/tmp/dmicon.png'
    size = (128, 128)

    i1 = icon1.resize(size)
    i2 = icon2.resize(size)
    i1 = i1.crop((0,0,64,128))
    i2.paste(i1, (0,0))
    i3 = BytesIO()
    i2.save(i3, 'PNG')
    i2.save(dest)
    return i3.getvalue()
    # return dest


class EiMM(Plugin):
    async def activate(self):
        self.dayvigs = []
        with open(path.format('dayvig.json'), 'r') as dayvig:
            self.dayvigs = json.load(dayvig)

    @command("^[Dd][Mm]icon (\d+)$", access=-1, name='DMicon',
             doc_brief="`DMicon <userID>`: Creates an icon for a DM between yourself and another user.")
    async def DMicon1(self, msg, arguments):
        arguments = list(arguments)
        arguments.append(msg.author.id)
        await self.DMicon2(msg, arguments)

    @command("^[Dd][Mm]icon (\d+) (\d+)$", access=-1, name='DMicon',
             doc_brief="`DMicon <userID> <userID>`: Creates an icon for a DM between two users.")
    async def DMicon2(self, msg, arguments):
        u1 = await self.get_user_info(arguments[0])
        u2 = await self.get_user_info(arguments[1])
        icon = create_dm_icon(get_avatar_image(u1), get_avatar_image(u2))
        await self.send_file(msg.channel, '/tmp/dmicon.png')

    @command("^shoot (\d+)$", access=-1, name='shoot')
    async def shoot_id(self, msg, arguments):
        user = msg.server.get_member(arguments[0])
        if user is None:
            user = await self.get_user_info(arguments[0])
        msg.mentions = [user]
        await self.shoot(msg, arguments)

    @command("^shoot <@!?(\d+)>(?:\*\*)?$", access=-1, name='shoot',
             doc_brief="`shoot @user`: Murders the fuck out of <user>.")
    async def shoot(self, msg, arguments):
        target = msg.mentions[0]
        modifier = None
        base = None
        addition = None
        with open(path.format('roles.json'), 'r') as roledict:
            roles = json.load(roledict)
        if random.randint(0, 1) == 0:
            modifier = random.choices(
                list(roles['modifier'].keys()),
                weights=list(roles['modifier'].values())
            )[0]
        base = random.choices(
            list(roles['normal'].keys()) + list(roles['bastard'].keys()),
            weights=list(roles['normal'].values()) + list(roles['bastard'].values())
        )[0]
        if random.randint(0, 1) == 0:
            addition = random.choices(
                list(roles['additions'].keys()),
                weights=list(roles['additions'].values())
            )[0]
        role = ""
        alignment = "Mafia"
        if modifier is not None:
            role += modifier + " "
        role += base
        if addition is not None:
            role += " + {}x {}".format(random.randint(1, 3), addition)
        if type(target) is not discord.Member or target.nick is None:
            user = target.name
        else:
            user = target.nick
        if target.id in roles['overrides']:
            if random.random() < roles['overrides'][target.id]['freq']:
                role = roles['overrides'][target.id]['role']
                if 'alignment' in roles['overrides'][target.id]:
                    alignment = roles['overrides'][target.id]['alignment']
                if type(role) is dict:
                    role = random.choices(
                        list(role.keys()),
                        weights=list(role.values())
                    )[0]
                else:
                    print("not a dict")
        flip_msg = "**{user}** has died! They were **{alignment} {role}**!".format(
            user=user,
            alignment=alignment,
            role=role
        )
        await self.send_message(msg.channel, flip_msg)

    @command("^vote <@!?(\d+)>(?:\*\*)?$", access=-1, name='vote')
    async def vote(self, msg, arguments):
        await self.send_message(
            msg.channel,
            "Sorry nerd, but there's no voting in Everyone is Mafia Mafia."
        )

    @command("^[Tt]oo bad,? <@!?(\d+)>, [Ii] never miss(?:\*\*)?$", access=-1,
             name='dayvig')
    async def dayvig(self, msg, arguments):
        if msg.author.id not in self.dayvigs:
            await self.send_message(
                msg.channel,
                "Sorry {}, why don't you reread your Role PM?".format(
                    msg.author.name
            ))
            return
        await self.send_message(msg.channel, "**PHASE PAUSE**")
        await asyncio.sleep(1)
        await self.shoot(msg, arguments)
        await asyncio.sleep(0.5)
        await self.send_message(msg.channel, "**PHASE UNPAUSE**")
