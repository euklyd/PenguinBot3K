"""
    Plugin Name : Tournament
    Plugin Version : 0.1

    Description:
        Provides basic utility commands, e.g., coin flips.

    Contributors:
        - Popguin / Euklyd

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *
import logging
import random

logger = logging.getLogger(__name__)


class Tournament(Plugin):
    def activate(self):
        self.matches = {}
        self.active_picks = {}
        self.tourney_channel = "190782867381420033"
        random.seed()
        marshu = "http://www.marshu.com/articles/images-website/articles/presidents-on-coins/"  # noqa E501
        self.coins = {"heads": [marshu+"penny-cent-coin-head-thumb.jpg",
                                marshu+"nickel-head-coin-thumb.jpg",
                                marshu+"dime-coin-head-thumb.jpg",
                                marshu+"quarter-coin-head-thumb.jpg",
                                marshu+"half-dollar-coin-head-thumb.jpg"],
                      "tails": [marshu+"penny-cent-coin-tail-thumb.jpg",
                                marshu+"nickel-coin-tail-thumb.jpg",
                                marshu+"dime-coin-tail-thumb.jpg",
                                marshu+"quarter-coin-tail-thumb.jpg",
                                marshu+"half-dollar-coin-tail-thumb.jpg"]
                      }
        pass

    @command("^flip", access=-1)
    def flip(self, msg):
        """`flip`: Flips a coin that will come up either heads or tails. Images of many types of coins are included."""
        coin = random.randint(0, 10)
        if (coin % 2 == 0):
            self.say(msg.channel, self.coins["heads"][int(coin/5)])
        else:
            tails = random.randint(0, 10)
            if (tails % 10 == 0):
                self.say(msg.channel, "https://puu.sh/rlzdJ/c9489a02b4.png")
            else:
                self.say(msg.channel, self.coins["tails"][int(coin/5)])

    @command("^flip-text", access=-1)
    def flip_text(self, msg):
        """`flip-text`: Flips a coin that will come up either heads or tails. Result will be plain text, no images."""
        coin = random.randint(0, 1)
        if (coin % 2 == 0):
            self.say(msg.channel, "<@!{}> flipped a coin and it came up **heads**!".format(msg.sender))
        else:
            self.say(msg.channel, "<@!{}> flipped a coin and it came up **tails**!".format(msg.sender))

    @command("^selection process$", access=-1)
    def select_help(self, msg):
        """`selection process`: prints the rules for stage and character selection."""
        response_str  = "**Stage and character selection process:**"
        response_str += "\n\n**Game 1:**"
        response_str += "\n1)  Both players choose their characters, and tell each other their choices."
        response_str += "\n1a) *If either player wishes, they may opt for a double-blind pick, in which both players select their character secretly, and announce at the same time. The `{}blind pick` command is helpful for this.*".format(self.core.config.trigger)
        response_str += "\n2)  The first player to strike a stage is determined. The `{}flip` command provides a coin flip for this use.".format(self.core.config.trigger)
        response_str += "\n3)  The player who won the flip bans a stage from the list of starter stages."
        response_str += "\n4)  The second player bans two stages from the remaining starter stages."
        response_str += "\n5)  The first player strikes one more stage."
        response_str += "\n6)  The remaining stage is the stage on which Game 1 will be played."
        response_str += "\n\n**Subsequent games:**"
        response_str += "\n1)  The winner of the previous game bans one stage from the list of starter and counterpick stages."
        response_str += "\n2)  The loser picks one stage from the remaining stages."
        response_str += "\n2a) *This cannot be a stage that the loser has won on previously.*"
        response_str += "\n3)  The winner selects their character (including 'not switching'), and informs the loser. "
        response_str += "\n4)  The loser selects their character, and the game commences."
        self.say(msg.channel, response_str)

    @command("^blind pick$", access=-1)
    def blind_pick_empty(self, msg):
        self.say(msg.channel, "<@!{}>, please @mention two players as well.".format(msg.sender))

    @command("^blind pick <@!?([0-9]+)> <@!?([0-9]+)>", access=-1)
    def blind_pick(self, msg):
        """`blind pick <@player1> <@player2>`: initiates a blind pick between `<player1>` and `<player2>`"""
        players = msg.arguments
        if (players[0] == players[1]):
            self.say(msg.channel, "**Error:** A blind pick needs two different players!")
        elif players[0] in self.matches:
            self.say(msg.channel, "**Error:** <!@{}> is already in a blind pick!".format(players[0]))
        elif players[1] in self.matches:
            self.say(msg.channel, "**Error:** <!@{}> is already in a blind pick!".format(players[1]))
        else:
            self.active_picks[players[0]] = ""
            self.active_picks[players[1]] = ""
            self.matches[players[0]] = players[1]
            self.matches[players[1]] = players[0]
            response_str = "Blind pick initiated between **<@!{}>** and **<@!{}>**".format(
                players[0], players[1]
            )
            response_str += "\nFor detailed guidance, use the `{} eyesight to the blind` command.".format(self.core.config.trigger)
            self.say(msg.channel, response_str)

    @command("^eyesight to the blind$", access=-1)
    def eyesight_to_the_blind(self, msg):
        response_str  = "**Double-blind character selection:**"
        response_str += "\nA double-blind pick is when both players choose their character secretly, then both picks are announced at the same time."
        response_str += "\nThis is frequently done if one or both of the players is concerned about being character counterpicked on the first game."
        response_str += "\nWhisper `waddle select <character>` to <@!225429735633715201> to make a selection."
        response_str += "\ne.g., privately whisper `waddle select King Dedede` to select \U0001F427 **THE \U0001F427 KING \U0001F427 HIMSELF \U0001F427**"
        self.say(msg.channel, response_str)

    @command("^select (.*)", access=-1)
    def select_character(self, msg):
        character = msg.arguments[0]
        if msg.sender in self.matches:
            player = msg.sender
            opponent = self.matches[player]
            self.active_picks[player] = character
            self.say(self.tourney_channel, "<@!{}> has selected their character!".format(msg.sender))
            if self.active_picks[opponent] is not "":
                pick_str = "**Blind pick complete!**\n<@!{}> has selected **{}**\n<@!{}> has selected **{}**".format(
                    player, self.active_picks[player],
                    opponent, self.active_picks[opponent]
                )
                self.say(self.tourney_channel, pick_str)
                self.matches.pop(player)
                self.matches.pop(opponent)
                self.active_picks.pop(player)
                self.active_picks.pop(opponent)
        else:
            self.whisper(msg.sender, "**Error:** You are not currently in a blind pick!")

    @command("cancel blind pick$", access=-1)
    def cancel_blind_pick(self, msg):
        """`cancel blind pick:` cancel the blind pick you're currently a part in."""
        if msg.sender in self.matches:
            player = msg.sender
            opponent = self.matches[player]
            self.matches.pop(player)
            self.matches.pop(opponent)
            self.active_picks.pop(player)
            self.active_picks.pop(opponent)
            self.say(self.tourney_channel, "Cancelled the blick pick between <@!{}> and <@!{}>.".format(player, opponent))
        else:
            self.say(msg.channel, "**Error:** <@!{}>, you are not currently in a blind pick!".format(msg.sender))
