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
import errno
import gspread
import json
import logging
import operator
import os
import pprint
import random
import re
import requests
import zipfile

from datetime import datetime
from imgurpython.client import ImgurClientRateLimitError
from imgurpython.helpers.error import ImgurClientError
from io import BytesIO
from munkres import Munkres, DISALLOWED
from PIL import Image
from oauth2client.service_account import ServiceAccountCredentials


logger = logging.getLogger(__name__)

PATH           = 'resources/eimm/{}'
SHEETS_SECRET  = 'resources/interview/client_secret.json'
PROFILE_SHEET  = 'EiMM Community Profiles'
SCOPE          = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
HEADINGS_MAP   = None
PROFILE_FIELDS = [
    'Also Known As', 'Pronouns', 'Home Community',
    'Country', 'Timezone (in UTC)', 'Birthday', # 'Age Range',
    'Favorite EiMM Game?', 'Favorite EiMM Role?',
    'Favorite type of EiMM?', 'About Me'
]
UPDATABLE_FIELDS = [
    'Discord ID',
    # 'UID',
    # 'Primary Name',
    'Also Known As',
    'Pronouns',
    'Home Community',
    'Country',
    'Timezone (in UTC)',
    # 'Birth year',
    'Birthday',
    # 'Age',
    # 'Age Range',
    'Student?',
    'Favorite EiMM Game?',
    'Favorite EiMM Role?',
    'Favorite type of EiMM?'
]

UPDATABLE_FIELDS = {
    'Discord ID': {'regex': r'.*#\d{4}', 'char_limit': 100},
    # 'UID',
    'Primary Name': {'regex': '.*', 'char_limit': 100},
    'Also Known As': {'regex': '.*', 'char_limit': 100},
    'Pronouns': {'choice': ['they/them/their/theirs/themself', 'she/her/her/hers/herself', 'he/him/his/his/himself'], 'char_limit': 100},
    'Home Community': {'choice': [], 'char_limit': 100},
    'Country': {'choice': [], 'char_limit': 100},
    'Timezone (in UTC)': {'regex': '', 'char_limit': 100},
    # 'Birth year',
    'Birthday': {'regex': '', 'char_limit': 100},
    # 'Age',
    # 'Age Range',
    'Student?': {'regex': '[yYnN]', 'char_limit': 100},
    'Favorite EiMM Game?': {'choice': [], 'char_limit': 100},
    'Favorite EiMM Role?': {'choice': [], 'char_limit': 100},
    'Favorite type of EiMM?': {'choice': [], 'char_limit': 100}
}

GREENTICK = None
REDTICK = None


# def select_option(bot, iterable):
#


class ValidateProfile():
    def discord_id(user, arg=None):
        return user.id

    def aka(user, arg=None):
        if arg is None or arg == '':
            return ''
        return arg

    def pronouns(user, arg=None):
        if arg is None or arg == '':
            return ''


def get_sheet(sheet_name=PROFILE_SHEET):
    creds   = ServiceAccountCredentials.from_json_keyfile_name(
        SHEETS_SECRET, SCOPE)
    client  = gspread.authorize(creds)
    sheet   = client.open(sheet_name)
    return sheet


def get_first_sheet(sheet_name=PROFILE_SHEET):
    return get_sheet().sheet1


def generate_headings(sheet):
    headings = sheet.row_values(1)
    if len(headings) > 26:
        # Don't use more than 26 columns please, you'd be a bad person
        raise RuntimeError("i don't want to handle more than 26 columns, go away")
    column = 'A'
    heading_map = {}
    for heading in headings:
        heading_map[heading] = column
        column = chr(ord(column) + 1)
    return heading_map


def record_by_key_value(sheet, key, value):
    if key not in sheet.row_values(1):
        raise KeyError(f"{key} not found in the sheet's headings")
    for record in records:
        if str(record[key]) == str(value):
            return record
    return None


def record_cell_by_key_value(sheet, key, value):
    if key not in sheet.row_values(1):
        raise KeyError(f"{key} not found in the sheet's headings")
    headings = generate_headings(sheet)
    for row, record in enumerate(records):
        if str(record[key]) == str(value):
            return record, f'{headings[key]}{row+2}'
    return None


