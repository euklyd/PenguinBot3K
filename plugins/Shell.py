"""
    Class Name : Shell

    Description:
        Interactive python shell

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
import logging
import re

result = None
# myvar = "this is my var"
# shell_ref = None
# meirl = None


class Shell(Plugin):
    async def activate(self):
        self.openshell = False
        global shell_ref
        global meirl
        shell_ref = self
        meirl = self

    def check_cmd(self, msg):
        code_regex = re.compile("```(.*)```")
        match = code_regex.match(msg.content)
        if (match is None):
            self.logger.info("nah")
            return None
        else:
            if ("import os" in match.groups()[0]):
                self.logger.info("fuq u")
                return "'fuck off'"
        self.logger.info("fall thru: {}".format(match.groups()[0]))
        return match.groups()[0]

    def foo(self):
        print("foo")

    async def bar(self):
        print("async bar")

    @command("^(?:shell\.py|python3)", access=1000, name='shell.py',
             doc_brief="`shell.py`: opens an interactive shell")
    async def shell_py(self, msg, arguments):
        self.openshell = True
        cmd = None
        await self.send_message(
            msg.channel,
            "```Python 3.5.2 (v3.5.2:4def2a2901a5, Jun 26 2016, 10:47:25)```"
        )
        while (cmd is None):
            cmd = await self.core.wait_for_message(
                author=msg.author,
                channel=msg.channel
            )
            cmd = self.check_cmd(cmd)
        while (not cmd.startswith("exit")):
            # global result
            self.result = None
            # cmd = "result = " + cmd
            # exec(cmd) in globals()
            # meirl = self
            # myvar = "this is my var"
            rescmd = (
                "import discord\n"
                # "global result\n"
                "self.result = {cmd}\n"
                # "reply = '```{{}}```'.format(result)\n"
                # "print(myvar)\n"
                # "myvar = 'goodbye'\n"
                # "print(myvar)\n"
                # "print(meirl)\n"
                # "print('openshell = {{}}'.format(meirl.openshell))\n"
                # "meirl.foo()\n"
                # "print(meirl.__dir__())\n"
                # "print(meirl.send_message)\n"
                # "func = meirl.__getattribute__('send_message')\n"
                # "print(func)\n"
                # "await self.bar()\n"
                # "await func(msg.channel, reply)\n"
                # "await meirl.send_message(msg.channel, reply)\n"
            ).format(cmd=cmd)
            # self.logger.info(globals())
            # exec(cmd) in globals()
            # self.logger.info(locals())
            # exec(cmd) in locals()
            try:
                exec(rescmd)
            except Exception as e:
                try:
                    exec(cmd)
                except Exception as e:
                    self.result = e
            # print(myvar)
            self.logger.info(self.result)
            if (self.result is not None):
                reply = "```py\n{}\n```".format(self.result)
                try:
                    await self.send_message(msg.channel, reply)
                except Exception as e:
                    reply = "```py\n{}\n```".format(e)
                    await self.send_message(msg.channel, reply)
            cmd = None
            while (cmd is None):
                cmd = await self.core.wait_for_message(
                    author=msg.author,
                    channel=msg.channel
                )
                cmd = self.check_cmd(cmd)
        self.openshell = False
        await self.send_message(msg.channel, "```Shell exited cleanly```")
