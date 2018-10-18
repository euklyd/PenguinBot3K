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
import os
import random
import requests

from datetime import datetime
from io import BytesIO
from PIL import Image
from oauth2client.service_account import ServiceAccountCredentials


logger = logging.getLogger(__name__)

PATH = 'resources/eimm/{}'
INTERVIEW_META  = 'interview_meta.json'
SHEETS_SECRET   = 'resources/eimm/client_secret.json'
INTERVIEW_SHEET = 'EiMM Interviews'
SCOPE           = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]


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


def interview_embed(question, interview, msg):
    asker = msg.server.get_member(question['author_id'])
    if asker is None:
        asker_nick = question['author_name']
        asker_url  = question['author_avatar']
    else:
        asker_nick = get_nick_or_name(asker)
        asker_url  = asker.avatar_url
    em = discord.Embed(
        title="{} interview".format(get_nick_or_name(interview.interviewee)),
        color=interview.interviewee.color,
        description=question['question'],
        timestamp=question['timestamp']
    )
    em.set_thumbnail(url=asker_url)
    em.set_author(
        name=asker_nick,
        icon_url=asker_url
    )
    em.set_footer(
        # text="Question #{}".format(len(interview.questions)),
        text="Question #{}".format(interview.user_questions[msg.author.id]),
        icon_url=interview.interviewee.avatar_url
    )
    return em


