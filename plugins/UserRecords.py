"""
    Plugin Name : UserRecords
    Plugin Version : 0.1

    Description:
        Allow users to store records corresponding to themselves,
        e.g. Steam IDs, Nintendo Friend Codes, etc.

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
import os
import random

logger = logging.getLogger(__name__)

path = "resources/user-records/{}"


def fehstr(entry):
    if 'memo' in entry:
        fs = "**{uname}:** `{fehid}` *({memo})*".format(
            uname=entry['uname'],
            fehid=entry['fehid'],
            memo=entry['memo']
        )
    else:
        fs = "**{uname}:** `{fehid}`".format(
            uname=entry['uname'],
            fehid=entry['fehid']
        )
    return fs


class UserRecords(Plugin):
    async def activate(self):
        self.feh = {}
        try:
            with open(path.format("feh.json"), 'r') as fehfile:
                self.feh = json.load(fehfile)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.feh = {}

    @command("^feheroes add (\d+)(?: (.+))?$",
             access=-1, name='feheroes',
             doc_brief="`feheroes add <id> [<name>]`: Record or modify your "
             "FE Heroes ID, and, optionally, the name of your avatar.")
    async def feh_add(self, msg, arguments):
        id = arguments[0]
        memo = arguments[1]

        entry = {
            'uid': msg.author.id,
            'uname': msg.author.name,
            'fehid': id,
            'server': msg.server.id
        }
        if memo is not None:
            entry['memo'] = memo

        old = None
        if msg.author.id in self.feh:
            old = self.feh[msg.author.id]
        self.feh[msg.author.id] = entry

        with open(path.format("feh.json"), 'w+') as fehfile:
            self.logger.info("updated feh entry for {}: {}".format(msg.author, entry))
            json.dump(self.feh, fehfile, indent=2)
        if old is None:
            await self.send_message(
                msg.channel,
                "Added\n    {}\nto the FE Heroes record.".format(fehstr(entry))
            )
        else:
            await self.send_message(
                msg.channel,
                "Added\n    {}\nto the FE Heroes record, replacing\n    {}".format(fehstr(entry), fehstr(old))
            )

    @command("^feheroes(?: list)$",
             access=-1, name='feheroes',
             doc_brief="`feheroes list`: List stored FE Heroes IDs for this "
             "server.")
    async def feh_list(self, msg, arguments):
        reply = "**FE Heroes Friend Codes**:\n\n"
        fehlist = []
        for uid in self.feh:
            fehlist.append((self.feh[uid]['uname'].lower(), self.feh[uid]))
        fehlist.sort()
        fehlist = [entry for (key, entry) in fehlist]
        for entry in fehlist:
            reply += fehstr(entry) + "\n"
        reply += (
            "\nTo or modify your own FE Heroes Friend Code, you can use "
            "`{} feheroes add <code>`. Optionally, you can add the name of "
            "your avatar as well with `{} feheroes add <friend code> <name>`."
        )
        await self.send_message(msg.channel, reply)
