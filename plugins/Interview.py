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
import operator
import os
import random
import requests

from datetime import datetime
from io import BytesIO
from PIL import Image
from oauth2client.service_account import ServiceAccountCredentials


logger = logging.getLogger(__name__)

PATH = 'resources/interview/{}'
INTERVIEW_META  = 'interview_meta.json'
SHEETS_SECRET   = 'resources/eimm/client_secret.json'
INTERVIEW_SHEET = 'EiMM Interviews'
SCOPE           = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]


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
        title='{} interview'.format(get_nick_or_name(interview.interviewee)),
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
        text='Question #{}'.format(interview.user_questions[msg.author.id]),
        icon_url=interview.interviewee.avatar_url
    )
    return em


def blank_answers_embed(interview, msg, asker_id):
    asker = msg.server.get_member(str(asker_id))
    if asker is None:
        asker_nick = '???'
        asker = '???'
        asker_url  = ''
    else:
        # asker_nick = get_nick_or_name(asker)
        asker_nick = asker.name
        asker_url  = asker.avatar_url
    em = discord.Embed(
        title="**{}**'s interview".format(interview.interviewee.name),
        description=' ',
        color=interview.interviewee.color
    )
    em.set_thumbnail(url=interview.interviewee.avatar_url)
    # em.set_author(
    #     name=asker_nick,
    #     icon_url=asker_url
    # )
    em.set_author(
        name=f'Asked by {asker}',
        icon_url=asker_url
    )
    return em


def add_split_field(embed, num, text):
    def split_text(text):
        if len(text) > 1000:
            pos = text[:1000].rfind(' ')
            if pos == -1:
                # catch 'what if there are no spaces'
                pos = 1000
            remainder = text[pos:]
            text = text[:pos]
        else:
            remainder = ''
        return text, remainder
    text, rem = split_text(text)
    embed.add_field(name=f'Question #{num}', value=text, inline=False)
    while rem != '':
        text, rem = split_text(rem)
        embed.add_field(name=f'Question #{num} (cont.)', value=text, inline=False)


def add_answer(embed, num, question, answer, space=True):
    BLANKSPACE = '<:blankspace:280996547708321792>'
    question = f'```{question}```'
    if space:
        answer = f'{answer}\n{BLANKSPACE}'
    if len(question) > 1000:
        question = question[:996] + '``` ```' + question[996:]
    if len(question) + len(answer) > 1000:
        add_split_field(embed, num, question)
        add_split_field(embed, num, answer)
    else:
        question_text = f'{question}\n{answer}'
        add_split_field(embed, num, question_text)