class InterviewMeta():
    server           = None
    question_channel = None
    answer_channel   = None
    interviewee      = None
    # questions        = []
    user_questions   = {}
    salt             = None
    opt_outs         = set()
    votes            = {}

    def load_from_dict(meta, core):
        iv_meta = InterviewMeta()
        iv_meta.server           = core.get_server(meta['server_id'])
        iv_meta.question_channel = core.get_channel(meta['q_channel'])
        if 'a_channel' in meta:
            iv_meta.answer_channel   = core.get_channel(meta['a_channel'])
        iv_meta.interviewee      = iv_meta.server.get_member(meta['interviewee'])
        # iv_meta.questions        = meta['questions']
        iv_meta.user_questions   = meta['user_questions']
        iv_meta.salt             = meta['salt']
        iv_meta.opt_outs         = set(meta['opt_outs'])
        iv_meta.votes            = meta['votes']
        # logger.info(iv_meta.to_dict())
        return iv_meta

    @property
    def total_questions(self):
        total_qs = 0
        for user_qs in self.user_questions.values():
            total_qs += user_qs
        return total_qs

    def load_fresh(self, question_channel, interviewee):
        if self.server is None:
            self.server = question_channel.server
        if self.salt is None:
            self.salt = random.randint(1, 99999999)
        self.question_channel = question_channel
        self.interviewee      = interviewee
        # self.questions        = []
        self.user_questions   = {}

    def to_dict(self):
        meta = {
            'server_id':      self.server.id,
            'q_channel':      self.question_channel.id,
            'a_channel':      self.answer_channel.id,
            'interviewee':    self.interviewee.id,
            # 'questions': self.questions,
            'user_questions': self.user_questions,
            'salt':           self.salt,
            'opt_outs':       list(self.opt_outs),
            'votes':          self.votes
        }
        return meta

    def increment_question(self, user):
        if user.id in self.user_questions:
            self.user_questions[user.id] += 1
        else:
            self.user_questions[user.id] = 1

    def dump(self, filepath=PATH.format(INTERVIEW_META)):
        meta = self.to_dict()
        with open(filepath, 'w') as metafile:
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
                self.logger.info("loaded interview meta")
                self.interview = InterviewMeta.load_from_dict(
                    iv_meta, self.core)
        except FileNotFoundError:
            self.logger.warning("couldn't find interview meta, loading new")
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

    @command("^(?:step on|conquer) <@!?\d+>$", access=-1, name='step on')
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

    @command("^iv setup <@!?\d+>$", access=700, name='iv setup',
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
            if not os.path.exists(os.path.dirname(filepath)):
                try:
                    os.makedirs(os.path.dirname(filepath))
                except OSError as e: # Guard against race condition
                    if e.errno != errno.EEXIST:
                        raise
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

    @command("^iv setup answers", access=700, name='iv setup answers',
             doc_brief="`iv setup answers`: Sets the answer channel to the "
             "current channel.")
    async def setup_answer_channel(self, msg, arguments):
        self.interview.answer_channel = msg.channel
        self.interview.dump()
        reply = (
            "**New interview setup:**\n"
            "Interviewee: {user}\n"
            "Question Channel: {qchn}\n"
            "Answer Channel: {achn}"
        ).format(user=str(self.interview.interviewee),
                 qchn=self.interview.question_channel.mention,
                 achn=self.interview.answer_channel.mention)
        await self.send_message(msg.channel, reply)

    @command("^ask[ \n](.+)", access=-1, name='ask',
             doc_brief="`ask <question>`: Submits <question> for the current "
             "interview.")
    async def ask(self, msg, arguments):
        if self.interview is None:
            await self.send_message(msg.channel,
                                    "Interviews haven't been set up yet.")
            return
        question = {
            'question':      msg.content[4:],  # i hope this works
            'author_id':     msg.author.id,
            'author_name':   msg.author.name,
            'author_avatar': msg.author.avatar_url,
            'timestamp':     msg.timestamp
        }
        # self.interview.questions.append(question)

        creds   = ServiceAccountCredentials.from_json_keyfile_name(
            SHEETS_SECRET, SCOPE)
        client  = gspread.authorize(creds)
        sheet   = client.open('EiMM Interviews').sheet1
        # records = sheet.get_all_records()

        self.interview.increment_question(msg.author)

        sheet.append_row(
            [
                datetime.utcnow().strftime('%m/%d/%Y %H:%m:%S'),
                datetime.utcnow().timestamp(),
                str(msg.author),
                msg.author.id,
                self.interview.user_questions[msg.author.id],
                msg.content[4:]
            ]
        )
        self.interview.dump()

        em = interview_embed(question, self.interview, msg)
        await self.send_message(self.interview.question_channel, embed=em)
        await self.add_reaction(msg, '✅')

    @command("^(mask|multi-ask)\n(.+)", access=-1, name='interview multi-ask',
             doc_brief="`multi-ask <list of questions on separate lines>: "
             "Submits multiple questions for the current interview.",
             doc_detail="Submits multiple questions for the current interview. "
             "Syntax:```\nmulti-ask\n<question 1>\n<question 2>\n...```"
             "This will submit each <question> separately for the current "
             "interviewee to answer. *Note that there can't be a question on "
             "the same line as the `multi-ask` command; the first question "
             "must be on the second line.*")
    async def mask(self, msg, arguments):
        if self.interview is None:
            await self.send_message(msg.channel,
                                    "Interviews haven't been set up yet.")
            return

        if arguments[0] == 'mask':
            content = msg.content[5:]
        else:
            content = msg.content[10:]  # strip command name
        questions = content.split('\n')

        creds   = ServiceAccountCredentials.from_json_keyfile_name(
            SHEETS_SECRET, SCOPE)
        client  = gspread.authorize(creds)
        sheet   = client.open('EiMM Interviews').sheet1

        for question_text in questions:
            if question_text == '':
                continue
            question = {
                'question':      question_text,
                'author_id':     msg.author.id,
                'author_name':   msg.author.name,
                'author_avatar': msg.author.avatar_url,
                'timestamp':     msg.timestamp
            }
            self.interview.increment_question(msg.author)

            sheet.append_row(
                [
                    datetime.utcnow().strftime('%m/%d/%Y %H:%m:%S'),
                    datetime.utcnow().timestamp(),
                    str(msg.author),
                    msg.author.id,
                    self.interview.user_questions[msg.author.id],
                    question_text
                ]
            )
            self.interview.dump()

        composite_question = {
            'question':      content,
            'author_id':     msg.author.id,
            'author_name':   msg.author.name,
            'author_avatar': msg.author.avatar_url,
            'timestamp':     msg.timestamp
        }
        em = interview_embed(composite_question, self.interview, msg)
        await self.send_message(self.interview.question_channel, embed=em)
        await self.add_reaction(msg, '✅')

    @command("^question (\d+)", access=-1, name='interview retrieve',
             doc_brief="`question <#>`: Retrieves the specified question and "
             "posts it in the answer channel.")
    async def get_question(self, msg, arguments):
        if msg.author.id != self.interview.interviewee.id:
            await self.send_message(msg.channel,
                "You must be the interviewee to use this command.")
            return
        if self.interview.answer_channel is None:
            await self.send_message(msg.channel,
                "The answer channel is not yet set up.")
            return
        em = interview_embed(
            self.interview.questions[int(arguments[0]) - 1],
            self.interview,
            msg
        )
        await self.send_message(self.interview.answer_channel, embed=em)

    @command("^iv stats( <@!?\d+>)?$", access=-1, name='iv stats',
             doc_brief="`iv stats <@user>`: Retrieves the number of questions "
             "`user` has asked, and the total number of questions.")
    async def iv_stats(self, msg, arguments):
        if len(msg.mentions) > 0:
            user = msg.mentions[0]
        else:
            user = msg.author
        reply = '**{}** has asked **{}** `{}` questions out of `{}` total.'.format(
            user,
            self.interview.interviewee,
            self.interview.user_questions[user.id],
            self.interview.total_questions
        )
        await self.send_message(msg.channel, reply)

    @command("^opt[ -](in|out)$", access=-1, name='opt',
             doc_brief="`opt [in/out]`: Opt-in or-out of interviews "
             "nominations. Default is opted-in.")
    async def opt(self, msg, arguments):
        if arguments[0] == 'in':
            if msg.author.id not in self.interview.opt_outs:
                reply = "**{}**, you're already opted-in to interviews."
            else:
                self.interview.opt_outs.remove(msg.author.id)
                reply = "**{}**, you're now opted-in to interviews."
        elif arguments[0] == 'out':
            if msg.author.id in self.interview.opt_outs:
                reply = "**{}**, you're already opted-out of interviews."
            else:
                self.interview.opt_outs.add(msg.author.id)
                reply = "**{}**, you're now opted-out of interviews."
        else:
            reply = "**{}**, something went wrong here with your opting."
        await self.send_message(msg.channel, reply.format(msg.author))

    @command("^(nom|nominate)(:? <@!?\d+>){1:3}$", access=-1, name='nominate',
             doc_brief="`nominate <@user1> [<@user2>] [@user3]`: Nominate up "
             "to three users for interviews. If you've already made "
             "nominations, they will all be replaced.")
    async def nominate(self, msg, arguments):
        votes = list(set([mention.id for mention in msg.mentions]))
        self.interview.votes[msg.author] = votes
        await self.add_reaction(msg, '✅')

    @command("^votals$", access=-1, name='votals',
             doc_brief="`votals`: Calculates current votals for interview "
             "nominations.")
    async def votals(self, msg, arguments):
        votals = {}
        for votes in self.votes.values():
            for vote in votes:
                if vote in votals:
                    votals[vote] += 1
                else:
                    votals[vote] = 1
        sorted_votals = sorted(votals.items(), key=lambda x: x[1])
        reply = "**__Votals__**\n"
        for nom in sorted_votals:
            reply += "**{}:** {}".format(msg.server.get_member(nom[0]), nom[1])

        if msg.author.id in self.interview.votes:
            reply += "You are currently voting for: "
            for vote in self.interview.votes[msg.author.id]:
                reply += "{}, ".format(msg.server.get_member(vote))
            reply = reply[:-2]

        await send_message(msg.channel, reply)
