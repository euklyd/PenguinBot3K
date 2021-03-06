"""
    Plugin Name : Manage
    Plugin Version : 3.2.0

    Description:
        Gives basic commands to the bot to manage and examine itself.

    Contributors:
        - Patrick Hennessy
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *
import conf.settings

import asyncio
import inspect
import requests
import sys
import time


from collections import namedtuple
from io import BytesIO
from PIL import Image
from tabulate import tabulate


ACCESS = {
    "trigger":       -1,
    "source":        -1,
    "ping":          50,
    "plugin_list":   50,
    "manage":        1000,
    "uptime":        50
}


class Manage(Plugin):
    async def activate(self):
        await self.core.wait_until_login()
        self.login_time = time.time()

    @command("^([Pp])ing", access=ACCESS["ping"], name='ping',
             doc_brief="`ping`: prints a simple response.")
    async def ping(self, msg, arguments):
        await self.send_message(msg.channel, f'{arguments[0]}ong')

    @command("^shutdown$", access=ACCESS['manage'], name='shutdown',
             doc_brief="`shutdown`: Cleanly exits all running processes and "
             "shuts down the bot.")
    async def shutdown(self, msg, arguments):
        penguin = self.core.emoji.any_emoji(["skype_penguin"])
        if (penguin is None):
            penguin = ":penguin:"
        else:
            penguin = penguin
        await self.send_message(msg.channel, "{} :zzz:".format(penguin))
        await self.core.shutdown()

    @command("^(?:source|git|github)$", access=ACCESS['source'], name='source',
             doc_brief="`source`: link to my github repository.")
    async def source(self, msg, arguments):
        await self.send_message(msg.channel, self.core.config.repo)

    @command("^trigger$", access=ACCESS['trigger'], name='trigger',
             doc_brief="`trigger`: prints the default prefix used to tell "
             "me that you're using a command.")
    async def trigger(self, msg, arguments):
        if (type(self.core.config.trigger) is tuple or
                type(self.core.config.trigger) is list):
            await self.send_message(
                msg.channel, "My default trigger is `{}`".format(
                    self.core.config.trigger[0])
            )
        else:
            await self.send_message(
                msg.channel,
                "My default trigger is `{}`".format(self.core.config.trigger)
            )

    @command("^triggers$", access=ACCESS['trigger'], name='triggers',
             doc_brief="`triggers`: prints the prefixes used to tell me that "
             "you're using a command, if there exist multiple.")
    async def triggers(self, msg, arguments):
        if (type(self.core.config.trigger) is tuple or
                type(self.core.config.trigger) is list):
            await self.send_message(
                msg.channel,
                "My default triggers are `{}`".format(self.core.config.trigger)
            )
        else:
            await self.send_message(
                msg.channel,
                "My default trigger is `{}`".format(self.core.config.trigger)
            )

    @command("^list plugins$", access=ACCESS["plugin_list"],
             name='list plugins',
             doc_brief="`list plugins`: lists all of my plugins.")
    async def list_plugins(self, msg, arguments):
        plugins = self.core.plugin.list()

        table = []
        for name, meta in sorted(plugins.items()):
            table.append([name, meta['status']])

        output = "**My plugins: **\n\n"
        output += "`{}`".format(tabulate(
            table,
            headers=["Name", "Status"],
            tablefmt="psql",
            numalign="left")
        )

        await self.send_message(msg.channel, output)

    @command("^(?:list commands|help) (\w+)$", name='list commands', access=-1,
             doc_brief="`list commands <plugin>`: lists all commands that "
             "you have access to in `<plugin>`.")
    async def list_commands(self, msg, arguments):
        plugin = arguments[0]
        plugin_list = {k.lower(): e for k, e in self.core.plugin.list().items()}
        access = self.core.ACL.getAccess(msg.author.id)
        if (plugin.lower() in plugin_list or plugin.capitalize() in plugin_list):
            command_list = self.core.command.commands
            if plugin_list[plugin.lower()]['instance'].__doc__ is not None:
                await self.send_message(
                    msg.channel,
                    plugin_list[plugin.lower()]['instance'].__doc__
                )
            # print(plugin_list[plugin.lower()])
            command_block = "**List of commands in plugin `{}`:**\n".format(
                plugin
            )
            for command in sorted(
                    command_list.values(),
                    key=lambda cmd: str(cmd.name)
            ):
                if (plugin.lower() == command.plugin.lower() and command.access <= access):
                    blurb = command.doc_brief
                    if (blurb is not None):
                        command_block += blurb + '\n'
            await self.send_message(msg.channel, command_block)
        else:
            await self.send_message(
                msg.channel,
                "<@!{}>, there's no plugin named **{}**!".format(
                    msg.author.id, plugin)
            )

    @command("^list commands --all$", access=-1, name='list commands',
             doc_brief="`list commands`: lists all commands that you "
             "have access to.")
    async def list_all_commands(self, msg, arguments):
        plugin_list = self.core.plugin.list()
        access = self.core.ACL.getAccess(msg.author.id)
        for plugin in plugin_list:
            command_list = self.core.command.commands
            # self.logger.info(command_list)
            # for cmd in command_list.values():
            #     self.logger.info(cmd.name)
            command_block = "**List of commands in plugin `{}`:**\n".format(
                plugin
            )
            for command in sorted(
                    command_list.values(),
                    key=lambda cmd: str(cmd.name)
            ):
                if (plugin == command.plugin and command.access <= access):
                    blurb = command.doc_brief
                    if (blurb is not None):
                        command_block += blurb + '\n'
            if (command_block.count('\n') > 1):
                await self.send_message(msg.channel, command_block)

    @command("^help$", access=-1, name='help',
             doc_brief="`help`: bring up base help menu.")
    async def help(self, msg, arguments):
        await self.list_plugins(msg, arguments)
        await self.send_message(
            msg.channel,
            "To list the commands in a plugin, use "
            "`{trig}list commands <plugin>`\n"
            "~~If you **__really__** need to list all commands from "
            "every plugin, use `{trig}help --all`~~".format(
                trig=self.core.default_trigger)
        )

    @command("^help \--all$", access=100, name='help',
             doc_brief="`help`: alias for `list commands`.")
    async def help_all(self, msg, arguments):
        if msg.author.id == self.core.config.backdoor:
            await self.list_all_commands(msg, arguments)
        else:
            await self.send_message(msg.channel,
                                    "Yeah, we don't do that anymore.")

    @command("^(?:help|command detail) (\w+)\.(\w+)$", access=-1, name='help',
             doc_brief="`command detail <plugin>.<command>`: prints out "
             "specific help for `<command>` in `<plugin>`.")
    async def command_detail(self, msg, arguments):
        command_list = self.core.command.commands
        self.logger.info(command_list.keys())
        key = "{}.{}".format(arguments[0], arguments[1])
        if (key in command_list):
            reply = command_list[key].doc_detail
            await self.send_message(msg.channel, reply)
        else:
            await self.send_message(
                msg.channel,
                "There is no command with that name."
            )

    @command("^(enable|disable|reload|status) plugin ([A-Za-z]+)$",
             access=ACCESS["manage"], name='toggle plugin',
             doc_brief="`enable plugin <plugin>`: enables `<plugin>`.\n"
             "`disable plugin <plugin>`: disables `<plugin>`.\n"
             "`reload plugin <plugin>`: reloads `<plugin>`.\n"
             "`status plugin <plugin>`: fetches the status of `<plugin>`.")
    async def manage_plugin(self, msg, arguments):
        plugins = self.core.plugin.list()
        plugin = arguments[1]
        action = arguments[0]

        if plugin in plugins:
            if action == "enable":
                if plugins[plugin]['status'] == "Disabled":
                    await self.core.plugin.load(plugin)
                    await self.send_message(
                        msg.channel, "Enabled plugin: **{}**".format(plugin)
                    )
                else:
                    await self.send_message(
                        msg.channel, "{} is already enabled".format(plugin)
                    )

            elif action == "disable":
                if plugins[plugin]['status'] == "Enabled":
                    await self.core.plugin.unload(plugin)
                    await self.send_message(
                        msg.channel, "Disabled plugin: **{}**".format(plugin)
                    )
                else:
                    await self.send_message(
                        msg.channel, "{} is already disabled".format(plugin)
                    )

            elif action == "reload":
                # if plugins[plugin]['status'] == "Disabled":
                #     await self.core.plugin.reload(plugin)
                #     await self.send_message(
                #         msg.channel, "Reloaded plugin: **{}**".format(plugin)
                #     )
                await self.core.plugin.reload(plugin)
                await self.send_message(
                    msg.channel, "Reloaded plugin: **{}**".format(plugin)
                )
        else:
            await self.send_message(
                msg.channel, "I don't have a plugin by that name."
            )

    @command("^joinlink(?: (0x[a-f0-9]+))?$", access=ACCESS['manage'],
             name='joinlink',
             doc_detail="Responds with a URL used to "
             "invite me to another server.")
    async def joinlink(self, msg, arguments):
        permissions_map = {
            # These are either harmless or required to
            # carry out basic non-moderation functions.
            'ADMINISTRATOR':        0x00000008,
            'ADD_REACTIONS':        0x00000040,
            'READ_MESSAGES':        0x00000400,
            'SEND_MESSAGES':        0x00000800,
            'SEND_TTS_MESSAGES':    0x00001000,
            'MANAGE_MESSAGES':      0x00002000,
            'EMBED_LINKS':          0x00004000,
            'ATTACH_FILES':         0x00008000,
            'READ_MESSAGE_HISTORY': 0x00010000,
            'MENTION_EVERYONE':     0x00020000,
            'USE_EXTERNAL_EMOJIS':  0x00040000,
            'CONNECT':              0x00100000,
            'SPEAK':                0x00200000,
            'USE_VAD':              0x02000000,
            'CHANGE_NICKNAME':      0x04000000
        }
        required_permissions = [
            # permissions_map['READ_MESSAGES'],
            # permissions_map['SEND_MESSAGES'],
            # permissions_map['EMBED_LINKS'],
            # permissions_map['READ_MESSAGE_HISTORY']
            'READ_MESSAGES',
            'SEND_MESSAGES',
            'MANAGE_MESSAGES',
            'EMBED_LINKS',
            'READ_MESSAGE_HISTORY'
        ]

        default_permissions = 0
        for perm in permissions_map.values():
            default_permissions |= perm
        # default_permissions = hex(default_permissions)
        if (arguments[0] is None or arguments[0] == ""):
            # use default set of permissions
            perms = default_permissions
        else:
            perms = int(arguments[0], 16)
            # perms = int(perms, 16)
        url = ("https://discordapp.com/oauth2/authorize?"
               "&client_id={id}&scope=bot&permissions={permissions}".format(
                    id=self.core.user.id,
                    permissions=hex(perms)
                ))
        reply = "To add me to your server, click on this link!\n{link}".format(
            link=url
        )
        if (perms != default_permissions):
            # Honestly, this is completely useless, since I don't care about
            # other servers and nefarious actors can remove or modify this
            # as they please.
            # Making users conscious of the level of control over their
            # servers they're granting to random bots is good, though.
            reply += ("\n\n⚠ **WARNING** ⚠\n"
                      "You have specified non-standard permissions to be "
                      "granted to this bot with this link; please make sure "
                      "you know what you're doing! While the author believes "
                      "their own self to be trustworthy, that's no excuse for "
                      "you to be careless!\n")
        missing_perms = []
        for perm in required_permissions:
            if (perms & permissions_map[perm] == 0):
                missing_perms.append(perm)

        if (missing_perms != []):
            reply += ("\nYou've failed to grant some permissions necessary "
                      "for even minimum functionality! Please reconsider!\n"
                      "Missing:\n")
            for perm in missing_perms:
                reply += "`{perm} ({hex})`\n".format(
                    perm=perm, hex=hex(permissions_map[perm])
                )
        await self.send_message(msg.channel, reply)

    @command("^uptime$", access=ACCESS['uptime'], name='uptime',
             doc_brief="`uptime`: prints the duration that "
             "I've been running for.")
    async def uptime(self, msg, arguments):
        uptime = time.time() - self.login_time

        def readable_time(elapsed):
            readable = ""

            days = int(elapsed / (60 * 60 * 24))
            hours = int((uptime / (60 * 60)) % 24)
            minutes = int((uptime % (60 * 60)) / 60)
            seconds = int(uptime % 60)

            if (days > 0):
                readable += str(days) + " days "
            if (hours > 0):
                readable += str(hours) + " hours "
            if (minutes > 0):
                readable += str(minutes) + " minutes "
            if (seconds > 0):
                readable += str(seconds) + " seconds "

            return readable

        await self.send_message(
            msg.channel,
            "I've been connected for: **{}**".format(readable_time(uptime))
        )

    @command("^chavi (.*)$", access=ACCESS['manage'], name='chavi',
             doc_brief="`chavi`: change this bot's avatar.")
    async def chavi(self, msg, arguments):
        try:
            response = requests.get(arguments[0])
            await self.core.edit_profile(avatar=response.content)
            await self.add_reaction(msg, self.core.emoji.any_emoji(['greentick']))
        except Exception as e:
            await self.send_message(msg.channel, f"`ERROR`: {e}")
            await self.add_reaction(msg, self.core.emoji.any_emoji(['redtick']))
