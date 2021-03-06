"""
    Class Name : Penguin
    Bot Version : 2.1.1

    Description:
        Provides an extensible engine for plugins to interact with;
        replaces Core.
        Features:
            - Publish / Subscribe Event System
            - Plugin manager
            - Configuration manager
            - User, Channel and Group Date manager

    Contributors:
        - Patrick Hennessy
        - Euklyd

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import discord

import conf.settings as config

from core.ACL import ACL
from core.Command import CommandManager
from core.Database import Database
from core.Event import EventManager
from core.Filter import FilterManager
from core.PluginManager import PluginManager
from core.Imgur import Imgur
from core.LogManager import LogManager
from core.MusicManager import MusicManager
from core.EmojiManager import EmojiManager

from imp import load_module, find_module
from sys import stdout, path, exit
import asyncio
import inspect
import logging
import logging.handlers
import time


class PenguinBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugins_loaded = False
        # Setup logger and load config
        self.setup_logger()
        self.config = self.load_config("settings")
        self.triggers = self.config.trigger
        if (type(self.config.trigger) is tuple or
                type(self.config.trigger) is list
        ):  # noqa E124
            self.default_trigger = self.config.trigger[0]
        else:
            self.default_trigger = self.config.trigger
        self.test_server = self.config.test_server
        self.bot_name = self.config.username

        # Setup managers
        self.plugin = PluginManager(self)
        self.event = EventManager(self)
        self.command = CommandManager(self)
        self.filter = FilterManager(self)
        self.ACL = ACL(self, self.config.backdoor)
        self.emoji = EmojiManager(self)

        if (self.config.channel_logging is True):
            self.log_manager = LogManager(self)

        if ("Voice" in self.config.plugins):
            if (self.config.imgur_api['id'] is None):
                raise RuntimeError("Music requires imgur credentials")
            self.music_manager = MusicManager(self)

        if (self.config.imgur_api['id'] is not None):
            self.imgur = Imgur(self)

        self.last_update = time.time()

    def run(self, *args):
        """
            Args:
                token (str): Bot auth token.
        """
        self.logger.info("Starting event loop")
        try:
            self.loop.run_until_complete(
                self.start(self.config.connector_options['token'])
            )
        except KeyboardInterrupt:
            self.exit()
        finally:
            self.loop.close()
            self.logger.info("self.loop closed")

    def exit(self):
        self.loop.run_until_complete(self.shutdown())
        self.logger.info("exit() complete")

    async def shutdown(self):
        """
            Summary:
                Does any nessessary clean up (like killing threads)
                before the bot exits

            Args:
                None

            Returns:
                None
        """
        # for task in asyncio.Task.all_tasks():
        #     self.logger.info(task)
        for plugin in config.plugins:
            await self.plugin.unload(plugin)
        await self.logout()

        for task in asyncio.Task.all_tasks():
            self.logger.info(task)
        self.logger.info("shutdown() complete")

    async def on_ready(self):
        """
            Summary:
                Called when the bot is ready by the Client superclass.

            Inherited from discord.Client.
        """
        self.logger.info("Connected to Discord")
        if (self.config.channel_logging is True):
            self.log_manager.update_info()

        if (self.plugins_loaded is False):
            await self.load_plugins()

    # async def cycle_games(self, games):
    #     while (True):
    #         for game in games:
    #             self.presence_args = {
    #                 'game': discord.Game(
    #                     name=game,
    #                     url=self.config.repo,
    #                     type=1
    #                 )
    #             }
    #             try:
    #                 await self.change_presence(**self.presence_args)
    #                 self.logger.info("changed game to '{}'".format(game))
    #             except discord.errors.HTTPException as e:
    #                 self.logger.warning("cycle_games: {}".format(e))
    #                 await asyncio.sleep(5.0)
    #             finally:
    #                 await asyncio.sleep(10.0)

    async def on_message(self, msg):
        """
            Summary:
                Called when the bot recieves a message.

            Inherited from discord.Client.
        """
        # self.logger.info(
        #     "Message Recieved: [Name:{}][UID:{}][CID:{}]: {}".format(
        #         msg.author.name,
        #         msg.author.id,
        #         msg.channel.id,
        #         msg.content
        #     )
        # )
        # self.logger.info("<{}>  {}".format(msg.author.name, msg.content))
        if (self.config.channel_logging is True):
            self.log_manager.log_message(msg)
        else:
            self.logger.info(
                ("Message Recieved: [Name:{uname}][UID:{uid}]"
                 "[CName:{cname}][CID:{cid}]: {content}").format(
                    uname=msg.author.name,
                    uid=msg.author.id,
                    cname=msg.channel.name,
                    cid=msg.channel.id,
                    content=msg.content
                )
            )
        await self.filter.check(msg)
        await self.command.check(msg)

        # embed debugging stuff:
        # if (msg.author.id == "136107769680887808"):
        #     self.logger.info(msg.embeds[0])
        # elif ((msg.author.id == "159985870458322944" or
        #        msg.author.id == "241170316045451264" or
        #        msg.author.id == "100165629373337600") and
        #       len(msg.embeds) >= 1):
        #     self.logger.info(msg.embeds[0])

    # async def on_server_update(self, before, after):
    #     """
    #         Summary:
    #             Called when the bot is notified that a channel is modified
    #
    #         Args:
    #             before (Server): The server object before being updated
    #             after (Server): The server object after being updated
    #
    #         Inherited from discord.Client.
    #     """
    #     pass
    # I don't actually want to be updating the server filetree during operation

    async def on_channel_update(self, before, after):
        """
            Summary:
                Called when the bot is notified that a channel is modified

            Args:
                before (Channel): The channel object before being updated
                after (Channel): The channel object after being updated

            Inherited from discord.Client.
        """
        if (self.config.channel_logging is True):
            self.log_manager.update_channel(after)
        else:
            pass

    def setup_logger(self):
        """
            Summary:
                Creates global settings for all logging
                Pretty colors are pretty

            Args:
                None

            Returns:
                None
        """
        from colorlog import ColoredFormatter
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
        logging.getLogger('peewee').setLevel(logging.WARNING)

        log = logging.getLogger('')
        log.setLevel(logging.INFO)

        # Create console handler
        console_hdlr = logging.StreamHandler(stdout)
        console_formatter = ColoredFormatter(
            "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)-25.25s%(reset)s %(white)s%(message)s%(reset)s",  # noqa E501
            datefmt="[%m/%d/%Y %H:%M:%S]",
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bg_red',
            }
        )
        console_hdlr.setFormatter(console_formatter)
        console_hdlr.setLevel(logging.INFO)
        log.addHandler(console_hdlr)

        # Create log file handler
        file_hdlr = logging.handlers.TimedRotatingFileHandler(
            "logs/botlog", when="midnight"
        )
        file_formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)-25.25s %(message)s",
            datefmt="[%m/%d/%Y %H:%M:%S]"
        )
        file_hdlr.setFormatter(file_formatter)
        file_hdlr.setLevel(logging.INFO)
        log.addHandler(file_hdlr)

        self.logger = logging.getLogger(__name__)

    def load_config(self, name):
        """
            Summary:
                Establishes a connection to the server
                Emits login event
                Starts message consumer thread
                Expects to have already loaded connection module
                Exits if it cannot find or load the config

            Args:
                name (str): Name of the config module to be loaded

            Returns:
                (Config): instance of Config class, storing all global
                config options
        """

        path.append("conf")

        try:
            config_canadiate = find_module(name, path=['conf'])
            config_module = load_module(name, *config_canadiate)

            self.logger.info("Loaded configuration from \"\"".format(
                config_canadiate[1]
            ))
            logging.getLogger('').setLevel(config_module.log_level)

            return config_module

        except ImportError as e:
            self.logger.critical("ImportError: " + str(e))
            exit(1)
        except AttributeError as e:
            self.logger.critical("Config class not found in conf/" + name)
            exit(1)

    # def load_connector(self, core):
    #     """
    #         Summary:
    #             Looks for and loads the connector defined in config
    #             Will exit if cannot find or load the connector module
    #
    #         Args:
    #             None
    #
    #         Returns:
    #             (Connector): The low level connection manager instance
    #     """
    #     path.append("connectors")
    #
    #     try:
    #         connector_candidate = find_module(
    #             config.connector, path=["connectors"]
    #         )
    #         connector_module = load_module(
    #             config.connector, *connector_candidate
    #         )
    #         connector = getattr(connector_module, config.connector)(
    #             core, **config.connector_options
    #         )
    #         self.logger.info("Loaded connector from: \"\"".format(
    #             connector_candidate[1]
    #         ))
    #
    #         return connector
    #
    #     except ImportError as e:
    #         self.logger.critical("ImportError: {}".format(str(e)))
    #         exit(1)
    #     except AttributeError as e:
    #         print(e)
    #         self.logger.critical("Could not find connector class: {}".format(
    #             config.connector
    #         ))
    #         exit(1)

    async def load_plugins(self):
        """
            Summary:
                Looks in plugins list in config and attempts to load each

            Args:
                None

            Returns:
                None
        """
        self.logger.info("Loading Plugins")
        for plugin in config.plugins:
            await self.plugin.load(plugin)
        self.plugins_loaded = True
