"""
    Plugin Name : Macro
    Plugin Version : 3.2.1

    Description:
        Transforms text into text with a macro applied.

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *

import discord
import logging
import random

logger = logging.getLogger(__name__)


class Macro(Plugin):
    async def activate(self):
        pass

    @command("^emojify ([\u2600-\u26FF\u2700-\u27BF\U0001F1E6-\U0001F1FF\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF]|(?:<:[A-Za-z0-9_]*:\d*>)) (.*)",
             access=-1, name='emojify',
             doc_brief="`emojify <emoji> <sentence>`: replace all spaces in "
             "`<sentence>` with `<emoji>`")
    async def emojify(self, msg, arguments):
        """
        0x1F600...0x1F64F, // Emoticons
        0x1F300...0x1F5FF, // Misc Symbols and Pictographs
        0x1F680...0x1F6FF, // Transport and Map
        0x2600...0x26FF,   // Misc symbols
        0x2700...0x27BF,   // Dingbats
        0xFE00...0xFE0F    // Variation Selectors
        """
        self.logger.debug(arguments)
        emoji = arguments[0]
        reply = arguments[1].replace(' ', ' {} '.format(emoji))
        reply = "<@!{}>: {}".format(msg.author.id, reply)
        self.logger.info(reply)
        await self.delete_message(msg)
        await self.send_message(msg.channel, reply)

    # Hidden special bonus version of emojify.
    @command('^emojify -f "(.*|(?:<:.*:\d*>)*)" (.*)', access=-1,
             name='emojify',
             doc_detail='`emojify -f "<anything>" <sentence>`: '
             'Like `emojify`, but instead of inserting an emoji, '
             'inserts `<anything>`')
    async def emojify_full(self, msg, arguments):
        self.logger.debug(arguments)
        emoji = arguments[0]
        reply = arguments[1].replace(' ', ' {} '.format(emoji))
        reply = "<@!{}>: {}".format(msg.author.id, reply)
        self.logger.info(reply)
        await self.delete_message(msg)
        await self.send_message(msg.channel, reply)

    @command('^emojify -w "(.*|(?:<:.*:\d*>))" (.*)', access=50,
             name='emojify',
             doc_detail='`emojify -w "<anything>" <sentence>`: as standard '
             '`emojify -f`, but sends output to the user in a DM.')
    async def emojify_whisper(self, msg, arguments):
        self.logger.debug(arguments)
        emoji = arguments[0]
        reply = arguments[1].replace(' ', ' {} '.format(emoji))
        reply = "<@!{}>: {}".format(msg.author.id, reply)
        self.logger.info(reply)
        await self.delete_message(msg)
        await self.send_whisper(msg.author, reply)

    @command("^cloud$", access=100, name='cloud',
             doc_brief="`cloud`: Prints out the dankest of ☁ memes")
    async def cloud(self, msg, arguments):
        cloudcopypasta = (
            "║\\\n"
            "║▒\\  IT'S DANGEROUS\n"
            "║▒▒\\\n"
            "║░▒║ TO LOSE GAME 1,\n"
            "║░▒║\n"
            "║░▒║ TAKE THIS!\n"
            "║░▒║\n"
            "║░▒║\n"
            "║░▒║\n"
            "║░▒║\n"
            "║░▒║\n"
            "▓▓▓▓\n"
            "[█▓]\n"
            "[█▓]\n"
            "[█▓]"
        )
        await self.send_message(msg.channel, cloudcopypasta)

    @command("^waddle|ddd|THE KING$", access=100, name='waddle',
             doc_brief="`waddle`: Prints out the dankest of 🐧 Penguin 🐧 memes")
    async def waddle(self, msg, arguments):
        dddpasta = ("🐧 **King Dedede** 🐧 is definitely **top tier**. "
                    "The king's got it all: disjoint ⚔, power 💪, recovery ✈, "
                    "and damaging throw combos 💥. He is the hardest character "
                    "in the game to kill vertically 💀, and with the safest "
                    "and strongest ways to kill 💀 being traditionally "
                    "vertical, that's huge ⛰. His presence at the ledge is "
                    "not to be ignored, as with clever Gordo setups, he can "
                    "cover most if not all ledge options with a potentially "
                    "deadly hitbox 💀. He might be combo food 🍖, but he wants "
                    "all that 💢 rage 💢 so he can kill with his safe and "
                    "powerful back air 🔨🐻 even earlier than usual. "
                    "**An obvious member of 🐧 top tier🐧.**\n"
                    "🐧 **THE 🐧 KING 🐧 IS 🐧 TOP 🐧 TIER** 🐧")
        await self.send_message(msg.channel, dddpasta)

    @command("^plumber|cancer|<:mario:[0-9]*>|mario$", access=100,
             name='plumber', doc_brief="`plumber`: Prints out the dankest of "
             "🚽 Plumber 🚽 memes")
    async def plumber(self, msg, arguments):
        mario = self.core.emoji.emoji(msg.server, ['mario'])
        m2 = self.core.emoji.emoji(
            msg.server,
            ['sunglasses_mewtwo', 'shades_mewtwo', 'mewtwo_shades'])
        mariopasta = ("{mario} Mario {mario} "
                      "is definitely **not top tier**. The plumber's got "
                      "nothing; no range ✖ , no power 😩 , mediocre recovery "
                      "😐 , and bad matchups "
                      "{sunglasses_mewtwo} ☁ He isn't very "
                      "fast 🐢 , and he doesn't have any strong kill set ups "
                      "like other top tiers 🍌 ⬇ 👏 ⬆ ✊. The only reason "
                      "Ally and ANTi were able to win supermajors with him 🏆 "
                      "is because of **pure skill**, and we will be "
                      "blessed 🙏  if we ever see two top players carry an "
                      "upper mid-tier so far again. Obviously **not** a "
                      "member of the {mario} top tier "
                      "{mario}".format(
                        mario=mario,
                        sunglasses_mewtwo=m2))
        await self.send_message(msg.channel, mariopasta)

    @command("^md|doc|doctor|💊$", access=100, name='doctor',
             doc_brief="`doctor`: Prints out the dankest of 💊 Doctor 💊 memes")
    async def doctor(self, msg, arguments):
        mario = self.core.emoji.emoji(msg.server, ['mario'])
        docpasta = ("💊Dr Mario💊 is definitely top tier. "
                    "The doctor's got it all: good pokes 🐻, KO power ⬆👷😂👌, "
                    "amazing oos ⬆✊, and damaging combos 👷👷👷. His presence "
                    "offstage is not to be ignored, as with proper ⬇🅱 "
                    "timing, he can cover several recoveries with a hitbox "
                    "that sends opponents downwards for a gimp 🌪. "
                    "He can also use upsmash to cover several ledge options "
                    "while being completely safe 👷. He might move slow 🐌, "
                    "but he has a projectile 💊 that can force approaches that "
                    "he can punish with his safe and powerful upsmash 👷💥. "
                    "An obvious member of top 5, unlike that worthless clone "
                    "{mario}😕😩😫.\n"
                    "💊 THE 💊 DOCTOR 💊 IS 💊 A 💊 TOP 💊 TIER 💊".format(
                        mario=mario
                    ))
        await self.send_message(msg.channel, docpasta)

    @command("^penguin|\U0001F427$", access=-1, name='penguin',
             doc_brief="`penguin`: Embeds the Skype `(penguin)` emoji")
    async def penguin(self, msg, arguments):
        penguin_url = "https://i.imgur.com/MGNa91r.gif"
        user = msg.server.get_member(self.core.user.id)
        em = discord.Embed(color=user.color)
        em.set_thumbnail(url=penguin_url)
        em.set_footer(
            text="",
            icon_url=user.avatar_url
        )
        await self.send_message(msg.channel, embed=em)
        self.logger.debug(em.to_dict())

    @command("^olaf|integrity$", access=-1, name='integrity',
             doc_detail="`integrity`: Embeds the face of Integrity irl")
    async def olaftegrity(self, msg, arguments):
        olaf_url = "http://i.imgur.com/791NLN5.png"
        user = msg.server.get_member(self.core.user.id)
        em = discord.Embed(color=user.color)
        em.set_thumbnail(url=olaf_url)
        await self.send_message(msg.channel, embed=em)

    @command("^boy|roy|🔥🔥🔥|ph1r3$", access=100, name='ph1r3',
             doc_brief="`ph1r3`: Prints out the dankest of 🔥 ph1r3 🔥 memes")
    async def ph1r3(self, msg, arguments):
        marf = self.core.emoji.emoji(msg.server, ['ppmd_marth', 'MarthSip'])
        roypasta = []
        roypasta.append(
            "🔥 Roy 🔥 is definitely low tier.  The boy got nothing:  "
            "No Speed 🏃 , Shitty KO Power 💥 , 0% off throws, "
            "and a pencil  ✏ disjoint 👌 🗡 .  Let's not forget that in his "
            "own respective game 😳 he's a total beta nerd 🤓 . "
            "His presence all over the stage should not be ignored, "
            "a single read 📖 gets you nothing 💀 at 40% 👀 , 🔥 🔥 🔥 you're "
            "not at risk ⚠ 💤 when trying to gimp him, and his 🔥 ⚔ is "
            "completely laggy 🐌 and can OHKO you at 304% 👌 👌 👌 😂 . "
            "He may be combo food 🍖 , but he wants that DING DONG 🐒 💥 💀 , "
            "so he can die you at 60% from a single grab 💥 💥 💥 👀 . "
            "Roy is the bottom top 5 sword character, unlike that amazing "
            "original character ⚔ Marth {marth} 😕 😩 😫 .\n\n"
            "**🔥 ROY'S 🔥 ACTUAL 🔥 SHIT 🔥**".format(marth=marf))
        roypasta.append(
            "🔥 **Roy** 🔥 is definitely **top tier**.  The boy got it all:  "
            "Speed 🏃 , KO Power 💥 , 💯 off throws, and disjoint 👌 ⚔ .  "
            "Let's not forget that in his own respective game 😘 he has "
            "6 different marriage options 😘 👰 .  "
            "His presence all over the stage should not be ignored, "
            "a single read kills 💀 you at *40%* 👀 , 🔥 🔥 🔥 puts you at "
            "risk ⚠ when trying to gimp him, and his 🔥 ⚔ is completely "
            "lagless and can OHKO you 👌 👌 👌 . "
            "He may be combo food 🍖 , but he wants that 💢 rage 💢 , "
            "so he can kill you at *10%* with a read 📖 💥 💥 💥 👀 . "
            "Roy is the real top 5 sword character, unlike that worthless "
            "clone {marth}  😕 😩 😫\n\n"
            "**🔥 ROY'S 🔥 OUR 🔥 BOY 🔥**".format(marth=marf))
        pasta = random.choice(roypasta)
        await self.send_message(msg.channel, pasta)

    @command("^oh no|uair$", access=-1, name='oh no',
             doc_brief="`oh no`: Pastes a random pasta")
    async def oh_no(self, msg, arguments):
        oh_nos = {}
        oh_nos['cloud'] = (
            "ー仁二二二ア\n"
            "¯\_(ツ)_/¯\n"
            "OH NO You've been Up-aired by the top-tier Anime Man!\n"
            "Repost this message in 10 chats or be up-aired again!\n"
        )
        oh_nos['diddy'] = (
            "You have been visited by the 🐒 **Mankey of FREE COMBOS** 🐒\n"
            "🍌 Bananas 🍌 and downthrows will come to you, "
            "but ONLY if you post \n"
            "**ヽ༼ຈل͜ຈ༽ﾉ HOO HAH ヽ༼ຈل͜ຈ༽ﾉ**\n"
            "in 10 chats!\n"
            "🙈 🙉 🙊"
        )
        pasta = random.choice(list(oh_nos.values()))
        await self.send_message(msg.channel, pasta)

    @command("^chillinrap *([123])?$", access=100, name='chillinrap',
             doc_brief='`chillinrap [verse number]`: "What\'s the set count '
             'going to be?"',
             doc_detail='"What\'s the set count going to be?"\n'
             '"Against who? mew2king?"\n'
             '"Chillin."\n'
             '"*Chillin*" 😂 😂 😂\n'
             '"What\'s the set count going to be?"\n'
             '"Alright, well, GIMR wants to know—"\n'
             '"What\'s the set count?\n"'
             '"—GIMR wants to know what\'s the set count going to be against '
             'Chillin. **The people** wanna know."\n'
             '"..."\n"..."\n'
             '"...I don\'t need to *say* anything; everyone knows what I\'m '
             'going to say.\n'
             '<:5_0:252694352315285504> ***AND IT\'S GONNA BE FIVE-OH*** '
             '<:5_0:252694352315285504>\n'
             'That- that\'s how it\'s gonna be."')
    async def chillinrap(self, msg, arguments):
        mb = self.core.emoji.emoji(msg.server, ['my_b'])
        leff = self.core.emoji.emoji(msg.server, ['5_0'])
        shine = self.core.emoji.emoji(msg.server, ['shine'])
        leff_fox = self.core.emoji.emoji(msg.server, ['leffen_fox'])
        nlt = self.core.emoji.emoji(msg.server, ['notlikethis'])
        salt = self.core.emoji.emoji(msg.server, ['pjsalt'])
        verse = []
        verse.append("{my_b} I'm not lawful, make "
                     "{leff5_0} this pussy stop talking 🙊\n"
                     "You're not one of the gods 👼❌, you're one of the "
                     "god-awfuls 👺✔\n"
                     "We all got gimped {shine} 😫 when "
                     "looking at your Fox {leffen_fox}\n"
                     "Bitch, stick to 🚮 Smash 4 🚮  and losing by four stocks "
                     "🦊 🦊 🦊 🦊\n"
                     "😤 Not a fan of your style\n {leff5_0} "
                     "You ain't standing your ground\n"
                     "Get wins 🏆👌 while kicking a man when he's down 👢😩\n"
                     "Like, {leff5_0} \"I beat Mango "
                     "{shine}🍊, I'm the favorite if he "
                     "chokes! {notlikethis}\n"
                     "\"As far as Armada 🍑 goes, I'll just wait 🤞 'til he's "
                     "a host.😏\"\n"
                     "Ain't no telling how foolish 😛 you'll be lookin' 👀\n"
                     "Evidence.zip 📁📂 can't contain the ass whooping 👊 \n🍑"
                     "Right when we realize the 💰 money match 💯💸 is over\n"
                     "That'll be your cue to throw your controller "
                     "😡 👋 🎮 ⬇".format(
                        leff5_0=leff,
                        my_b=mb,
                        shine=shine,
                        leffen_fox=leff_fox,
                        notlikethis=nlt))

        verse.append("Expose {leff5_0} you as a fraud\n"
                     "Yeah I'll be blowing you up 💥\n"
                     "Who said you were a god? 👼❓\n"
                     "I know it wasn't Plup 🚀🦊"
                     "{notlikethis}👌\n"
                     "Been here 🔟 ten 🗓 years and you know "
                     "{my_b} I'm showing up\n"
                     "For a man of many words {leff5_0}, "
                     "I think you've said enough 🙊\n"
                     "But, the only way to make you hush\n"
                     "First I'll body bag your Fox 🦊{shine}"
                     "💀 then .zip 📁 it shut\n"
                     "'Imma put you in your place\n"
                     "Kid 👦, you a disgrace 👺\n"
                     "Get killed quick like that missile hit you in the face "
                     "🚀{leffen_fox}💀\n"
                     "After all of this {leff5_0} you'll be "
                     "watching 👀 your mouth 🙊\n"
                     "Ain't no telling who'll be calling you out\n"
                     "Salty {pjsalt} Suite 🎮 goes down\n"
                     "You better come correct ✔\n"
                     "Until you win a major 🏆 show your elders 👴 some "
                     "respect 🤝".format(
                        leff5_0=leff,
                        my_b=mb,
                        pjsalt=salt,
                        shine=shine,
                        leffen_fox=leff_fox,
                        notlikethis=nlt))

        verse.append("💌 P.S. Leffen, I ain't done yet "
                     "{my_b}\n"
                     "I'm the underdog 🐶 so place your bets 💸\n"
                     "Whoever want to see {leff5_0} Leffen "
                     "looking dumb 😜\n"
                     "Throw your money 👋💯💸 on the line cause "
                     "{my_b} I'm making some 💰👌\n"
                     "Gotta say bro 🤔 you're looking awfully weak 😩\n"
                     "Wait and see 👀 what happens in the Salty "
                     "{pjsalt} Suite 🎮\n"
                     "Vanilla Fox 🍦🦊 don't suit you so go find another 🌈🦊\n"
                     "Teach you a lesson and take back my color "
                     "{leff5_0}{my_b}".format(
                        leff5_0=leff,
                        my_b=mb,
                        pjsalt=salt,
                        shine=shine))

        if (arguments[0] is not None):
            reply = verse[int(arguments[0])-1]
            self.logger.info(reply)
            await self.send_message(msg.channel, reply)
        else:
            for i in range(0, len(verse)):
                self.logger.info(verse[i])
                await self.send_message(msg.channel, verse[i])

    @command("^nipples|knuckles$", access=100, name="nipples",
             doc_brief="`knuckles`: oh. my mistake")
    async def nipples(self, msg, arguments):
        nipples = self.core.emoji.emoji(
            msg.server, ['knuckles', 'nipples_the_enchilada']
        )
        nipplespasta = ("here i come, rougher than {nip}, the best of them, "
                        "tougher than {nip}\n"
                        "you can call me {nip}, unlike {nip}, i dont chuckle, "
                        "id rather flex my {nip}\n"
                        "im hard as {nip}, it aint hard to chuckle, i break "
                        "em down whether they {nip} or {nip}\n"
                        "unlike {nip}, im independent since my first chuckle, "
                        "first {nip}, feel the {nip} than the {nip} "
                        "chuckle").format(nip=nipples)
        await self.send_message(msg.channel, nipplespasta)

    @command("^YEAH[_ ]WEED", access=100)
    async def yeah_weed(self, msg, arguments):
        w_char = """