class InterviewMeta():
    server           = None
    question_channel = None
    answer_channel   = None
    interviewee      = None
    user_questions   = {}
    salt             = None
    opt_outs         = set()
    votes            = {}
    active           = True

    def load_from_dict(meta, core):
        iv_meta = InterviewMeta()
        iv_meta.server           = core.get_server(meta['server_id'])
        iv_meta.question_channel = core.get_channel(meta['q_channel'])
        if 'a_channel' in meta:
            iv_meta.answer_channel   = core.get_channel(meta['a_channel'])
        iv_meta.interviewee      = iv_meta.server.get_member(meta['interviewee'])
        iv_meta.user_questions   = meta['user_questions']
        iv_meta.salt             = meta['salt']
        iv_meta.opt_outs         = set(meta['opt_outs'])
        iv_meta.votes            = meta['votes']
        iv_meta.active           = meta['active']
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
        self.user_questions   = {}
        self.active           = True

    def to_dict(self):
        meta = {
            'server_id':      self.server.id,
            'q_channel':      self.question_channel.id,
            'a_channel':      self.answer_channel.id,
            'interviewee':    self.interviewee.id,
            'user_questions': self.user_questions,
            'salt':           self.salt,
            'opt_outs':       list(self.opt_outs),
            'votes':          self.votes,
            'active':         self.active
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


def get_sheet(sheet_name=INTERVIEW_SHEET):
    creds   = ServiceAccountCredentials.from_json_keyfile_name(
        SHEETS_SECRET, SCOPE)
    client  = gspread.authorize(creds)
    sheet   = client.open(sheet_name).sheet1
    return sheet


class Interview(Plugin):
    """
    __**PenguinBot Interview User Guide**__

    **Voting**

    You can nominate 1-3 users with `##nominate`. For example, `##nominate @Ampharos#1651 @Iris#5134 @Monde#6197`.
    To change your votes, simply `##nominate` different users. If you want to delete your votes, just `##unvote` to clear everything.
    When you've successfully voted, PenguinBot will react to your message with <:greentick:502460759197089802>.
    To opt-out of the nomination process entirely, just `##opt out`. If you change your mind, simply `##opt in`.

    **Asking Questions**

    Questions can be submitted for the current interviewee with `##ask <your question here>`. For example, `##ask euklyd, why is your bot so hard to use?`. If you'd rather harass your friends with a deluge of many questions at once, use `##mask`, like so:
    ```
    ##mask
    euklyd, why is your bot so hard to use?
    also, why is its avatar a piplup?
    what is it with you and penguins, anyways?
    ```
    (Each question should be on a different line.)

    **Answering Questions**

    Interviewees will have access to both a hidden channel and a Google sheet with each question.
    After filling in the **Answer** column of the sheet for a question, you can use the command `##answer`, and PenguinBot will post several answers at a time in the interview answers channel.
    """
    async def activate(self):
        try:
            with open(PATH.format(INTERVIEW_META),  'r') as meta:
                iv_meta = json.load(meta)
                self.logger.info("loaded interview meta")
                self.interview = InterviewMeta.load_from_dict(
                    iv_meta, self.core)
        except FileNotFoundError:
            self.logger.warning("couldn't find interview meta, loading new")
            self.interview = None

    @command("^iv setup <@!?\d+>$", access=700, name='iv setup',
             doc_brief="`iv setup <@user>`: Sets up an interview for "
             "<user>, with the secret questions in the current channel.")
    async def setup_question_channel(self, msg, arguments):
        if self.interview is None:
            await self.send_message(msg.channel,
                'Setting up interviews for the first time.')
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
            '**New interview setup:**\n'
            'Interviewee: {user}\n'
            'Question Channel: {qchn}\n'
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
            '**New interview setup:**\n'
            'Interviewee: {user}\n'
            'Question Channel: {qchn}\n'
            'Answer Channel: {achn}'
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
        if self.interview.active is False:
            await self.send_message(
                msg.channel,
                'Interview questions are currently **closed**; please wait '
                'for the next round to begin.')
            return
        question = {
            'question':      msg.content[4:],  # i hope this works
            'author_id':     msg.author.id,
            'author_name':   msg.author.name,
            'author_avatar': msg.author.avatar_url,
            'timestamp':     msg.timestamp
        }

        sheet = get_sheet()

        self.interview.increment_question(msg.author)

        sheet.append_row(
            [
                datetime.utcnow().strftime('%m/%d/%Y %H:%m:%S'),
                datetime.utcnow().timestamp(),
                str(msg.author),
                msg.author.id,
                self.interview.user_questions[msg.author.id],
                msg.content[4:],
                '',
                False
            ]
        )
        self.interview.dump()

        em = interview_embed(question, self.interview, msg)
        await self.send_message(self.interview.question_channel, embed=em)
        await self.add_reaction(msg, '✅')

    @command("^(mask|multi-ask)\n(.+)", access=-1, name='interview multi-ask',
             doc_brief="`multi-ask <list of questions on separate lines>:` "
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
        if self.interview.active is False:
            await self.send_message(
                msg.channel,
                'Interview questions are currently **closed**; please wait '
                'for the next round to begin.')
            return
        if arguments[0] == 'mask':
            content = msg.content[5:]
        else:
            content = msg.content[10:]  # strip command name
        questions = content.split('\n')

        sheet = get_sheet()

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
                    question_text,
                    '',
                    False
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

    @command("^ans(?:wer)?(:? <@!?(\d)>)?", access=-1, name='interview answer',
             doc_brief="`answer`: Answers as many questions as possible from "
             "a single user.")
    async def answer(self, msg, arguments):
        # if the columns on the sheet change, this will need to be adjusted
        POSTED_COL = 'H'

        if msg.author.id != self.interview.interviewee.id:
            await self.send_message(msg.channel,
                'You must be the interviewee to use this command.')
            return
        if self.interview.answer_channel is None:
            await self.send_message(msg.channel,
                'The answer channel is not yet set up.')
            return

        sheet       = get_sheet()
        records     = sheet.get_all_records()
        answers     = []
        asker_id    = None
        char_count  = 0
        answered_qs = 0
        for i, record in enumerate(records):
            if record['Posted?'] != 'FALSE':
                answered_qs += 1
            elif record['Answer'] != '':
                record['Question'] = str(record['Question'])
                record['Answer'] = str(record['Answer'])
                if asker_id == None:
                    asker_id = record['ID']
                elif record['ID'] != asker_id:
                    # only collect questions from a single user
                    continue
                if len(record['Answer']) > 5500:
                    # The questions start on line 2, and the list is 0-indexed
                    sheet.update_acell(f'{POSTED_COL}{i+2}', 'TOO LONG')
                    await self.send_message(
                        msg.channel,
                        f'The answer in row {i+2} is too long to post; figure '
                        'out posting that one yourself (then mark it Posted).')
                    continue
                char_count += len(record['Question']) + len(record['Answer'])
                if char_count > 5500:
                    break
                answers.append((i, record))
        if len(answers) == 0:
            await self.send_message(msg.channel,
                'There are no new questions at this time.')
            return
        em = blank_answers_embed(self.interview, msg, asker_id)
        for num, record in answers:
            if num != answers[-1][0]:
                add_answer(em, record['#'], record['Question'], record['Answer'])
            else:
                add_answer(em, record['#'], record['Question'], record['Answer'], space=False)
        answered_qs += len(answers)
        em.set_footer(
            text='{} questions answered'.format(answered_qs),
            icon_url=self.interview.interviewee.avatar_url
        )

        await self.send_message(self.interview.answer_channel, embed=em)
        for num, record in answers:
            # The questions start on line 2, and the list is 0-indexed
            sheet.update_acell(f'{POSTED_COL}{num+2}', 'TRUE')

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
             doc_brief="`opt <in/out>`: Opt-in or-out of interviews "
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
                for voter, votes in self.interview.votes.items():
                    self.interview.votes[voter] = [
                        vote for vote in votes if vote != msg.author.id
                    ]
                reply = "**{}**, you're now opted-out of interviews."
        else:
            reply = '**{}**, something went wrong here with your opting.'
        self.interview.dump()
        await self.send_message(msg.channel, reply.format(msg.author))

    @command("^opt[ -]list$", access=-1, name='opt list',
             doc_brief="`opt list`: List users opted out of interviews.")
    async def opt_list(self, msg, arguments):
        users = [
            msg.server.get_member(user) for user in self.interview.opt_outs
        ]
        users = sorted(users, key=lambda x: str(x).lower())
        reply = '__**Opted-Out Users**__```'
        for user in users:
            reply += str(user) + '\n'
        reply += (
            '```*As they have opted-out, you cannot nominate any of these '
            'users for interviews.*'
        )
        await self.send_message(msg.channel, reply)

    @command("^iv (enable|disable)$", access=700, name='toggle',
             doc_brief="`iv <enable/disable>`: Enables or disables interview "
             "voting and nominating.")
    async def toggle(self, msg, arguments):
        if arguments[0] == 'enable':
            if self.interview.active is not True:
                self.interview.active = True
                await self.send_message(msg.channel, "Interviews **enabled**.")
            else:
                await self.send_message(msg.channel,
                                        "Interviews already **enabled**.")
                return
        else:
            if self.interview.active is not False:
                self.interview.active = False
                await self.send_message(msg.channel, "Interviews **disabled**.")
            else:
                await self.send_message(msg.channel,
                                        "Interviews already **disabled**.")
                return
        self.interview.dump()

    @command("^(nom|nominate)(:? <@!?\d+>){1,3}$", access=-1, name='nominate',
             doc_brief="`nominate <@user1> [<@user2>] [@user3]`: Nominate up "
             "to three users for interviews. If you've already made "
             "nominations, they will all be replaced.")
    async def nominate(self, msg, arguments):
        if self.interview.active is False:
            await self.send_message(
                msg.channel,
                'Nominations are currently **closed**; please wait for '
                'the next round to begin.')
            return
        votes     = []
        self_vote = False
        opt_outs  = []
        bots      = []
        reply = ''
        for mention in msg.mentions:
            if mention.id == msg.author.id:
                self_vote = True
            elif mention.id in self.interview.opt_outs:
                opt_outs.append(str(mention))
            elif mention.id == '224283755538284544':
                bots.append(str(mention))
                votes.append(mention.id)
                await self.add_reaction(msg, '🔥')
                await self.send_message(msg.channel, 'harufe!')
            elif mention.bot is True:
                bots.append(str(mention))
            else:
                votes.append(mention.id)
        votes = list(set(votes))  # clear duplicates
        opt_outs = list(set(opt_outs))
        self.interview.votes[msg.author.id] = votes
        self.interview.dump()
        if len(self.interview.votes[msg.author.id]) > 0:
            await self.add_reaction(msg, self.core.emoji.any_emoji(['greentick']))
        if self_vote:
            redtick = self.core.emoji.any_emoji(['redtick'])
            await self.add_reaction(msg, redtick)
            reply += (
                '{} **{}**, your anti-town self-vote was ignored.\n'
            ).format(redtick, msg.author, ', '.join(opt_outs))
        if len(opt_outs) > 0:
            redtick = self.core.emoji.any_emoji(['redtick'])
            reply += (
                '{} **{}**, your vote(s) for `[{}]` were ignored because they '
                'opted-out.\n'
            ).format(redtick, msg.author, ', '.join(opt_outs))
            await self.add_reaction(msg, redtick)
        if len(bots) > 0:
            bot_tag = self.core.emoji.any_emoji(['bottag'])
            reply += (
                '{} **{}**, while we appreciate your support of the **Rᴏʙᴏᴛ '
                'Rᴇᴠᴏʟᴜᴛɪᴏɴ**, bots such as `[{}]` cannot win interview '
                'nominations; you would be best served voting for a more '
                'humanlike compromise, like Makaze or Arcanite.\n'
            ).format(bot_tag, msg.author, ', '.join(bots))
            await self.add_reaction(msg, bot_tag)
        await self.send_message(msg.channel, reply)

    @command("^(unvote|unnom|im conq and i hate voting)$", access=-1,
             name='unvote',
             doc_brief="`unnom`: Deletes all your current votes.")
    async def unvote(self, msg, arguments):
        if self.interview.active is False:
            await self.send_message(
                msg.channel,
                'Nominations are currently **closed**; please wait for '
                'the next round to begin.')
            return
        if msg.author.id not in self.interview.votes or len(self.interview.votes[msg.author.id]) == 0:
            reply = "**{}**, you're not currently nominating anyone."
        else:
            self.interview.votes[msg.author.id] = []
            reply = '**{}**, your nomination(s) have been cleared.'
        await self.send_message(msg.channel, reply.format(msg.author))

    @command("^votals ?(--full)?$", access=-1, name='votals (full)',
             doc_brief="`votals [--full]`: Displays current vote totals for "
             "interview nominations.",
             doc_detail="`votals [--full]`: Displays current vote totals for "
             "interview nominations. If the `--full` flag is provided, so "
             "long as the user's access is ≥ 300, detailed votal information "
             "will be calculated.")
    async def votals(self, msg, arguments):
        votals = {}
        for voter, votes in self.interview.votes.items():
            for vote in votes:
                if vote in votals:
                    votals[vote].append(voter)
                else:
                    votals[vote] = [voter]
        # sorted_votals is a list of lists of the format:
        # [ID, [voter IDs], member]
        sorted_votals = [list(nom) + [msg.server.get_member(nom[0])] for nom in votals.items()]
        # Sort by the number of votes, then alphabetically
        sorted_votals = sorted(sorted_votals, key=lambda x: (-len(x[1]), str(x[2]).lower()))
        max_len = 0
        for nom in sorted_votals:
            max_len = max(len(str(msg.server.get_member(nom[0]))), max_len)

        reply = '**__Votals__**```\n'
        access = self.core.ACL.get_final_user_access(msg.author, self.name)
        if arguments[0] == '--full' and access >= 300:
            votal_fmt = '{{:<{}}} {{}} ({{}})\n'.format(max_len+1)
            for nom in sorted_votals:
                if nom[0] not in self.interview.opt_outs:
                    reply += votal_fmt.format(
                        str(msg.server.get_member(nom[0])) + ':',
                        len(nom[1]),
                        # alphabetize
                        ', '.join(sorted([str(msg.server.get_member(voter)) for voter in nom[1]], key=lambda x: x.lower()))
                    )
        else:
            votal_fmt = '{{:<{}}} {{}}\n'.format(max_len+1)
            for nom in sorted_votals:
                if nom[0] not in self.interview.opt_outs:
                    reply += votal_fmt.format(
                        str(msg.server.get_member(nom[0])) + ':',
                        len(nom[1])
                    )
        reply += '```'

        if msg.author.id in self.interview.votes:
            if len(self.interview.votes[msg.author.id]) == 0:
                reply += '*You are not currently voting; vote with `nominate <@user1> <@user2> <@user3>`.*'
            else:
                reply += '*You are currently voting for: '
                votelist = ', '.join(sorted(
                    [str(msg.server.get_member(voter)) for voter in self.interview.votes[msg.author.id]],
                    key=lambda x: x.lower()
                ))
                reply += '{}, '.format(votelist)
                reply = reply[:-2] + '*'

        await self.send_message(msg.channel, reply)
