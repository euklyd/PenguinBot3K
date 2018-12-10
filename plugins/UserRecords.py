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


def recordstr(entry):
    if 'memo' in entry:
        print_line = '**{uname}:** `{app_id}` *({memo})*'.format(
            uname=entry['uname'],
            app_id=entry['app_id'],
            memo=entry['memo']
        )
    else:
        print_line = "**{uname}:** `{app_id}`".format(
            uname=entry['uname'],
            app_id=entry['app_id']
        )
    return print_line


def generate_add_cmd(record_name, json_file):
    async def add(self, msg, arguments):
        try:
            with open(path.format(json_file), 'r') as recordfile:
                records = json.load(recordfile)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            records = {}
        id = arguments[0]
        memo = arguments[1]

        servers = [msg.server.id]
        old = None
        if msg.author.id in records:
            old = records[msg.author.id]
            if msg.server.id in old['servers']:
                servers = [server for server in old['servers']]
            else:
                servers += [server for server in old['servers']]

        entry = {
            'uid': msg.author.id,
            'uname': msg.author.name,
            'app_id': id,
            'servers': servers
        }
        if memo is not None:
            entry['memo'] = memo

        records[msg.author.id] = entry

        with open(path.format(json_file), 'w+') as recordfile:
            json.dump(records, recordfile, indent=2)
        if old is None:
            await self.send_message(
                msg.channel,
                f'Added\n    {recordstr(entry)}\nto the {record_name} record.'
            )
        else:
            await self.send_message(
                msg.channel,
                f'Added\n    {recordstr(entry)}\nto the {record_name} record, replacing\n    {recordstr(old)}'
            )
    return add


def generate_list_cmd(record_name, json_file, cmd_name):
    async def lst(self, msg, arguments):
        try:
            with open(path.format(json_file), 'r') as recordfile:
                records = json.load(recordfile)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            records = {}
        reply = f'**__{record_name}s:__**\n\n'
        record_list = []
        for uid in records:
            if msg.server.id in records[uid]['servers']:
                # only list IDs for users in the same server
                record_list.append((records[uid]['uname'].lower() + uid, records[uid]))
        record_list.sort()
        record_list = [entry for (key, entry) in record_list]
        for entry in record_list:
            reply += recordstr(entry) + '\n'
        reply += (
            '\nTo add or modify your own {record}, you can use '
            '`{t}{cmd} add <code>`. Optionally, you can add a memo as well '
            'with `{t}{cmd} add <code> <name>`.'
        ).format(record=record_name, t=self.core.default_trigger, cmd=cmd_name)
        await self.send_message(msg.channel, reply)
    return lst


class UserRecords(Plugin):
    async def activate(self):
        # self.feh = {}
        # try:
        #     with open(path.format("feh.json"), 'r') as fehfile:
        #         self.feh = json.load(fehfile)
        # except FileNotFoundError:
        #     os.makedirs(os.path.dirname(path), exist_ok=True)
        #     self.feh = {}
        pass

    @command("^(?:fe)?heroes add (\d+)(?: (.+))?$",
             access=-1, name='feheroes',
             doc_brief="`feheroes add <id> [<name>]`: Record or modify your "
             "FE Heroes ID, and, optionally, the name of your avatar.")
    async def feh_add(self, msg, arguments):
        # id = arguments[0]
        # memo = arguments[1]
        #
        # servers = [msg.server.id]
        # old = None
        # if msg.author.id in self.feh:
        #     old = self.feh[msg.author.id]
        #     if msg.server.id in old['servers']:
        #         servers = [server for server in old['servers']]
        #     else:
        #         servers += [server for server in old['servers']]
        #
        # entry = {
        #     'uid': msg.author.id,
        #     'uname': msg.author.name,
        #     'fehid': id,
        #     'servers': servers
        # }
        # if memo is not None:
        #     entry['memo'] = memo
        #
        # self.feh[msg.author.id] = entry
        #
        # with open(path.format("feh.json"), 'w+') as fehfile:
        #     self.logger.info("updated feh entry for {}: {}".format(msg.author, entry))
        #     json.dump(self.feh, fehfile, indent=2)
        # if old is None:
        #     await self.send_message(
        #         msg.channel,
        #         "Added\n    {}\nto the FE Heroes record.".format(recordstr(entry))
        #     )
        # else:
        #     await self.send_message(
        #         msg.channel,
        #         "Added\n    {}\nto the FE Heroes record, replacing\n    {}".format(recordstr(entry), recordstr(old))
        #     )
        cmd = generate_add_cmd('FE Heroes Friend Code', 'feh.json')
        await cmd(self, msg, arguments)

    @command("^(?:fe)?heroes(?: list)?$",
             access=-1, name='feheroes',
             doc_brief="`feheroes list`: List stored FE Heroes IDs for this "
             "server.")
    async def feh_list(self, msg, arguments):
        # reply = "**__FE Heroes Friend Codes:__**\n\n"
        # fehlist = []
        # for uid in self.feh:
        #     if msg.server.id in self.feh[uid]['servers']:
        #         # only list IDs for users in the same server
        #         fehlist.append((self.feh[uid]['uname'].lower() + uid, self.feh[uid]))
        # print(fehlist)
        # fehlist.sort()
        # fehlist = [entry for (key, entry) in fehlist]
        # for entry in fehlist:
        #     reply += recordstr(entry) + "\n"
        # reply += (
        #     "\nTo add or modify your own FE Heroes Friend Code, you can use "
        #     "`{t}feheroes add <code>`. Optionally, you can add the name of "
        #     "your avatar as well with `{t}feheroes add <code> <name>`."
        # ).format(t=self.core.default_trigger)
        # await self.send_message(msg.channel, reply)
        cmd = generate_list_cmd(
            'FE Heroes Friend Code',
            'feh.json',
            'feheroes'
        )
        await cmd(self, msg, arguments)


    @command("^(?:switch|sw) add (?:SW-?)?(\d{4}-\d{4}-\d{4})(?: (.+))?$",
             access=-1, name='switch',
             doc_brief="`switch add <friendcode> [<name>]`: Record or modify "
             "your Switch Friend Code, and, optionally, the name of your Mii.")
    async def sw_add(self, msg, arguments):
        cmd = generate_add_cmd('Switch Friend Code', 'switch_codes.json')
        await cmd(self, msg, arguments)

    @command("^(?:switch|sw)(?: list)?$",
             access=-1, name='switch',
             doc_brief="`switch list`: List stored Switch Friend Codes for "
             "this server.")
    async def sw_list(self, msg, arguments):
        cmd = generate_list_cmd(
            'Switch Friend Code',
            'switch_codes.json',
            'switch'
        )
        await cmd(self, msg, arguments)
