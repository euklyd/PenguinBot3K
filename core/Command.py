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

# import threading
import re
import logging


class Command():
    def __init__(self, pattern, callback, trigger="", access=0, silent=False,
                 name=None, plugin=None, doc_brief=None, doc_detail=None,
                 flags=0):
        self.pattern   = pattern
        self.access    = access
        self.callback  = callback
        self.trigger   = trigger
        self.silent    = silent
        self.name      = name
        self.plugin    = plugin
        self.doc_brief = doc_brief
        self.flags     = flags
        if (doc_detail is None):
            self.doc_detail = doc_brief
        else:
            self.doc_detail = doc_detail

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
        triggers = self.core.triggers
        if type(triggers) == tuple:
            for trigger in triggers:
                if message.content.startswith(trigger):
                    # message.content needs to be set to be the stripped
                    # content later so that in case of fall-through, it
                    # doesn't break filters.
                    content = message.content.replace(trigger, "", 1)
                    break
            else:
                # not found
                return
        elif message.content.startswith(trigger):
            content = message.content.replace(triggers, "", 1)
        else:
            # not found
            return

        if message.author.id == self.core.config.backdoor:
            OVERRIDE = '(.*) +-a <@!?(\d+)>$'
            match = re.search(OVERRIDE, content)
            if match:
                content = match.group(1)
                author_id = match.group(2)
                author = message.server.get_member(match.group(2))

                # strip off the -a mention
                # message.mentions = message.mentions[:-1]
                index = -1
                for i, member in enumerate(message.mentions):
                    if member.id == author_id:
                        index = i
                        break
                message.mentions.pop(i)

                if author:
                    message.author = author
                else:
                    author = await self.core.get_user_info(match.group(2))
                    if author:
                        message.author = author

        commands = list(self.commands.items())
        for key, command in commands:
            match = re.search(command.pattern, content, flags=command.flags)

            if (match):
                self.logger.info("'{}' detected".format(message.content))
                if (self.core.ACL.getAccess(message.author.id) >=
                            command.access or
                        message.author.id == self.core.config.backdoor or
                        self.core.ACL.get_user_role_access(message.author,
                            command.plugin) >= command.access
                ):  # noqa E124
                    message.content = content
                    arguments = match.groups()
                    self.logger.info("'{}' invoked".format(
                                     message.content))
                    await command.invoke(message, arguments)
                elif (not command.silent):
                    await self.core.send_message(
                        message.channel,
                        "\u200B<@!{}>: Sorry, you need `{}` access to use "
                        "that command.".format(
                            message.author.id, command.access)
                    )  # TODO: get rid of zero-width space?
                    self.logger.info("'{}' (from {} in {}) refused".format(
                        message.content,
                        message.author.id,
                        message.channel)
                    )
                    self.logger.info(
                        "{} only has ACL access level of {}".format(
                            message.author.id,
                            self.core.ACL.getAccess(message.author.id))
                    )

    def register(self, pattern, callback, trigger="", access=0, silent=False,
                 cmd_name=None, doc_brief=None, doc_detail=None, flags=0):
        """
            Summary:
                Pushes command instance to command list

            Args:
                pattern (str):   Regex that the message parser will match with
                callback (func): Function object that will be invoked when
                                 message parser finds a match
                trigger (str):   Beginning of the string to denote a command,
                                 default is in the config
                access (int):    Amount of access required to invoke a command
                silent (bool):   Squelch access error messages

            Returns:
                None
        """
        clazz = type(callback.__self__).__name__
        name = clazz + "." + callback.__name__

        if (name in self.commands):
            self.logger.warning(
                "Duplicate command '{clazz}.{name}'. "
                "Skipping registration.".format(clazz=clazz, name=name)
            )
            return
        else:
            self.logger.debug("Registered command '{clazz}.{name}'".format(
                              clazz=clazz, name=name))

            if (trigger is None):
                trigger = ""
            elif (trigger == ""):
                trigger = self.core.config.trigger

            self.commands[name] = Command(
                pattern,
                callback,
                trigger=trigger,
                access=access,
                silent=silent,
                name=cmd_name,
                plugin=clazz,
                doc_brief=doc_brief,
                doc_detail=doc_detail,
                flags=flags
            )
            # self.logger.info(self.commands[name])
            self.logger.debug("Command has trigger: {}".format(trigger))

    def unregister(self, cmd_name):
        """
            Summary:
                Unregisters a command
                Removes command instance from command list
                Command will no longer run when message parser finds a match

            Args:
                cmd_name (str): Name of the command to unregister

            Returns:
                None
        """
        if (cmd_name in self.commands):
            command = self.commands[cmd_name]

            clazz = type(command.callback.__self__).__name__
            name = clazz + "." + command.callback.__name__

            del self.commands[cmd_name]
            self.logger.debug("Unregistered command '{}'".format(name))

        else:
            self.logger.warning(
                "Cannot unregister '{}', command not found.".format(cmd_name)
            )
