"""
    Plugin Name : Manage
    Plugin Version : 1.2

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
    @command("^ping", access=ACCESS["ping"])
    def ping(self, msg):
        """`ping`: prints a simple response."""
        self.say(msg.channel, "Pong")

    #@command("^trigger$", trigger="?", access=ACCESS['trigger'])
    @command("^trigger$", access=ACCESS['trigger'])
    def trigger(self, msg):
        """`trigger`: prints the default prefix used to tell me that you're using a command."""
        if (type(self.core.config.trigger) is tuple or type(self.core.config.trigger) is list):
            self.say(msg.channel, "My default trigger is `{}`".format(self.core.config.trigger[0]))
        else:
            self.say(msg.channel, "My default trigger is `{}`".format(self.core.config.trigger))

    @command("^triggers$", access=ACCESS['trigger'])
    def triggers(self, msg):
        """`triggers`: prints the prefixes used to tell me that you're using a command, if there exist multiple."""
        if (type(self.core.config.trigger) is tuple or type(self.core.config.trigger) is list):
            self.say(msg.channel, "My default triggers are `{}`".format(self.core.config.trigger))
        else:
            self.say(msg.channel, "My default trigger is `{}`".format(self.core.config.trigger))

    @command("^list plugins$", access=ACCESS["plugin_list"])
    def list_plugins(self, msg):
        """`list plugins`: lists all of my plugins."""
        plugins = self.core.plugin.list()

        table = []
        for name, meta in sorted(plugins.items()):
            table.append([name, meta['status']])

        output = "**My plugins: **\n\n"
        output += "`{}`".format(tabulate(table, headers=["Name", "Status"], tablefmt="psql", numalign="left"))

        self.say(msg.channel, output)

    @command("^list commands (\w+)")
    def list_commands(self, msg):
        """`list commands <plugin>`: lists all commands that you have access to in `<plugin>`."""
        plugin = msg.arguments[0]
        plugin_list = self.core.plugin.list()
        access = self.core.ACL.getAccess(msg.sender)
        if (plugin in plugin_list):
            command_list = self.core.command.commands
            command_block = "**List of commands in plugin `{}`:**\n".format(plugin)
            for command in sorted(command_list.keys()):
                if (plugin == command.split('.')[0] and command_list[command].access <= access):
                    docstr = command_list[command].callback.__doc__
                    if (docstr is not None and command_list[command].access <= access):
                        command_block += docstr + '\n'
            self.say(msg.channel, command_block)
        else:
            self.say(msg.channel, "<@!{}>, there's no plugin named **{}**!".format(msg.sender, plugin))

    # @command("^list commands$", access=-1)
    # def list_all_commands(self, msg):
    #     """`list commands`: lists all commands that you have access to in all plugins."""
    #     access = self.core.ACL.getAccess(msg.sender)
    #     command_list = self.core.command.commands
    #     command_block = "**List of all commands in all plugins:**\n"
    #     for command in sorted(command_list.keys()):
    #         docstr = command_list[command].callback.__doc__
    #         if (docstr is not None and command_list[command].access <= access):
    #             command_block += docstr + '\n'
    #     self.say(msg.channel, command_block)

    @command("^list commands$", access=-1)
    def list_all_commands(self, msg):
        """`list commands <plugin>`: lists all commands that you have access to."""
        plugin_list = self.core.plugin.list()
        access = self.core.ACL.getAccess(msg.sender)
        for plugin in plugin_list:
            command_list = self.core.command.commands
            command_block = "**List of commands in plugin `{}`:**\n".format(plugin)
            for command in sorted(command_list.keys()):
                if (plugin == command.split('.')[0] and command_list[command].access <= access):
                    docstr = command_list[command].callback.__doc__
                    if (docstr is not None and command_list[command].access <= access):
                        command_block += docstr + '\n'
            if (command_block.count('\n') > 1):
                self.say(msg.channel, command_block)

    @command("^help$", access=-1)
    def help(self, msg):
        """`help`: alias for `list commands`."""
        self.list_all_commands(msg)

    @command("^(enable|disable|reload|status) plugin ([A-Za-z]+)$", access=ACCESS["plugin_manage"])
    def manage_plugin(self, msg):
        """`enable plugin <plugin>`: enables `<plugin>`.
`disable plugin <plugin>`: disables `<plugin>`.
`reload plugin <plugin>`: reloads `<plugin>`.
`status plugin <plugin>`: fetches the status of `<plugin>`."""
        plugins = self.core.plugin.list()
        plugin = msg.arguments[1]
        action = msg.arguments[0]

        if plugin in plugins:
            if action == "enable":
                if plugins[plugin]['status'] == "Disabled":
                    self.core.plugin.load(plugin)
                    self.say(msg.channel, "Enabled plugin: **{}**".format(plugin))
                else:
                    self.say(msg.channel, "{} is already enabled".format(plugin))

            elif action == "disable":
                if plugins[plugin]['status'] == "Enabled":
                    self.core.plugin.unload(plugin)
                    self.say(msg.channel, "Disabled plugin: **{}**".format(plugin))
                else:
                    self.say(msg.channel, "{} is already disabled".format(plugin))

            elif action == "reload":
                if plugins[plugin]['status'] == "Disabled":
                    self.core.plugin.reload(plugin)
                    self.say(msg.channel, "Reloaded plugin: **{}**".format(plugin))
        else:
            self.say(msg.channel, "I don't have a plugin by that name.")

    @subscribe("connect")
    def on_connect(self, *args, **kwargs):
        self.login_time = time.time()

    @command("^uptime$", access=ACCESS['uptime'])
    def uptime(self, msg):
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

        self.say(msg.channel, "I've been connected for: **" + readable_time(uptime) + "**")