<:YEAH_WEED:242233070051131392>                                       <:YEAH_WEED:242233070051131392>
<:YEAH_WEED:242233070051131392>             <:YEAH_WEED:242233070051131392>             <:YEAH_WEED:242233070051131392>
<:YEAH_WEED:242233070051131392>             <:YEAH_WEED:242233070051131392>             <:YEAH_WEED:242233070051131392>
<:YEAH_WEED:242233070051131392>             <:YEAH_WEED:242233070051131392>             <:YEAH_WEED:242233070051131392>
<:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392>
"""
        e_char = """
<:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392>
<:YEAH_WEED:242233070051131392>
<:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392>
<:YEAH_WEED:242233070051131392>
<:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392>
"""
        d_char = """
<:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392>
<:YEAH_WEED:242233070051131392>                                       <:YEAH_WEED:242233070051131392>
<:YEAH_WEED:242233070051131392>                                       <:YEAH_WEED:242233070051131392>
<:YEAH_WEED:242233070051131392>                                       <:YEAH_WEED:242233070051131392>
<:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392><:YEAH_WEED:242233070051131392>
"""
        await self.delete_message(msg)
        await self.send_message(msg.channel, w_char)
        await self.send_message(msg.channel, e_char)
        await self.send_message(msg.channel, e_char)
        await self.send_message(msg.channel, d_char)
