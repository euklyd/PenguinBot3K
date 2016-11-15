"""
    Plugin Name : LogManager
    Plugin Version : 0.1.0

    Description:
        Allows for retrieval of logs (from the core.LogManager module)
         by moderators.

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *

import random
import re
import string
import discord

ACCESS = {
    'retrieve': 500
}


class Moderation(Plugin):
    async def activate(self):
        self.log_manager = self.core.log_manager
        pass

    @command("^gimme logs(?: ([0-9]+))", access=ACCESS['retrieve'])
    async def put_logs(self, msg, arguments):
        """`gimme logs`: Uploads the current log file for the current channel privately to the requestor.\n\t**Optional:** Specify a number after `gimme logs` to request that many days in the past in addition to today's file."""
        if (len(arguments) == 1):
            if (arguments[0] < 0):
                await self.send_message(
                    msg.author,
                    "Invalid argument for `gimme logs`: needs to be greater than or equal to 0."
                )
                return
            else:
                days = arguments[0]
        else:
            days = 0
        filenames = self.log_manager.get_logs(msg.channel, days)
        for filename in filenames:
            fp = open(filename, 'r')
            self.logger.info("Sending {file} to {user}#{discriminator}".format(
                file=filename,
                user=msg.author.name,
                discriminator=msg.author.discriminator
            ))
            await self.core.send_file(msg.author, fp, filename=filename)
            fp.close()
