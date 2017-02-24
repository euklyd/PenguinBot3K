"""
    Plugin Name : Query
    Plugin Version : 0.1

    Description:
        Allows for querying of stuff.

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
import glob
import os
import re

ACCESS = {
    'user':      100,
}

querydir = "resources/query/{}"


class Query(Plugin):
    async def activate(self):
        pass

    async def deactivate(self):
        pass

    @command('^cfhack_feb2017 (.*)$', access=ACCESS['user'],
             name='cfhack')
    async def cfhack_feb2017(self, msg, arguments):
        fname = querydir.format("sorted_unique_cf.txt")
        if (os.path.exists(fname) is False):
            self.logger.info(os.listdir(querydir.format("")))
            await self.send_message(
                msg.channel,
                "I don't have the list of affected sites, but you can find "
                "it at https://github.com/pirate/sites-using-cloudflare"
            )
            return
        await self.send_message(msg.channel, "Searching now...")
        sites = arguments[0].split(' ')
        line_num = 0
        count = 0
        replies = [""]
        n_replies = 0
        self.logger.info(sites)
        for line in open(fname):
            for site in sites:
                if (site in line):
                    replies[n_replies] += "`L{0:0>7}`: {l}".format(
                        line_num, l=line
                    )
                    if (len(replies[n_replies]) >= 1800):
                        n_replies += 1
                        replies.append("")
                    count += 1
            line_num += 1
        if (replies == []):
            await self.send_message(msg.channel,
                                    "None of your sites were found!")
        else:
            replies[0] = "**{}: Found on {} lines:**\n{}".format(
                msg.author.name, count, replies[0]
            )
            if (len(replies) > 1 or replies[0].count('\n') > 10):
                await self.send_message(
                    msg.channel,
                    "{}: Too many results; sending responde via DM".format(
                        msg.author.name
                    )
                )
                ch = msg.author
            else:
                ch = msg.channel
            for reply in replies:
                await self.send_message(ch, reply)