# def validate_profile_input(key, value):
#     switcher = {
#         ''
#     }
#     validate =


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


def get_nick_or_name(member):
    if member.nick is None:
        return member.name
    return member.nick


class EiMM(Plugin):
    async def activate(self):
        self.dayvigs = []
        with open(PATH.format('dayvig.json'), 'r') as dayvig:
            self.dayvigs = json.load(dayvig)
        with open(PATH.format('ganon.json'),  'r') as ganon:
            self.ganons = json.load(ganon)
        with open(PATH.format('conquerors.json'),  'r') as conquerors:
            self.conquerors = json.load(conquerors)
        self.plus_ultra = {}
        with open(PATH.format('cats.json'),  'r') as cats:
            self.cats = json.load(cats)

        global GREENTICK
        global REDTICK
        GREENTICK = self.core.emoji.any_emoji(['greentick'])
        REDTICK   = self.core.emoji.any_emoji(['redtick'])

        sheet = get_first_sheet(sheet_name=PROFILE_SHEET)
        global HEADINGS_MAP
        HEADINGS_MAP = generate_headings(sheet)

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
             doc_brief="`shoot <@user>`: Murders the fuck out of <user>.")
    async def shoot(self, msg, arguments):
        target = msg.mentions[0]
        modifier = None
        base = None
        addition = None
        with open(PATH.format('roles.json'), 'r') as roledict:
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
        role = ''
        alignment = 'Mafia'
        if modifier is not None:
            role += modifier + ' '
        role += base
        if addition is not None:
            role += ' + {}x {}'.format(random.randint(1, 3), addition)
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
                    print('not a dict')
        flip_msg = '**{user}** has died! They were **{alignment} {role}**!'.format(
            user=user,
            alignment=alignment,
            role=role
        )
        await self.send_message(msg.channel, flip_msg)

    @command("^[Tt]oo bad,? <@!?(\d+)> ?,? [Ii] never miss(?:\*\*)?$", access=-1,
             name='dayvig')
    async def dayvig(self, msg, arguments):
        if msg.author.id not in self.dayvigs:
            await self.send_message(
                msg.channel,
                "Sorry {}, why don't you reread your Role PM?".format(
                    msg.author.name
            ))
            return
        await self.send_message(msg.channel, '**PHASE PAUSE**')
        await asyncio.sleep(1.5)
        await self.shoot(msg, arguments)
        await asyncio.sleep(1)
        await self.send_message(msg.channel, '**PHASE UNPAUSE**')

    @command("^GANON CANNON <@!?\d+>$", access=-1, name='ganon cannon')
    async def ganon_cannon(self, msg, arguments):
        if msg.author.id not in self.ganons:
            await self.send_message(
                msg.channel,
                "Sorry {}, why don't you reread your Role PM?".format(
                    msg.author.name
            ))
            return
        ganon = self.core.emoji.any_emoji(['return_of_ganon'])
        replies = [
            (
                "Do you sleep still? Wait! Do not be so hasty, boy... I can "
                "see this peoples dreams... Memes... Memes... Memes... "
                "Memes... Memes as far as the eye can see. They are dank "
                "memes... None can skimm across them... They yield no meaning "
                "to catch... What did the host of the game say?... That the "
                "gods sealed memes away? And they left behind people who "
                "would one day awaken this place?"
            ),
            (
                "How ridiculous... So many pathetic creatures, scattered "
                "across a handful of factions, drifting on this thread like "
                "fallen leaves on a forgotten pool... What they can possibly "
                "hope to achieve? Don't you see? All of you... Your gods "
                "destroyed you! And now, I will too!"
            ),
            (
                f'**{ganon} There shall be no heroes today {ganon}**'
            )
        ]
        for reply in replies:
            await self.send_message(msg.channel, reply)
            await asyncio.sleep(0.5)
        await self.send_message(msg.channel, '**PHASE PAUSE**')
        await asyncio.sleep(1.5)
        await self.shoot(msg, arguments)
        await asyncio.sleep(1)
        await self.send_message(msg.channel, '**PHASE UNPAUSE**')

    @command("^(?:step on|conquer|STEP ON) <@!?\d+> *,?(REALLY HARD|PLUS ULTRA|gently|softly,? with grace)?$",
             access=-1, name='step on')
    async def step_on(self, msg, arguments):
        victim = None
        plus_ultra = False
        print(arguments)
        if arguments[0] is not None and msg.author.id in self.conquerors['plus ultra'] + [self.core.config.backdoor]:
            plus_ultra = True
            if 'ly' in arguments[0]:
                # catch "gently" and "softly,? with grace"
                if msg.author.id != self.core.config.backdoor:
                    await self.send_message(msg.channel, "Nice try, but things don't quite work that way.")
                    return
                else:
                    plus_ultra = False
            if msg.author.id != self.core.config.backdoor and msg.author.id in self.plus_ultra:
                diff = datetime.now() - self.plus_ultra[msg.author.id]
                if diff.days <= 1:
                    await self.send_message(msg.channel,
                                            "You're still a bit too tired for that...")
                    return
            self.plus_ultra[msg.author.id] = datetime.now()
            if msg.mentions[0].id in self.conquerors['steppees'] and 'role' in self.conquerors['steppees'][msg.mentions[0].id]:
                role = self.conquerors['steppees'][msg.mentions[0].id]['role']
            else:
                role = 'Pancake'
        elif msg.mentions[0].id in self.conquerors['steppees']:
            if 'role' in self.conquerors['steppees'][msg.mentions[0].id]:
                role = self.conquerors['steppees'][msg.mentions[0].id]['role']
            else:
                role = 'Pancake'
        elif msg.mentions[0].id not in self.conquerors:
            await self.send_message(msg.channel,
                                    "Didn't you mean to step on someone else?")
            return
        elif msg.author.id not in self.conquerors[msg.mentions[0].id]['heels']:
            await self.send_message(
                msg.channel,
                "Sorry, but you're not wearing the right heels for this."
            )
            return
        else:
            if 'role' in self.conquerors[msg.mentions[0].id]:
                role = self.conquerors[msg.mentions[0].id]['role']
            else:
                role = 'Pancake'
        victim = msg.mentions[0]
        if type(victim) is not discord.Member or victim.nick is None:
            victim_name = victim.name
        else:
            victim_name = victim.nick
        flip_msg = '**{user}** has died! They were **{alignment} {role}**!'.format(
            user=victim_name,
            alignment='Mafia',
            role=role
        )
        em = discord.Embed(color=victim.color)
        em.set_image(url='https://i.imgur.com/jTs7pRq.gif')
        if arguments[0] is not None and 'softly' in arguments[0]:
            em.description = 'https://www.youtube.com/watch?v=AH4JiIcDvkc'
        if plus_ultra:
            flip_msg = flip_msg.upper()
        # if msg.author.id in self.cats and self.cats[msg.author.id] > 0 and victim.id in self.cats['cat bearers']:
        if msg.author.id in self.cats and self.cats[msg.author.id] > 0:
            await self.send_message(msg.channel, f"You're currently immobilized by `{self.cats[msg.author.id]}` adorable, innocent kitties. Do you *really* want to disturb them...? `[y/n]`")
            m = await self.core.wait_for_message(
                timeout=300,
                author=msg.author,
                channel=msg.channel,
                check=lambda m: m.content.lower() == 'y' or m.content.lower() == 'n'
            )
            if m is None:
                return
            if m.content.lower() == 'n':
                await self.send_message(msg.channel, f'Good choice, **{msg.author}.** Your `{self.cats[msg.author.id]}` kitties continue happily purring.')
                return
            ohno = self.core.emoji.any_emoji(['ohno'])
            await self.send_message(msg.channel, f'{ohno} The kitties all scatter...')
            self.cats[msg.author.id] = 0
        await self.send_message(msg.channel, flip_msg, embed=em)

    @command("^cat +(<@!?\d+>|\d+)?$", access=100, name='cat')
    async def cat(self, msg, arguments):
        '''
        {
            "user ID 1": # of cats,
            "user ID 2": # of cats,
            ...
            "cat bearers": [
                "user ID A", "user ID B", ...
            ]
        }
        '''
        if len(msg.mentions) > 0:
            user = msg.mentions[0]
        else:
            user = msg.server.get_member(arguments[0])
        if msg.author.id not in self.cats['cat bearers']:
            await self.send_message(msg.channel, f"Sorry **{msg.author}**, you don't have any cats to gift...")
            return
        if user.id not in self.cats:
            await self.send_message(msg.channel, f'Sorry, but **{user}** is not a **Platinum Elite Member** of the Cat Fanclub™.')
            return
        self.cats[user.id] += 1
        with open(PATH.format('cats.json'),  'w') as cats:
            json.dump(self.cats, cats, indent=2)
        ohmy = self.core.emoji.any_emoji(['ohmy'])
        await self.send_message(msg.channel, f"Wow **{msg.author}**, you're such a good friend! You've visited **{user}** with an adorable cat! {ohmy}")

    @command("^checkcats$", access=1000, name='checkcats')
    async def checkcats(self, msg, arguments):
        cats_msg = ''
        for userid, numcats in self.cats.items():
            try:
                user = await self.get_user_info(userid)
            except discord.NotFound:
                continue
            except discord.HTTPException:
                continue
            cats_msg += f'{user}: {numcats}\n'
        await self.send_whisper(msg.author, cats_msg)

    @command("^updateall profiles", access=1000)
    async def update_all(self, msg, arguments):
        # Automated way to update all the community profiles with Discord ID
        # snowflakes in addition to username#disc combos.
        # NOTE: Not for regular use.
        sheet   = get_first_sheet()
        records = sheet.get_all_records()
        col     = HEADINGS_MAP['UID']
        total   = 0
        for user in msg.server.members:
            for i, record in enumerate(records):
                if record['Discord ID'].lower() == str(user).lower() and record['UID'] == '':
                    row = i + 2
                    sheet.update_acell(f'{col}{row}', user.id)
                    total += 1
        await self.send_message(msg.channel, f'Updated {total} profile entries with ID snowflakes.')

    @command("^eimmprof ?(<@!?\d+>|\d+)?$", access=1000, name='eimmprofile')
    async def eimmprofile(self, msg, arguments):
        if arguments[0] is None:
            # get own profile
            uid = msg.author.id
        elif len(msg.mentions) == 0:
            # get user profile by ID
            uid = arguments[0]
        else:
            # get user profile by mention
            uid = msg.mentions[0].id
        user = msg.server.get_member(uid)
        if user is None:
            user = await self.core.get_user_info(uid)

        sheet   = get_first_sheet()
        records = sheet.get_all_records()
        profile = None
        if uid == self.core.user.id:
            profile = 'penguin override'
        elif 'UID' in sheet.row_values(1):
            # search by discord id snowflake
            for record in records:
                # print(record['UID'], type(record['UID']), user.id, type(user.id))
                if str(record['UID']) == user.id:
                    profile = record
                    break
            if profile is None:
                await self.send_message(msg.channel, 'User not found.')
                return
        else:
            # search by discord username#disc combo
            for record in records:
                if record['Discord ID'].lower() == str(user).lower():
                    profile = record
                    break
            if profile is None:
                await self.send_message(msg.channel, 'User not found.')
                return
        if type(user) is discord.Member:
            em = discord.Embed(
                # title='{} interview'.format(get_nick_or_name(interview.interviewee)),
                title='User Profile',
                color=user.color,
                # timestamp=user.joined_at
            )
        else:
            em = discord.Embed(
                # title='{} interview'.format(get_nick_or_name(interview.interviewee)),
                title='User Profile',
                color=msg.server.get_member(self.core.user.id).color
            )
        em.set_thumbnail(url=user.avatar_url)
        em.set_author(
            name=str(user),
            icon_url=user.avatar_url
        )
        if type(user) is discord.Member:
            em.set_footer(
                text='Server member since {}'.format(user.joined_at.date()),
                icon_url=user.avatar_url
            )

        if profile == 'penguin override':
            em.description = (
                "🐧 King Dedede 🐧 is definitely top tier. The king's got it all: disjoint ⚔, power 💪, recovery ✈, and damaging throw combos 💥. He is the hardest character in the game to kill vertically ⬆💀, and with the safest and strongest ways to kill 💀 being traditionally ⬆vertical⬆, that's huge ⛰. His presence at the ledge is not to be ignored, as with clever <:gordo:407347632479010816> setups, he can cover most if not all ledge options with a potentially deadly hitbox 💀. He might be combo food 🍖, but he wants all that 💢 rage 💢 so he can kill with his safe and powerful back air 🔨🐻 even earlier than usual. An obvious member of 🐧 top tier🐧.\n"
                "🐧 THE 🐧 KING 🐧 IS 🐧 TOP 🐧 TIER 🐧"
            )
            await self.send_message(msg.channel, embed=em)
            return
        # for field, value in profile.items():
        #     if value == '' or value is None:
        #         value = '---'
        #     em.add_field(name=field, value=value)
        for field in PROFILE_FIELDS:
            if field in profile:
                value = profile[field]
            else:
                continue
            if value == '' or value is None:
                value = '---'
            em.add_field(name=field, value=value)

        await self.send_message(msg.channel, embed=em)

    # @command("^eimmprof update *(.*)$", access=1000, name='eimmprofile update')
    # async def eimmprof_update(self, msg, arguments):
    #     key = arguments[0]
    #     lowered_keys = [key.lower() for key in PROFILE_FIELDS]
    #     if key is None or key.lower() not in lowered_keys:
    #         # headings = list(HEADINGS_MAP.keys())
    #         headings = PROFILE_FIELDS
    #         await self.send_message(
    #             msg.channel,
    #             f'The values you can update are `{', '.join(headings)}`.'
    #         )
    #         return
    #     key = PROFILE_FIELDS[lowered_keys.index()]

    @command("^sadcat ?(\w+)?$", access=-1, name='sadcat',
             doc_brief="`sadcat`: posts a random sad cat 😿")
    async def sadcat(self, msg, arguments):
        SADCAT_ALBUM = ['tYiOD5a', 'kSwj6F5']
        sadcats = []
        if type(SADCAT_ALBUM) is list:
            for album in SADCAT_ALBUM:
                sadcats += self.core.imgur.get_album_images(album)
        else:
            sadcats = self.core.imgur.get_album_images(SADCAT_ALBUM)
        sadcat = random.choice(sadcats)
        if arguments[0] is not None:
            for cat in sadcats:
                if cat.description is not None and cat.description.lower() == arguments[0].lower():
                    sadcat = cat
                    break
        em = discord.Embed(
            title=sadcat.description,
            color=msg.server.get_member(self.core.user.id).color
        )
        em.set_image(url=sadcat.link)
        em.set_footer(text=f'{len(sadcats)} sad cats')
        await self.send_message(msg.channel, embed=em)


    @filter("^(euklyd|iris|monde) sux$", name='mod sux', server=(
            '328399532368855041', '126104649018245123'), flags=re.IGNORECASE)
    async def mods_dont_suck(self, msg, arguments):
        # await self.send_message(msg.channel, 'nuh')
        m = await self.core.wait_for_message(
            timeout=30,
            author=msg.server.get_member('116275390695079945'),
            channel=msg.channel,
            content='agreed tbh'
        )
        if m is None:
            return
        await self.delete_message(m)
        await self.send_message(msg.channel, "...but not as much as amy")

    @filter("^amy sux$", name='amy sux', server=('328399532368855041',
            '126104649018245123'), flags=re.IGNORECASE)
    async def amy_sux(self, msg, arguments):
        # await self.send_message(msg.channel, 'nuh')
        m = await self.core.wait_for_message(
            timeout=30,
            author=msg.server.get_member('116275390695079945'),
            channel=msg.channel,
            content='<:despairein:392820084739145748>'
        )
        if m is None:
            return
        # await self.delete_message(m)
        await self.send_message(msg.channel, "**the truth cannot be silenced** 😤")

    @command("^(en|un)role <@&\d+>", access=900, name='enrole',
             doc_brief="`enrole/unrole @role <playerlist on following lines>`: "
             "Enroles/unroles an entire playerlist in the player `role`.")
    async def enrole(self, msg, arguments):
        playerlist = msg.content.splitlines()[1:]
        not_found = []
        for player in playerlist:
            name = player.rsplit('(')[0]
            if name[-1] == ' ':
                name = name[:-1]
            member = msg.server.get_member_named(name)
            if member is None:
                not_found.append(player)
                continue
            if arguments[0] == 'en':
                await self.core.add_roles(member, msg.role_mentions[0])
            else:
                await self.core.remove_roles(member, msg.role_mentions[0])
        if len(not_found) > 0:
            await self.send_message(
                msg.channel,
                'Error {}roling the following users:\n'
                '```{}```'.format(arguments[0], '\n'.join(not_found))
            )
            await self.add_reaction(msg, REDTICK)
        else:
            await self.add_reaction(msg, GREENTICK)

    @command("^dumpavis *(<@&\d+>)? *(--zip)?$", access=900, name='dumpavis',
             doc_brief="`dumpavis @role`: Creates an imgur album with the "
             "avatars of all users in `role`.")
    async def dumpavis(self, msg, arguments):
        role = None
        if len(msg.role_mentions) == 0:
            for a_role in msg.server.roles:
                if a_role.is_everyone:
                    role = a_role
                    break
            else:
                await self.send_message(msg.channel, "Couldn't find `@everyone`.")
        else:
            role = msg.role_mentions[0]
        # print([role.name for role in msg.server.roles])
        # print(role)
        # print(msg.role_mentions)
        now = datetime.utcnow()

        self.logger.info(self.core.imgur.credits)
        await asyncio.sleep(1)

        try:
            image_ids = []
            i = 0
            for member in msg.server.members:
                if role in member.roles:
                    avatar_url = member.avatar_url.replace('webp', 'png')
                    self.logger.info(f'uploading {avatar_url}')
                    img = self.core.imgur.upload_from_url(avatar_url, anon=False)
                    image_ids.append(img['id'])
                    i += 1
                    if i % 5 == 0:
                        await asyncio.sleep(0.2)
            diff = datetime.utcnow() - now
            album = self.core.imgur.create_album({
                'title': f'{role.name} avatar dump',
                'description': f'Dump of user avatars for role {role.name} on {now}',
                'privacy': 'hidden',
                # 'layout': 'grid'  # this is probably deprecated
            })
            print(album)
            url_list = '\n'.join([f'https://imgur.com/{img}' for img in image_ids])

            self.core.imgur.album_add_images(album['id'], image_ids)
            await self.send_message(
                msg.channel,
                f'Created album for {len(image_ids)} user avatars in {diff}: '
                f'<https://imgur.com/a/{album["id"]}>'
            )
        except (ImgurClientRateLimitError, ImgurClientError) as e:
            avatar_list = []
            for member in msg.server.members:
                if role in member.roles:
                    avatar_list.append(
                        (member.name, member.avatar_url.replace('webp', 'png'))
                    )

            if arguments[0] != '--zip':
                await self.send_message(
                    msg.channel,
                    f"Imgur's **fucking awful API** broke on us: `{e}`\nHave a list of URLs instead:"
                )
                STEP = 10
                for i in range(0, len(avatar_list), STEP):
                    url_list = '\n'.join([f'{avi[0]}: {avi[1]}' for avi in avatar_list[i:i+STEP]])
                    reply = f'```{url_list}```'
                    await self.send_message(
                        msg.channel,
                        reply
                    )
                return
            else:
                dirname = f'{role.name}-{now}'
                dirpath = f'/tmp/{dirname}/'
                zipname = f'/tmp/{dirname}.zip'
                files = []
                if not os.path.exists(dirpath):
                    os.makedirs(dirpath)
                self.logger.info(f'Created {dirpath}.')
                for name, url in avatar_list:
                    filename = dirpath + f'{name}.png'
                    files.append(filename)
                    response = requests.get(url)
                    self.logger.info(f'Downloaded {name}')
                    with open(filename, 'wb') as f:
                        f.write(response.content)

                self.logger.info('Downloaded files.')

                with zipfile.PyZipFile(zipname, mode='a') as avatar_zip:
                    for filename in files:
                        avatar_zip.write(filename)

                os.remove(dirpath)

    @command("^qselect (.*)$", access=900, name='qselect',
             doc_brief="`qselect <host json>`: Selects the hosts for the "
             "queue season with the application specified by `host json`.")
    async def qselect(self, msg, arguments):
        try:
            hosts = json.loads(arguments[0])
        except JSONDecodeError as e:
            await self.send_message(msg.channel, e)
            return
        assignments, picks = mod_bias_queue_algorithm(hosts)
        for host in picks:
            for i in range(0, len(host.prefs)):
                if host.prefs[i] == DISALLOWED:
                    host.prefs[i] = 'N/A'
        reply = "**The next season's host slots, in order, are...** 🥁 🥁 🥁"
        await self.send_message(msg.channel, reply)
        nums = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Finally']
        for num, host in zip(nums, assignments):
            await asyncio.sleep(5.0)
            reply = f'**{num},** `{host.name}`, with preferences `{host.prefs}`!'
            await self.send_message(msg.channel, reply)
        reply = (
            '*The full list of selected hosts, in priority order, is:*\n'
            f'```{pprint.pformat(picks)}```'
            '*("but euklyd, that\'s ugly code formatting", you may say: '
            'i\'ll fix it later u nerd)*'
            # f"```{[str(pick) + '\n' for pick in picks]}```"
        )
        await self.send_message(msg.channel, reply)

