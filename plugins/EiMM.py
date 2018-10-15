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

from datetime import datetime
# from googleapiclient import discovery
# from httplib2 import Http
from io import BytesIO
from PIL import Image
# from oauth2client import file, client, tools


logger = logging.getLogger(__name__)

PATH = "resources/eimm/{}"
INTERVIEW_META = "interview_meta.json"


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


class InterviewMeta():
    server           = None
    question_channel = None
    # answer_channel   = None
    interviewee      = None
    questions        = {}
    salt             = None

    def load_from_dict(meta):
        self.server           = self.core.get_server(meta['server_id'])
        self.question_channel = self.core.get_channel(meta['q_channel'])
        # self.answer_channel   = self.core.get_channel(meta['a_channel'])
        self.interviewee      = self.server.get_member(meta['inteviewee'])
        self.questions        = meta['questions']
        self.salt             = meta['salt']

    def load_fresh(self, question_channel, interviewee):
        if self.server is None:
            self.server = question_channel.server
        if self.salt is None:
            self.salt = random.randint(1, 99999999)
        self.question_channel = question_channel
        self.interviewee      = interviewee
        self.questions        = {}

    def to_dict(self):
        meta = {
            'server_id': self.server.id,
            'q_channel': self.question_channel.id,
            # 'a_channel': self.answer_channel.id,
            'interviewee': self.interviewee.id,
            'questions': self.questions,
            'salt': self.salt
        }
        return meta

    def dump(self, filepath=PATH.format(INTERVIEW_META)):
        meta = self.to_dict()
        with open(filepath) as metafile:
            json.dump(meta, metafile)


