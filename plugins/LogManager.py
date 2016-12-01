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

import os
import random
import re
import string
import zipfile

ACCESS = {
    'retrieve': 500
}


class LogManager(Plugin):
    async def activate(self):
        await self.core.wait_until_login()
        self.log_manager = self.core.log_manager
        pass

    @command("^gimme logs <#([0-9]+)>(?: ([0-9]+))?$",
             access=ACCESS['retrieve'],
             doc_brief="`gimme logs #<channel>`: Retrieve log files for "
             "<channel>.",
             doc_detail=("`gimme logs #<channel>`: Uploads the current log "
                         "file for the specified channel privately to the "
                         "requestor.\n\t"
                         "**Optional:** Specify a number after `gimme logs` "
                         "to request that many days in the past in addition "
                         "to today's file."))
    async def remote_log_request(self, msg, arguments):
        channel = self.core.get_channel(arguments[0])
        if (len(arguments) == 2 and arguments[1] is not None):
            if (int(arguments[1]) < 0):
                await self.send_message(
                    msg.author,
                    ("Invalid argument for `gimme logs`: needs to be"
                     "greater than or equal to 0.")
                )
                return
            else:
                days = int(arguments[1])
        else:
            days = 0
        await self.send_logs(channel, msg.author, days=days, request_id=msg.id)

    @command("^gimme logs(?: ([0-9]+))?$", access=ACCESS['retrieve'],
             doc_brief="`gimme logs`: Retrieve log files for the curent "
             "channel.",
             doc_detail=("`gimme logs`: Uploads the current log file for the "
                         "current channel privately to the requestor.\n\t"
                         "**Optional:** Specify a number after `gimme logs` "
                         "to request that many days in the past in addition "
                         "to today's file."))
    async def log_request(self, msg, arguments):
        if (len(arguments) == 1 and arguments[0] is not None):
            if (int(arguments[0]) < 0):
                await self.send_message(
                    msg.author,
                    ("Invalid argument for `gimme logs`: needs to be"
                     "greater than or equal to 0.")
                )
                return
            else:
                days = int(arguments[0])
        else:
            days = 0
        await self.send_logs(
            msg.channel, msg.author, days=days, request_id=msg.id
        )
        await self.delete_message(msg)

    async def send_logs(self, channel, requestor, days=0, request_id="0000"):
        filenames = self.log_manager.get_logs(channel, days)
        if (len(filenames) > 1):
            await self.send_zip(
                channel, requestor, filenames, request_id=request_id
            )
        elif (len(filenames) == 1):
            with open(filenames[0], 'rb') as fp:
                await self.send_file(
                    requestor,
                    fp,
                    filename=filenames[0].split('/')[-1]
                )
        else:
            await self.send_message(
                requestor,
                "ERROR: There are no logs to retrieve."
            )

    async def send_zip(self, channel, destination, filenames, request_id="0000"):
        """
        Helper function for send_logs()
        """
        zip_name = "{ch_name}-{msg_id}.zip".format(
            ch_name=channel.name,
            msg_id=request_id
        )
        zip_path = "resources/{}".format(zip_name)
        with zipfile.PyZipFile(zip_path, mode='a') as log_zip:
            for logfile in filenames:
                log_zip.write(logfile)
        with open(zip_path, 'rb') as log_zip:
            await self.send_file(destination, log_zip, filename=zip_name)
        os.remove(zip_path)
