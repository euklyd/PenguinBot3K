"""
    Plugin Name : Manage
    Plugin Version : 2.0

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
import sys
import time
import inspect
from tabulate import tabulate
from collections import namedtuple

ACCESS = {
    "ping"          : 50,
    "trigger"       : -1,
    "plugin_list"   : 50,
    "plugin_manage" : 1000,
    "uptime"        : 50
}

class Manage(Plugin):
    async def activate(self):
        await self.core.wait_until_login()
        self.login_time = time.time()

    @command("^ping", access=ACCESS["ping"])
    async def ping(self, msg, arguments):
        """`ping`: prints a simple response."""
        await self.send_message(msg.channel, "Pong")

    @command("^trigger$", access=ACCESS['trigger'])
    async def trigger(self, msg, arguments):
        """`trigger`: prints the default prefix used to tell me that you're using a command."""
        if (type(self.core.config.trigger) is tuple or type(self.core.config.trigger) is list):
            await self.send_message(msg.channel, "My default trigger is `{}`".format(self.core.config.trigger[0]))
        else:
            await self.send_message(msg.channel, "My default trigger is `{}`".format(self.core.config.trigger))

    @command("^triggers$", access=ACCESS['trigger'])
    async def triggers(self, msg, arguments):
        """`triggers`: prints the prefixes used to tell me that you're using a command, if there exist multiple."""
        if (type(self.core.config.trigger) is tuple or type(self.core.config.trigger) is list):
            await self.send_message(msg.channel, "My default triggers are `{}`".format(self.core.config.trigger))
        else:
            await self.send_message(msg.channel, "My default trigger is `{}`".format(self.core.config.trigger))

    @command("^list plugins$", access=ACCESS["plugin_list"])
    async def list_plugins(self, msg, arguments):
        """`list plugins`: lists all of my plugins."""
        plugins = self.core.plugin.list()

        table = []
        for name, meta in sorted(plugins.items()):
            table.append([name, meta['status']])

        output = "**My plugins: **\n\n"
        output += "`{}`".format(tabulate(table, headers=["Name", "Status"], tablefmt="psql", numalign="left"))

        await self.send_message(msg.channel, output)

    @command("^list commands (\w+)")
    async def list_commands(self, msg, arguments):
        """`list commands <plugin>`: lists all commands that you have access to in `<plugin>`."""
        plugin = arguments[0]
        plugin_list = self.core.plugin.list()
        access = self.core.ACL.getAccess(msg.author.id)
        if (plugin in plugin_list):

            # debug stuff
            # module = plugin_list[plugin]['instance']
            # for name, callback in inspect.getmembers(module, inspect.ismethod):
            #     self.logger.debug("{} -> {} : {}".format(module, name, inspect.getdoc(callback)))

            command_list = self.core.command.commands
            command_block = "**List of commands in plugin `{}`:**\n".format(plugin)
            for command in sorted(command_list.keys()):
                if (plugin == command.split('.')[0] and command_list[command].access <= access):
                    docstr = command_list[command].callback.__doc__
                    if (docstr is not None and command_list[command].access <= access):
                        command_block += docstr + '\n'
            # self.send_message(msg.channel, command_block)
            await self.send_message(msg.channel, command_block)
        else:
            # self.send_message(msg.channel, "<@!{}>, there's no plugin named **{}**!".format(msg.author.id, plugin))
            await self.send_message(msg.channel, "<@!{}>, there's no plugin named **{}**!".format(msg.author.id, plugin))

    @command("^list commands$", access=-1)
    async def list_all_commands(self, msg, arguments):
        """`list commands`: lists all commands that you have access to."""
        plugin_list = self.core.plugin.list()
        access = self.core.ACL.getAccess(msg.author.id)
        for plugin in plugin_list:
            command_list = self.core.command.commands
            command_block = "**List of commands in plugin `{}`:**\n".format(plugin)
            for command in sorted(command_list.keys()):
                if (plugin == command.split('.')[0] and command_list[command].access <= access):
                    docstr = command_list[command].callback.__doc__
                    if (docstr is not None and command_list[command].access <= access):
                        command_block += docstr + '\n'
            if (command_block.count('\n') > 1):
                await self.send_message(msg.channel, command_block)

    @command("^help$", access=-1)
    async def help(self, msg, arguments):
        """`help`: alias for `list commands`."""
        await self.list_all_commands(msg, arguments)

    @command("^(enable|disable|reload|status) plugin ([A-Za-z]+)$", access=ACCESS["plugin_manage"])
    async def manage_plugin(self, msg, arguments):
        """`enable plugin <plugin>`: enables `<plugin>`.
`disable plugin <plugin>`: disables `<plugin>`.
`reload plugin <plugin>`: reloads `<plugin>`.
`status plugin <plugin>`: fetches the status of `<plugin>`."""
        plugins = self.core.plugin.list()
        plugin = arguments[1]
        action = arguments[0]

        if plugin in plugins:
            if action == "enable":
                if plugins[plugin]['status'] == "Disabled":
                    self.core.plugin.load(plugin)
                    await self.send_message(msg.channel, "Enabled plugin: **{}**".format(plugin))
                else:
                    await self.send_message(msg.channel, "{} is already enabled".format(plugin))

            elif action == "disable":
                if plugins[plugin]['status'] == "Enabled":
                    self.core.plugin.unload(plugin)
                    await self.send_message(msg.channel, "Disabled plugin: **{}**".format(plugin))
                else:
                    await self.send_message(msg.channel, "{} is already disabled".format(plugin))

            elif action == "reload":
                if plugins[plugin]['status'] == "Disabled":
                    self.core.plugin.reload(plugin)
                    await self.send_message(msg.channel, "Reloaded plugin: **{}**".format(plugin))
        else:
            await self.send_message(msg.channel, "I don't have a plugin by that name.")

    # @subscribe("connect")
    # def on_connect(self, *args, **kwargs):
    #     self.login_time = time.time()

    @command("^uptime$", access=ACCESS['uptime'])
    async def uptime(self, msg, arguments):
        """`uptime`: prints the duration that I've been running for."""
        uptime = time.time() - self.login_time

        def readable_time(elapsed):
            readable = ""

            days = int(elapsed / (60 * 60 * 24))
            hours = int((uptime / (60 * 60)) % 24)
            minutes = int((uptime % (60 * 60)) / 60)
            seconds = int(uptime % 60)

            if(days > 0):       readable += str(days) + " days "
            if(hours > 0):      readable += str(hours) + " hours "
            if(minutes > 0):    readable += str(minutes) + " minutes "
            if(seconds > 0):    readable += str(seconds) + " seconds "

            return readable

        await self.send_message(msg.channel, "I've been connected for: **" + readable_time(uptime) + "**")