class EiMM(Plugin):
    async def activate(self):
        self.dayvigs = []
        with open(PATH.format('dayvig.json'), 'r') as dayvig:
            self.dayvigs = json.load(dayvig)
        with open(PATH.format('ganon.json'),  'r') as ganon:
            self.ganons = json.load(ganon)
        with open(PATH.format('conquerors.json'),  'r') as conquerors:
            self.conquerors = json.load(conquerors)
        try:
            with open(PATH.format(INTERVIEW_META),  'r') as meta:
                iv_meta = json.load(meta)
                self.interview = InterviewMeta.load_from_dict(iv_meta)
        except FileNotFoundError:
            self.interview = None

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
        await self.send_message(msg.channel, "**PHASE PAUSE**")
        await asyncio.sleep(1.5)
        await self.shoot(msg, arguments)
        await asyncio.sleep(1)
        await self.send_message(msg.channel, "**PHASE UNPAUSE**")

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
                f"**{ganon} There shall be no heroes today {ganon}**"
            )
        ]
        for reply in replies:
            await self.send_message(msg.channel, reply)
            await asyncio.sleep(0.5)
        await self.send_message(msg.channel, "**PHASE PAUSE**")
        await asyncio.sleep(1.5)
        await self.shoot(msg, arguments)
        await asyncio.sleep(1)
        await self.send_message(msg.channel, "**PHASE UNPAUSE**")

    @command("^(?:step on|conquer) <@!?\d+>$", access=-1, name='step')
    async def step_on(self, msg, arguments):
        victim = None
        if msg.mentions[0].id not in self.conquerors:
            await self.send_message(msg.channel,
                                    "Didn't you mean to step on someone else?")
            return
        if msg.author.id not in self.conquerors[msg.mentions[0].id]['heels']:
            await self.send_message(
                msg.channel,
                "Sorry, but you're not wearing the right heels for this."
            )
            return
        victim = msg.mentions[0]
        if 'role' in self.conquerors[msg.mentions[0].id]:
            role = self.conquerors[msg.mentions[0].id]['role']
        else:
            role = 'Pancake'
        if type(victim) is not discord.Member or victim.nick is None:
            victim_name = victim.name
        else:
            victim_name = victim.nick
        flip_msg = "**{user}** has died! They were **{alignment} {role}**!".format(
            user=victim_name,
            alignment='Mafia',
            role=role
        )
        em = discord.Embed(color=victim.color)
        em.set_image(url='https://i.imgur.com/jTs7pRq.gif')
        await self.send_message(msg.channel, flip_msg, embed=em)

    @command("^iv setup <@!?\d+>$", access=700, name='interview setup',
             doc_brief="`iv setup <@user>`: Sets up an interview for "
             "<user>, with the secret questions in the current channel.")
    async def setup_question_channel(self, msg, arguments):
        if self.interview is None:
            await self.send_message(msg.channel,
                "Setting up interviews for the first time.")
            self.interview = InterviewMeta()
        else:
            old_interview = self.interview.to_dict()
            old_interview.pop('salt')
            filepath = PATH.format('old_interviews/{}.json'.format(
                self.interview.interviewee.name))
            with open(filepath, 'w') as archive_file:
                json.dump(old_interview, archive_file)

        self.interview.load_fresh(msg.channel, msg.mentions[0])
        filepath = PATH.format(INTERVIEW_META.format(
            self.interview.interviewee.name))
        with open(filepath, 'w') as archive_file:
            json.dump(self.interview.to_dict(), archive_file)
        # if self.interview.answer_channel is not None:
        #     achn = self.interview.answer_channel.mention
        # else:
        #     achn = None
        reply = (
            "**New interview setup:**\n"
            "Interviewee: {user}\n"
            "Question Channel: {qchn}\n"
            # "Answer Channel: {achn}"
        ).format(user=str(self.interview.interviewee),
                 qchn=self.interview.question_channel.mention,
                 # achn=achn)
                 )
        await self.send_message(msg.channel, reply)

    @command("^ask (.+)", access=-1, name='interview ask',
             doc_brief="`ask <question>`: Submits <question> for the current "
             "interview.")
    async def ask_question(self, msg, arguments):
        if self.interview is None:
            await self.send_message(msg.channel,
                                    "Interviews haven't been set up yet.")
            return
        question = {
            'question':    arguments[0],
            'author_id':   msg.author.id,
            'author_name': msg.author.name,
            'timestamp':   msg.timestamp.timestamp
        }
        if msg.author.id in self.interview.questions:
            self.interview.questions[msg.author.id].append(question)
        else:
            self.interview.questions[msg.author.id] = [question]
        self.interview.dump()

        em = discord.Embed(
            title="{interviewee} interview",
            color=self.interview.interviewee.color,
            description=arguments[0],
            timestamp=msg.timestamp
        )
        em.set_thumbnail(url=self.interview.interviewee.avatar_url)
        em.set_author(
            name=quote['name'],
            icon_url=msg.author.avatar_url
        )
        em.set_footer(
            text="Question #{}".format(len(self.interview.questions[msg.author.id])),
        )

        await self.send_message(self.interview.question_channel, embed=em)

    # @command("^submit (.*)$", access=-1, name='submit',
    #          doc_brief="`submit <question here>`: Submits a question for EiMM "
    #          "interviews")
    # async def submit_question(self, msg, arguments):
    #     SCOPES = [
    #         'https://www.googleapis.com/auth/analytics.readonly',
    #         'https://www.googleapis.com/auth/drive',
    #         'https://www.googleapis.com/auth/spreadsheets'
    #     ]
    #
    #     store = file.Storage('token.json')
    #     creds = store.get()
    #     if not creds or creds.invalid:
    #         flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    #         creds = tools.run_flow(flow, store)
    #     service = discovery.build('sheets', 'v4', http=creds.authorize(Http()))
    #
    #     # with open(PATH.format('interview_meta.json'), 'r') as meta:
    #     #     interview_meta = json.load(meta)
    #     interview_meta = {
    #         'uid':            '100165629373337600',
    #         'name':           'euklyd',
    #         'spreadsheet_id': '1kZP1k1DNv0E9D4cIq13bFgoJWqQsJJguE46He-QqwKE',
    #         'sheet_id':       '0'
    #     }
    #     interviewee_uid   = interview_meta['uid']
    #     interviewee_uname = interview_meta['name']
    #     spreadsheet_id    = interview_meta['spreadsheet_id']
    #     sheet_id          = interview_meta['sheet_id']
    #
    #     data = [
    #         datetime.now().isoformat(),
    #         interviewee_uid,
    #         interviewee_uname,
    #         msg.author.id,
    #         msg.author.name,
    #         arguments[0]
    #     ]
    #
    #     range_            = 'A1:F100000'
    #     value_input_option= 'USER_ENTERED'
    #     body = {'values': data}
    #
    #     result = service.spreadsheets().values().update(
    #         spreadsheetId=spreadsheet_id, range=range_,
    #         valueInputOption=value_input_option, body=body
    #     ).execute()
