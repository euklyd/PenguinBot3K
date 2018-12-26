"""
    Class Name : Filter
    Class Version: 0.1

    Description:
        Filters messages (not for commands) and applies actions accordingly.
        Based on the framework used by the Command.py core module.

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import logging
import re


class Filter():
    def __init__(self, pattern, callback, ignore=None, name=None, plugin=None,
                 server=None, doc_brief=None, doc_detail=None, flags=0):
        self.pattern   = pattern
        self.callback  = callback
        self.ignore    = ignore
        self.name      = name
        self.plugin    = plugin
        self.server    = server
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


class FilterManager():
    def __init__(self, core):
        self.filters = {}
        self.core = core
        self.logger = logging.getLogger(__name__)

    async def check(self, message):
        """
            Summary:
                Checks an incoming message against all filters
                Invokes any filter that catches the message

            Args:
                message (Message): A message instance from discord.Message

            Returns:
                None
        """
        if message.author.bot:
            return
        if message.server is None:
            return
        filters = list(self.filters.items())
        # self.logger.info(filters)
        for key, msg_filter in filters:
            # self.logger.info("key:    {}".format(key))
            # self.logger.info("filter: {}".format(msg_filter))
            # self.logger.info("flags:  {}".format(msg_filter.flags))
            match = re.search(msg_filter.pattern, message.content, msg_filter.flags)
            if (msg_filter.server is not None and
                match and (
                    msg_filter.server is True or
                    message.server.id in msg_filter.server)
            ):
                # self.logger.debug("'{}' detected")
                self.logger.info("{}: '{}' detected".format(msg_filter.name, message.content))
                if (msg_filter.ignore is None or self.core.ACL.getAccess(message.author.id) < msg_filter.ignore):
                    arguments = match.groups()
                    # self.logger.info(arguments)
                    self.logger.info("'{}' invoked".format(message.content))
                    await msg_filter.invoke(message, arguments)

    def register(self, pattern, callback, ignore=None, filter_name=None,
                 server=None, doc_brief=None, doc_detail=None, flags=0):
        """
            Summary:
                Pushes Filter instance to filter list

            Args:
                pattern (str): Regex that the message parser will match with
                callback (func): Function object that will be invoked when message parser finds a match
                ignore (int): Ignore messages from authors with access greater than this amount

            Returns:
                None
        """
        clazz = type(callback.__self__).__name__
        name = clazz + "." + callback.__name__

        if (name in self.filters):
            self.logger.warning("Duplicate filter \"" + clazz + "." + name + "\". Skipping registration.")
            return
        else:
            self.logger.debug("Registered filter \"" +  clazz + "." + name + "\"")

            if (server == "TEST"):
                server = self.core.test_server

            self.filters[name] = Filter(
                pattern,
                callback,
                ignore=ignore,
                name=filter_name,
                plugin=clazz,
                server=server,
                doc_brief=doc_brief,
                doc_detail=doc_detail,
                flags=flags
            )
            # self.logger.info(self.filters[name])

    def unregister(self, filter_name):
        """
            Summary:
                Unregisters a filter
                Removes Filter instance from filter list
                Filter will no longer run when message parser finds a match

            Args:
                filter_name (str): Name of the filter to unregister

            Returns:
                None
        """
        if (filter_name in self.filters):
            msg_filter = self.filters[filter_name]

            clazz = type(msg_filter.callback.__self__).__name__
            name = clazz + "." + msg_filter.callback.__name__

            del self.filters[filter_name]
            self.logger.debug("Unregistered filter \"" + name + "\"")

        else:
            self.logger.warning("Cannot unregister \"" + filter_name + "\", filter not found.")
