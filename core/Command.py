"""
    Class Name : Command

    Description:
        Manager for commands

    Contributors:
        - Patrick Hennessy
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import threading
import re
import logging


class Command():
    def __init__(self, pattern, callback, trigger="", access=0, silent=False):
        self.pattern  = pattern
        self.access   = access
        self.callback = callback
        self.trigger  = trigger
        self.silent   = silent

        self.logger = logging.getLogger(__name__)

    def __str__(self):
        return self.callback.__name__

    async def invoke(self, message, arguments):
        await self.callback(message, arguments)


class CommandManager():
    def __init__(self, core):
        self.commands = {}
        self.core = core
        self.logger = logging.getLogger(__name__)

    async def check(self, message):
        """
            Summary:
                Checks if an incoming message is a command
                Invokes any command that matches the criteria

            Args:
                message (Message): A message instance from discord.Message

            Returns:
                None
        """
        commands = list(self.commands.items())
        # self.logger.info(commands)
        for key, command in commands:
            # self.logger.info("key:     {}".format(key))
            # self.logger.info("command: {}".format(command))
            # self.logger.info("trigger: {}".format(command.trigger))
            if (message.content.startswith(command.trigger)):
                t = ""  # debug
                if type(command.trigger) == tuple:
                    for trigger in command.trigger:
                        content = message.content.replace(trigger, "", 1)
                        if (content != message.content):
                            t = trigger # debug
                            break
                else:
                    t = command.trigger # debug
                    content = message.content.replace(command.trigger, "", 1)

                match   = re.search(command.pattern, content)

                if (match):
                    # self.logger.info("trigger '{}' matched!".format(t))  # debug
                    # self.logger.debug("'{}' registered")
                    self.logger.info("'{}' registered".format(message.content))
                    if (self.core.ACL.getAccess(message.author.id) >= command.access or message.author.id == self.core.config.backdoor):
                        message.content = content
                        # message.arguments = match
                        arguments = match.groups()
                        # print(arguments)
                        self.logger.info("'{}' invoked".format(message.content))
                        await command.invoke(message, arguments)
                    elif (not command.silent):
                        await self.core.send_message(message.channel, u"\u200B<@!{}>: Sorry, you need `{}` access to use that command.".format(message.author.id, command.access))
                        self.logger.info("'{}' (from {} in {}) refused".format(message.content, message.author.id, message.channel))
                        self.logger.info("{} only has ACL access level of {}".format(message.author.id, self.core.ACL.getAccess(message.author.id)))

    def register(self, pattern, callback, trigger="", access=0, silent=False):
        """
            Summary:
                Pushes command instance to command list

            Args:
                pattern (str): Regex that the message parser will match with
                callback (func): Function object that will be invoked when message parser finds a match
                trigger (str): Beginning of the string to denote a command, default is in the config
                access (int): Amount of access required to invoke a command
                silent (bool): Squelch access error messages

            Returns:
                None
        """
        clazz = type(callback.__self__).__name__
        name = clazz + "." + callback.__name__

        if (name in self.commands):
            self.logger.warning("Duplicate command \"" + clazz + "." + name + "\". Skipping registration.")
            return
        else:
            self.logger.debug("Registered command \"" +  clazz + "." + name + "\"")

            if (trigger is None):
                trigger = ""
            elif (trigger == ""):
                trigger = self.core.config.trigger

            self.commands[name] = Command(
                pattern,
                callback,
                trigger=trigger,
                access=access,
                silent=silent
            )
            self.logger.debug("Command has trigger: {}".format(trigger))

    def unregister(self, command_name):
        """
            Summary:
                Unregisters a command
                Removes command instance from command list
                Command will no longer run when message parser finds a match

            Args:
                command_name (str): Name of the command to unregister

            Returns:
                None
        """
        if (command_name in self.commands):
            command = self.commands[command_name]

            clazz = type(command.callback.__self__).__name__
            name = clazz + "." + command.callback.__name__

            del self.commands[command_name]
            self.logger.debug("Unregistered command \"" + name + "\"")

        else:
            self.logger.warning("Cannot unregister \"" + command_name + "\", command not found.")