class Host():
    def __init__(self, name, prefs, prio):
        self.prefs = []
        for pref in prefs:
            if type(pref) is int:
                self.prefs.append(pref)
            elif pref == '' or pref is None:
                self.prefs.append(DISALLOWED)
            else:
                self.prefs.append(int(pref))

        self.name   = name
        self.prio   = prio

    def __repr__(self):
        prefs = [None if pref == DISALLOWED else pref for pref in self.prefs]
        return f'<name={self.name}, prefs={prefs}, prio={self.prio}>'

    def __str__(self):
        return f'{self.name} [{self.prio}]: {self.prefs}'

def mod_bias_host_selection(hosts, priority=2):
    hosts = [
        Host(
            name, prefs['prefs'], prefs['priority']
        ) for name, prefs in hosts.items()
    ]

    # Select n=2 hosts from the hosts with priority
    prio_hosts = [
        host for host in hosts if host.prio > 0
    ]
    if len(prio_hosts) > priority:
        picks = random.sample(prio_hosts, priority)
    else:
        # If there are fewer than 2 prio hosts, use as many as possible
        picks = prio_hosts

    # Don't modify the original list
    hosts_copy = list(hosts)
    for host in picks:
        hosts_copy.remove(host)

    # Separate out the rest of the hosts into normal and low priorities
    normal_hosts = [
        host for host in hosts_copy if host.prio >= 0
    ]
    low_hosts = [
        host for host in hosts_copy if host.prio < 0
    ]
    random.shuffle(normal_hosts)
    random.shuffle(low_hosts)

    # The selected hosts for the six queue slots per season are:
    # n=2 priority hosts +
    # m=4 other hosts (may or may not have prio)
    # If n<2, m increases to compensate.
    picks = picks + normal_hosts + low_hosts

    return picks

def mod_bias_hungarian_algorithm(picks, total=6):
    '''
    tl;dr Numbers go in, numbers come out.

    Uses the Hungarian Algorithm, aka Munkres Assignment Algorithm,
    to assign hosts to slots with maximum respect for preferences:
    https://en.wikipedia.org/wiki/Hungarian_algorithm
    '''
    random.shuffle(picks)

    matrix = []
    for pick in picks:
        matrix.append(pick.prefs)
    m = Munkres()
    indices = m.compute(matrix)

    assignments = [None]*(total)
    for row, col in indices:
        assignments[col] = picks[row]

    return assignments

def mod_bias_queue_algorithm(hosts, priority=2, total=6):
    '''
    Inputs:
    - dict of hosts, in the format specified at the top of this file.
    - (optional) number of hosts selected at a higher priority (default 2)
    - (optional) total number of hosts to select (default 6)

    Returns:
    - Ordered list of assigned hosts (first in the list gets slot 1, etc.)
    - Ordered list of selected hosts, in case manual assignment is needed
    '''
    picks = mod_bias_host_selection(hosts, priority=priority)
    assignments = mod_bias_hungarian_algorithm(picks[:total])
    return assignments, picks
