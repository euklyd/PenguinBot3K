"""
    Plugin Name : Interview
    Plugin Version : 0.1

    Description:
        Infrastructure for running an AMA-style interview on Discord.

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
import errno
import gspread
import json
import logging
import random
import re
import requests

from datetime import datetime, timezone
from io import BytesIO
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint


logger = logging.getLogger(__name__)

SHEETS_SECRET   = 'resources/eimm/client_secret.json'
INTERVIEW_SHEET = 'EiMM Passwords'
SCOPE           = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

USER_ID   = 'Discord Snowflake'
NAME      = 'Name'
PASSWORD  = 'Password'
TIMESTAMP = 'Timestamp'

COLS = {
    USER_ID:   'A',
    NAME:      'B',
    PASSWORD:  'C',
    TIMESTAMP: 'D'
}

GREENTICK = None
REDTICK = None


def get_sheet(sheet_name=INTERVIEW_SHEET):
    creds   = ServiceAccountCredentials.from_json_keyfile_name(
        SHEETS_SECRET, SCOPE)
    client  = gspread.authorize(creds)
    sheet   = client.open(sheet_name)
    return sheet


class Passwords(Plugin):
    async def activate(self):
        global GREENTICK
        global REDTICK
        GREENTICK = self.core.emoji.any_emoji(['greentick'])
        REDTICK   = self.core.emoji.any_emoji(['redtick'])
        # This isn't part of interview meta because state can be saved
        # just fine using only the sheet.
        self.sheet = get_sheet().sheet1
        records    = self.sheet.get_all_records()
        self.users = {}
        for i, record in enumerate(records):
            row = i+2
            self.users[str(record[USER_ID])] = row

    def update_sheet(self, user, password):
        '''
        user is a discord.User, password is a string

        returns None if success, False if fail
        '''
        if user.id in self.users:
            cell_list = self.sheet.range(
                f'{COLS[NAME]}{self.users[user.id]}:{COLS[TIMESTAMP]}{self.users[user.id]}'
            )
            cell_list[0].value = str(user)
            cell_list[1].value = password
            cell_list[2].value = datetime.utcnow().strftime('%m/%d/%Y %H:%M:%S')
            self.sheet.update_cells(cell_list)
            logger.info('updated pw')
            # self.sheet.update_acell(
            #     f'{PASSWORD}{self.users[user.id]}',
            #     password
            # )
            # self.sheet.update_acell(
            #     f'{NAME}{self.users[user.id]}',
            #     str(user)
            # )
            # self.sheet.update_acell(
            #     f'{TIMESTAMP}{self.users[user.id]}',
            #     datetime.utcnow().timestamp()
            # )
        else:
            self.sheet.append_row([
                user.id,
                str(user),
                password,
                datetime.utcnow().strftime('%m/%d/%Y %H:%M:%S')
            ])
            self.sheet = get_sheet().sheet1
            self.users[user.id] = self.sheet.row_count
        return None


    @command("^set password", access=-1, name='set password')
    async def set_password(self, msg, arguments):
        if not msg.channel.is_private:
            await self.send_message(
                msg.channel,
                'This channel is not private! This command can only be used in DMs.'
            )
            await self.add_reaction(msg, REDTICK)
            return
        if msg.author.id in self.users:
            reply = 'You already have a password set; setting a new one will overwrite it.\n'
        else:
            reply = 'You do not currently have a password set; this will create a new one for you.\n'
        await self.send_message(msg.channel, reply)

        finished = 'n'
        while finished != 'y' and finished != 'Y':
            reply = 'Respond to this message with your new password. *Please do not use a password you use elsewhere, as EiMM staff will be able to read it.*'
            await self.send_message(msg.channel, reply)
            resp = await self.core.wait_for_message(
                timeout=3600,
                channel=msg.channel
            )
            password = resp.content
            await self.send_message(
                msg.channel,
                f'`{password}`; is this correct? [y/n]'
            )
            resp = await self.core.wait_for_message(
                timeout=3600,
                channel=msg.channel
            )
            finished = resp.content

        self.update_sheet(msg.author, password)
        await self.send_message(msg.channel, 'Your password has been updated.')
