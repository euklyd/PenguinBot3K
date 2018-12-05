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

import asyncio
import discord
import json
import logging
import random

from datetime import datetime

logger = logging.getLogger(__name__)

image_path = "resources/images/{}"
macro_path = "resources/macro/{}"


class Macro(Plugin):
    async def activate(self):
        pass

    emojis = (
        """
        0x1F600...0x1F64F, // Emoticons
        0x1F300...0x1F5FF, // Misc Symbols and Pictographs
        0x1F680...0x1F6FF, // Transport and Map
        0x2600...0x26FF,   // Misc symbols
        0x2700...0x27BF,   // Dingbats
        0xFE00...0xFE0F    // Variation Selectors
        """
        "\u2600-\u26FF"
        "\u2700-\u27BF"
        "\U0001F1E6-\U0001F1FF"
        "\U0001F300-\U0001F5FF"
        "\U0001F600-\U0001F64F"
        "\U0001F680-\U0001F6FF"
    )

    @command("^emojify ([{}]|(?:<:[A-Za-z0-9_]*:\d*>)) (.*)".format(emojis),
             access=-1, name='emojify',
             doc_brief="`emojify <emoji> <sentence>`: replace all spaces in "
             "`<sentence>` with `<emoji>`")
    async def emojify(self, msg, arguments):
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

    @command("^BScop (.*)$", name='bullshit police')
    async def bullshit_police(self, msg, arguments):
        cops = self.core.emoji.any_emoji(['blobpatrol'])
        reply = (
            "{cops} LOOK {cops} OUT {cops} {name} {cops} IT'S {cops} THE "
            "{cops} BULLSHIT {cops} POLICE {cops}"
        ).format(cops=cops, name=arguments[0])
        await self.delete_message(msg)
        await self.send_message(msg.channel, reply)

    @command("^cloud$", access=50, name='cloud',
             doc_brief="`cloud`: The dankest of ☁ memes")
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

    @command("^(?:waddle|ddd|THE KING)$", access=50, name='waddle',
             doc_brief="`waddle`: The dankest of 🐧 Penguin 🐧 memes")
    async def waddle(self, msg, arguments):
        gordo = self.core.emoji.any_emoji(['gordo'])
        dddpasta = ("🐧 **King Dedede** 🐧 is definitely **top tier**. "
                    "The king's got it all: disjoint ⚔, power 💪, recovery ✈, "
                    "and damaging throw combos 💥. He is the hardest character "
                    "in the game to kill vertically ⬆💀, and with the safest "
                    "and strongest ways to kill 💀 being traditionally "
                    "⬆vertical⬆, that's huge ⛰. His presence at the ledge is "
                    "not to be ignored, as with clever {gordo} setups, he can "
                    "cover most if not all ledge options with a potentially "
                    "deadly hitbox 💀. He might be combo food 🍖, but he wants "
                    "all that 💢 rage 💢 so he can kill with his safe and "
                    "powerful back air 🔨🐻 even earlier than usual. "
                    "**An obvious member of 🐧 top tier🐧.**\n"
                    "🐧 **THE 🐧 KING 🐧 IS 🐧 TOP 🐧 TIER** 🐧".format(
                        gordo=gordo
                    ))
        await self.send_message(msg.channel, dddpasta)

    @command("^(?:plumber|cancer|<:mario:[0-9]*>|mario)$", access=100,
             name='plumber', doc_brief="`plumber`: The dankest of "
             "🚽 Plumber 🚽 memes")
    async def plumber(self, msg, arguments):
        mario = self.core.emoji.any_emoji(['mario'])
        m2 = self.core.emoji.any_emoji(
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

    @command("^(?:md|MD|doc|doctor|💊)$", access=100, name='doctor',
             doc_brief="`doctor`: The dankest of 💊 Doctor 💊 memes")
    async def doctor(self, msg, arguments):
        mario = self.core.emoji.any_emoji(['mario'])
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

    @command("^(?:birb|falco)$", access=100, name='birb',
             doc_brief="`birb`: The dankest of birb memes")
    async def birb(self, msg, arguments):
        hoohah = self.core.emoji.any_emoji(['hoo_hah', 'HooHah', 'hoohah'])
        birbpasta = (
            "Falco's 🐦 only better than 5 🖐 characters (8 with miis ✊ ⚔ 🔫 ) "
            "❔ 😐   😮 Clearly they haven't seen 👀 me 🤳 beat random people 👤 "
            "in wifi crew battles 💻 👥 😆 What a joke 🃏 😂 , can't wait for "
            "ZeRo 0⃣ {diddy} to call 📞 them out 📤 🤣".format(
                diddy=hoohah
            ))
        await self.send_message(msg.channel, birbpasta)

    @command("^(?:penguin|\U0001F427)$", access=-1, name='penguin',
             doc_brief="`penguin`: Embeds the Skype `(penguin)` emoji")
    async def penguin(self, msg, arguments):
        penguin_url = "https://i.imgur.com/MGNa91r.gif"
        penguin_url = "https://cdn.discordapp.com/attachments/342186707028017152/360499286863249421/skype_penguin_transparent.gif"
        user = msg.server.get_member(self.core.user.id)
        em = discord.Embed(color=user.color)
        em.set_thumbnail(url=penguin_url)
        em.set_footer(
            text="",
            icon_url=user.avatar_url
        )
        await self.send_message(msg.channel, embed=em)

    @command("^(?:cat|\U0001F408|\:3)$", access=-1, name='cat',
             doc_brief="`cat`: Embeds the Skype `(cat)` emoji")
    async def cat(self, msg, arguments):
        cat_url = "http://i.imgur.com/kJYNv51.gif"
        user = msg.server.get_member(self.core.user.id)
        em = discord.Embed(color=user.color)
        em.set_thumbnail(url=cat_url)
        em.set_footer(
            text="",
            icon_url=user.avatar_url
        )
        await self.send_message(msg.channel, embed=em)

    @command("^(?:thinking|🤔)$", access=-1, name='thinking',
             doc_brief="`thinking`: Embeds the `:thinking:` emoji's ultimate "
             "form")
    async def thinking(self, msg, arguments):
        thinking_url = "http://i.imgur.com/oHPYovk.gif"
        user = msg.server.get_member(self.core.user.id)
        em = discord.Embed(color=user.color)
        em.set_thumbnail(url=thinking_url)
        em.set_footer(
            text="",
            icon_url=user.avatar_url
        )
        await self.send_message(msg.channel, embed=em)

    @command("^(?:[Oo]laf|[Ii]ntegrity)$", access=-1, name='integrity',
             doc_detail="`integrity`: Embeds the face of Integrity irl ⛄")
    async def integrity(self, msg, arguments):
        olaf_url = "http://i.imgur.com/791NLN5.png"
        user = msg.server.get_member(self.core.user.id)
        em = discord.Embed(color=user.color)
        em.set_thumbnail(url=olaf_url)
        await self.send_message(msg.channel, embed=em)

    @command("^(?:[Ss]akurai|jank|game blows)$", access=-1, name='sakurai',
             doc_detail="`sakurai`: 👍")
    async def sakurai(self, msg, arguments):
        ayy = ["http://i.imgur.com/rbpQb3M.gif",
               "http://i.imgur.com/ahTXT2T.gif"]
        await self.send_message(msg.channel, random.choice(ayy))

    @command("^( )?(?:boy|[Rr]oy|🔥🔥🔥|ph1r3)$", access=50, name='ph1r3',
             doc_brief="`ph1r3`: The dankest of 🔥 ph1r3 🔥 memes",
             doc_detail="` roy`: The one true 🔥 ph1r3 🔥 meme")
    async def ph1r3(self, msg, arguments):
        marf = self.core.emoji.any_emoji(['ppmd_marth', 'MarthSip'])
        roypasta = [
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
            "**🔥 ROY'S 🔥 ACTUAL 🔥 SHIT 🔥**".format(marth=marf),

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
            "**🔥 ROY'S 🔥 OUR 🔥 BOY 🔥**".format(marth=marf)
        ]
        if (arguments[0] == " "):
            pasta = roypasta[0]
        elif (msg.author.id in ["190933659887337472"]):
            pasta = roypasta[0]
            pasta += random.choice(
                ["", "\n(A great big steaming, wet, smelly 💩 shit 💩)"])
        else:
            pasta = random.choice(roypasta)
        await self.send_message(msg.channel, pasta)

    # @command("^ (?:boy|[Rr]oy|🔥🔥🔥|ph1r3)$", access=99, name='roy',
    #          doc_detail="` roy`: The one true 🔥 ph1r3 🔥 meme")
    # async def roy(self, msg, arguments):
    #     marf = self.core.emoji.emoji_str(msg.server, ['ppmd_marth', 'MarthSip'])
    #     roypasta = (
    #         "🔥 Roy 🔥 is definitely low tier.  The boy got nothing:  "
    #         "No Speed 🏃 , Shitty KO Power 💥 , 0% off throws, "
    #         "and a pencil  ✏ disjoint 👌 🗡 .  Let's not forget that in his "
    #         "own respective game 😳 he's a total beta nerd 🤓 . "
    #         "His presence all over the stage should not be ignored, "
    #         "a single read 📖 gets you nothing 💀 at 40% 👀 , 🔥 🔥 🔥 you're "
    #         "not at risk ⚠ 💤 when trying to gimp him, and his 🔥 ⚔ is "
    #         "completely laggy 🐌 and can OHKO you at 304% 👌 👌 👌 😂 . "
    #         "He may be combo food 🍖 , but he wants that DING DONG 🐒 💥 💀 , "
    #         "so he can die you at 60% from a single grab 💥 💥 💥 👀 . "
    #         "Roy is the bottom top 5 sword character, unlike that amazing "
    #         "original character ⚔ Marth {marth} 😕 😩 😫 .\n\n"
    #         "**🔥 ROY'S 🔥 ACTUAL 🔥 SHIT 🔥**".format(marth=marf))
    #     await self.send_message(msg.channel, roypasta)

    # TODO: finish
    @command("^(?:[Zz]ard|[Cc]harizard|[Ll]izardon|🔥[🐲🐉])$", access=99,
             name='charizard',
             doc_detail="`charizard`: The dankest of 🔥🐲 memes.")
    async def charizard(self, msg, arguments):
        zardpasta = [
            ":fire::dragon_face: **Charizard** (リザードン, **Lizardon** :lizard:) is "
            "a playable character in {shine} *Super Smash Bros. 4* :wastebasket:. "
            ":fire::dragon_face: **Charizard** is a fucking :muscle: beast :lion:. "
            "He does lots of :camel: neck :bicyclist: exercises :lifter:. "
            "Also, never skip :muscle: tail :dragon: day :muscle:.",

            ":fire::dragon_face: Charizard is :medal: top 15 :trophy:. "
            "He's a good character. He's {salt} underrated. :sob:"
            "Everyone thinks he's 💤 bad, but he's actually not :fire::muscle:. "
            "He's top 15. MKLeo said so. He has it all: speed 🏃, KO power 💥:muscle:, 💯% off throws, "
            "and disjoint 👌⚔. Let's not forget :confused: that in his own respective "
            "series, he learns Sunny Day :sun_with_face: and Solar Beam :mag::flashlight: and has two :fire::dragon: Mega "
            "Evolutions :muscle::dragon: that utterly thrash :skull: the majority of the OU tier :medal:👌. "
            "His presence all over the stage should not be ignored; a single "
            "read can kill :skull: at 20%, puts you at risk ⚠ when you try to gimp him, "
            "and his back air 🐻 is completely lagless and can OHKO you 👌 👌 👌. "
            "He may be combo food 🍖, but he wants that 💢R💢A💢G💢E💢 so he can kill "
            "you at 0% with a read 📖 💥 💥 💥 👀. As the Patron Saint of Genwunners, "
            "Charizard is the second-most powerful character on the roster, "
            "and playing as him against a Unovabortion results in an "
            "automatic victory out of hatred and despair, especially since "
            "the Zard got in over that Zoroark loser due to his clear "
            "superiority. Charizard is so badass that Alain was able to "
            "defeat Ash Ketchum and his brand spanking new superpowered "
            "Greninja just by owning a Mega Charizard X, causing millions "
            "of grown men who still watch a children's cartoon to unleash "
            "their rage.",

            "The only character that Charizard loses against on principle is "
            "God-Emperor of the Universe Captain Falcon, and even that's "
            "debatable as most Falcon vs. Charizard matches end with our "
            "manly heroic Captain jumping on the dragon's back and soaring "
            "through the skies to bring GREAT BURNING JUSTICE to the galaxy. "
            "Charizard is the real top 15 character.",

            "While the Smash Back Room initially committed the heretical "
            "crime of listing Charizard as a bottom-tier character "
            "(TWICE IN A ROW), they finally started learning the error of "
            "their ways and moved him to the upper low tier. Of course, "
            "they still fail to recognize the power of the ultimate badass "
            "of Pokémon, but hey, it's a start."
        ]

    @command("^(?:thwomp|[Aa]rdan|[Dd]oga+)$", access=99, name='thwomp',
             doc_detail="`thwomp`: The dankest of "
             "<:thwomp:249488838689423360> memes.")
    async def thwomp(self, msg, arguments):
        thwomp = self.core.emoji.any_emoji(['thwomp'])
        return_of_ganon = self.core.emoji.any_emoji(
            ['return_of_ganon', 'ganon'])
        ppmd_kreygasm = self.core.emoji.any_emoji(
            ['ppmd_kreygasm', 'ppmdKreygasm'])
        expand = self.core.emoji.any_emoji(['expand_dong', 'expand'])
        dong = self.core.emoji.any_emoji(['dong'])
        cunedd = self.core.emoji.any_emoji(['cunedd'])
        ok_marth = self.core.emoji.any_emoji(['ok_marth'])
        blobthink = self.core.emoji.any_emoji(['blobthinking', 'blobthink'])
        cain = self.core.emoji.any_emoji(
            ['cain', 'fe1_cain', 'abel', 'fe1_abel'])
        extra_thicc = self.core.emoji.any_emoji(['EXTRA_THICC'])
        dogaaaa = self.core.emoji.any_emoji(
            ['dogaaaa', 'fe1_dogaaaa', 'doga', 'fe1_doga'])
        shine = self.core.emoji.any_emoji(['shine'])
        sanic = self.core.emoji.any_emoji(['sanic'])
        ardan = self.core.emoji.any_emoji(['ardan', 'fe4_ardan'])
        bitf_ddd = self.core.emoji.any_emoji(['bitf_ddd'])
        leff5_0 = self.core.emoji.any_emoji(['5_0'])
        arvis = self.core.emoji.any_emoji(
            ['grillmaster', 'fe4_arvis', 'arvis'])
        savage_blow = self.core.emoji.any_emoji(['savage_blow'])
        thwomppasta = (
            "Ask ❓ yourself, are you man 💪 enough, thwomp {thwomp} enough, "
            "insane {ganon} enough to play this game with two of the greatest "
            "{kreygasm} units in all of Fire Emblem?  If you answered yes, "
            "you're a big {expand}, fat {dong} liar {cunedd} !\n"
            "But that's okay {ok_marth}, because Intelligent {think} Systems "
            "is bringing back generals into your home 🏚 for a special Dynasty"
            "Warriors clone {cain} !  First, it's survival of the fittest "
            "{thicc} in our selection process.\n"
            "Be there as Doga {doga} - DOGAAAA {doga} - unleashes his fury 💥 "
            "on the rest of the cast 🏥. Doga has gone undefeated in 500 "
            "straight matches in the animal shelter 😿. But if their "
            "restraining order 📋 doesn't do it for you, then the power 💪 of "
            "pursuit {shine} will!\n"
            "Taste the adrenaline {sanic} as the cast faces off against our "
            "Hero Sword general, the legendary Ardan {ardan} ! Ardan {ardan}, "
            "Ardaaaan {ardan}. No living creature {ddd} is a match for this "
            "machine {leff5_0}. Watch six tons of general hunt for his prey "
            "{arvis}.  There's no consolation "
            "prize 🥈 , cause this bad boy's programmed to show no mercy "
            "{savage_blow}.\n"
            "So, what are you waiting for ❓ ❓ ❓ ?  Preorder now to bring "
            "Doga {doga} and Ardan {ardan} into your living room 🏚 , "
            "but put away the fine china 🍽 ! "
            "You can only find these generals in Fire Emblem Warriors, "
            "so call your local Amazon 🌴 now!".format(
                thwomp=thwomp,
                ganon=return_of_ganon,
                kreygasm=ppmd_kreygasm,
                expand=expand,
                dong=dong,
                cunedd=cunedd,
                ok_marth=ok_marth,
                think=blobthink,
                cain=cain,
                thicc=extra_thicc,
                doga=dogaaaa,
                shine=shine,
                sanic=sanic,
                ardan=ardan,
                ddd=bitf_ddd,
                leff5_0=leff5_0,
                savage_blow=savage_blow,
                arvis=arvis
            )
        )
        await self.send_message(msg.channel, thwomppasta)

    @command("^(?:secret|daddy'?s|cummies) forest(?: invite)?$", access=-1,
             name='secret forest',
             doc_brief="`secret forest invite`: The invite link for the "
             "💦Secret Forest💦 Discord server.")
    async def secretforest(self, msg, arguments):
        daddy = (
            "Hello💦 💦 💦\n"
            "I'm a  😻 DADDY 😻  from SF, I want to invite you to the 💦 "
            "Cummies💦😩Forest😩.\n"
            "https://discord.gg/DADDYFOREST\n\n"
            "A solution for the bad implemented and shitty "
            "Slutty Forest Discord Server.\n"
            "We have a lot of 👅 features 👅.\n"
            "- 💦Daddy💦 bot\n"
            "- 😻 DADDY 😻 Channel\n"
            "- Awesome 🍆NUT🍆 and 💦CUMMIES💦 Channel 😩\n"
            "- 💔 No Daddies 💔  from the 😾 SF Staff 😾\n"
            "- Bots that ""help"" 👀 👀 👀 😍\n"
            "- 😻And a lot of daddies😻.😩\n"
        )
        await self.send_message(msg.channel, daddy)

    @command("^(?:oh no|up?air) ?([A-Za-z]+)?$", access=-1, name='oh no',
             doc_brief="`oh no`: Pastes a random 'oh no' pasta")
    async def oh_no(self, msg, arguments):
        oh_nos = {}
        oh_nos['cloud'] = (
            "ー仁二二二ア\n"
            "¯\_(ツ)_/¯\n"
            "OH NO You've been Up-aired by the top-tier Anime Man!\n"
            "Repost this message in 10 chats or be up-aired again!\n"
            "http://i.imgur.com/KCrDmIsm.jpg"
        )
        oh_nos['diddy'] = (
            "You have been visited by the 🐒 **Mankey of FREE COMBOS** 🐒\n"
            "🍌 Bananas 🍌 and ⬆upthrows⬆ will come to you, "
            "but ONLY if you post \n"
            "**ヽ༼ຈل͜ຈ༽ﾉ HOO HAH ヽ༼ຈل͜ຈ༽ﾉ**\n"
            "in 10 chats!\n"
            "🙈 🙉 🙊"
        )
        if (len(arguments) == 1 and arguments[0] in oh_nos):
            pasta = oh_nos[arguments[0]]
        else:
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
        mb = self.core.emoji.any_emoji(['my_b'])
        leff = self.core.emoji.any_emoji(['5_0'])
        shine = self.core.emoji.any_emoji(['shine'])
        leffox = self.core.emoji.any_emoji(['leffen_fox', 'fox_facepalm'])
        nlt = self.core.emoji.any_emoji(['notlikethis'])
        salt = self.core.emoji.any_emoji(['pjsalt'])
        verse = []
        verse.append("{my_b} I'm not lawful, make "
                     "{leff5_0} this pussy stop talking 🙊\n"
                     "You're not one of the gods 👼❌, you're one of the "
                     "god-awfuls 👺✔\n"
                     "We all got gimped {shine} 😫 when "
                     "looking at your Fox {leffox}\n"
                     "Bitch, stick to 🚮 Smash 4 🚮  and losing by four stocks "
                     "🦊 🦊 🦊 🦊\n"
                     "😤 Not a fan of your style\n {leff5_0} "
                     "You ain't standing your ground\n"
                     "Get wins 🏆👌 while kicking a man when he's down 👢😩\n"
                     "Like, {leff5_0} \"I beat Mango {shine}🍊, "
                     "I'm the favorite if he chokes! {nlt}\n"
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
                        leffox=leffox,
                        nlt=nlt))

        verse.append("Expose {leff5_0} you as a fraud\n"
                     "Yeah I'll be blowing you up 💥\n"
                     "Who said you were a god? 👼❓\n"
                     "I know it wasn't Plup 🚀🦊 {nlt}👌\n"
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
                     "🚀{leffox}💀\n"
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
                        leffox=leffox,
                        nlt=nlt))

        verse.append("💌 P.S. Leffen, I ain't done yet {my_b}\n"
                     "I'm the underdog 🐶 so place your bets 💸\n"
                     "Whoever want to see {leff5_0} Leffen looking dumb 😜\n"
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

    @command("^(?:nipples|knuckles)$", access=100, name='nipples',
             doc_brief="`knuckles`: oh. my mistake")
    async def nipples(self, msg, arguments):
        nipples = self.core.emoji.any_emoji(
            ['knuckles', 'nipples_the_enchilada']
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

    @command("^(?:magic|[Ii] prefer the magic)$", access=-1, name='magic',
             doc_detail="`magic`: Mee6 breaks records. Nadeko breaks records. "
             "PenguinBot3K breaks records. PenguinBot3.5K breaks the rules. "
             "Personally, I prefer the magic.")
    async def magic(self, msg, arguments):
        with open(macro_path.format("magic.json"), 'r') as magicfile:
            magic = json.load(magicfile)
            await self.send_message(
                msg.channel,
                random.choice(list(magic.values()))
            )

    @command("^THE PUNCH ?(.+)?$",
             access=50, name='the punch',
             doc_brief="`THE PUNCH`: I was just wondering why Ganondorf is "
             "in the very middle of the tiers.",
             doc_detail="I was just wondering why Ganondorf is in the very "
             "middle of the tiers. Before I get into what I mean, allow me to "
             "first put out there that I have been playing for years, "
             "and I have watched MANY videos of the tournament masters.")
    async def THE_PUNCH(self, msg, arguments):
        with open(macro_path.format("the_punch.json"), 'r') as punchfile:
            punch = json.load(punchfile)
            if (arguments[0] in punch['dict']):
                await self.send_message(
                    msg.channel,
                    punch['dict'][arguments[0]]
                )
            else:
                await self.send_message(
                    msg.channel,
                    ("Section keys are: `{keys}`\n"
                     "Use with `{trigger}THE PUNCH <key>`").format(
                        keys="`, `".join(punch['dict']),
                        trigger=self.core.default_trigger)
                )
        ganon = self.core.emoji.any_emoji(['return_of_ganon'])
        if (ganon != "`:return_of_ganon:`"):
            await self.send_message(msg.channel, ganon)

    @command("^pasta ?(.*)$", access=-1, name='pasta',
             doc_brief="`pasta <pasta name>`: The associatedd "
             "pasta for `<pasta name>`. Use without arguments to list "
             "available pastas.")
    async def pasta(self, msg, arguments):
        pasta = arguments[0].lower()
        with open(macro_path.format("pastas.json"), 'r') as pastafile:
            pastas = json.load(pastafile)
            if msg.server.id not in pastas:
                reply = "This server has no pastas..."
            elif (pasta == "" or pasta == "--list" or pasta == "--help"):
                reply = "**Available pastas:** "
                for k in pastas[msg.server.id]:
                    reply += "`{}`, ".format(k)
                reply = reply[0:-2]
            elif (pasta in pastas[msg.server.id]):
                reply = pastas[msg.server.id][pasta]
            else:
                reply = "No such pasta."
            await self.send_message(
                msg.channel,
                reply
            )

    @command('^makepasta name:"([^"]*)" text:"([^"]*)"$', access=500,
             name='makepasta',
             doc_brief='`makepasta name:"<name>" text:"<pastatext>"`: Creates '
             'a new pasta for use with the `pasta` command.',
             doc_detail='`makepasta name:"<name>" text:"<pastatext>"`: '
             'Creates a new pasta, accessible by using the '
             '`pasta <name>` command, which I will respond to with <text>.')
    async def makepasta(self, msg, arguments):
        name = arguments[0].lower()
        pastas = {}
        with open(macro_path.format("pastas.json"), 'r') as pastafile:
            pastas = json.load(pastafile)
        if msg.server.id not in pastas:
            pastas[msg.server.id] = {}
        if (name in pastas[msg.server.id]):
            reply = "**ERR:** Pasta `{}` already exists.".format(name)
        elif (name[0:2] == "--"):
            reply = "**ERR:** `--` is a reserved sequence."
        else:
            try:
                pastas[msg.server.id][name] = arguments[1]
                with open(macro_path.format("pastas.json"), 'w') as pastafile:
                    json.dump(pastas, pastafile, indent=2)
                reply = "Successfully added new pasta `{}`.".format(name)
            except:
                reply = "ERR: Something went wrong."
        await self.send_message(msg.channel, reply)

    @command("^scizzy$", access=-1, name='scizzy',
             doc_brief="`scizzy`: random scizor quote")
    async def scizzy(self, msg, arguments):
        with open(macro_path.format("scizzy.json"), 'r') as quotefile:
            quotes = json.load(quotefile)
        await self.send_message(
            msg.channel,
            random.choice(quotes)
        )

    @command("^submitscizzy (.*)", access=-1, name='scizzy',
             doc_brief="`submitscizzy`: submit a scizor quote for `scizzy`")
    async def submitscizzy(self, msg, arguments):
        # quote = arguments[0]
        quote = msg.content.split("submitscizzy ")[1]
        quotes = []
        try:
            with open(macro_path.format("unchecked_scizzy.json"), 'r') as f:
                quotes = json.load(f)
        except FileNotFoundError:
            quotes = []
        quotes.append({'quote': quote, 'user': msg.author.name})
        with open(macro_path.format("unchecked_scizzy.json"), 'w') as f:
            json.dump(quotes, f, indent=2)
        await self.send_message(
            msg.channel,
            "Thanks for the submission {}".format(
                self.core.emoji.any_emoji(["ScizzyOK"])
            )
        )

    @command("^validatescizzy$", access=1000, name='validatescizzy',
             doc_brief="`validatescizzy`: validate scizzy quotes")
    async def validatescizzy(self, msg, arguments):
        unchecked_quotes = []
        quotes = []
        try:
            with open(macro_path.format("scizzy.json"), 'r') as quotefile:
                quotes = json.load(quotefile)
        except FileNotFoundError:
            quotes = []
        try:
            with open(macro_path.format("unchecked_scizzy.json"), 'r') as f:
                unchecked_quotes = json.load(f)
        except FileNotFoundError:
            await self.send_message(
                msg.channel, "No scizzy quotes to be validated!"
            )
            return
        for q in unchecked_quotes:
            await self.send_message(
                msg.channel,
                "**Submission:**\n\t{}\nFrom: {}".format(q['quote'], q['user'])
            )
            reply = await self.core.wait_for_message(author=msg.author,
                                                     channel=msg.channel)
            if (reply.content.lower() == "y"):
                quote = q['quote']
                quotes.append(quote)
                await self.send_message(msg.channel, "Submission accepted.")
            elif (reply.content.startswith("edit: ")):
                quote = reply.content.split("edit: ")[1]
                quotes.append(quote)
                await self.send_message(msg.channel, "Submission modified.")
            else:
                await self.send_message(msg.channel, "Submission rejected.")
        with open(macro_path.format("scizzy.json"), 'w') as quotefile:
            json.dump(quotes, quotefile, indent=2)
        with open(macro_path.format("unchecked_scizzy.json"), 'w') as f:
            json.dump([], f, indent=2)
        await self.send_message(
            msg.channel,
            "Scizzies saved {}".format(self.core.emoji.any_emoji(["ScizzyOK"]))
        )

    @command("^(?:animes|mangos|animes_and_mangos)(?:\.gif)?$", access=-1,
             name='animes and mangos.gif',
             doc_brief='`animes_and_mangos.gif`: ~silly kids~')
    async def animes_and_mangos(self, msg, arguments):
        filename = image_path.format("animes_and_mangos.gif")
        with open(filename, 'rb') as anime_file:
            sent_file = await self.send_file(
                msg.channel,
                anime_file,
                filename="animes_and_mangos.gif"
            )

    @command("^YEAH[_ ]WEED", access=100)
    async def yeah_weed(self, msg, arguments):
        weed = str(self.core.emoji.any_emoji(['YEAH_WEED', 'yeahweed']))
        blank = str(self.core.emoji.any_emoji(
            ['blankspace', 'blank_space', 'blank']))
        w_char = """
{weed}{blank}{blank}{blank}{weed}
{weed}{blank}{weed}{blank}{weed}
{weed}{blank}{weed}{blank}{weed}
{weed}{blank}{weed}{blank}{weed}
{weed}{weed}{weed}{weed}{weed}
""".format(weed=weed, blank=blank)
        e_char = """
{weed}{weed}{weed}{weed}{weed}
{weed}
{weed}{weed}{weed}{weed}
{weed}
{weed}{weed}{weed}{weed}{weed}
""".format(weed=weed, blank=blank)
        d_char = """
{weed}{weed}{weed}{weed}
{weed}{blank}{blank}{blank}{weed}
{weed}{blank}{blank}{blank}{weed}
{weed}{blank}{blank}{blank}{weed}
{weed}{weed}{weed}{weed}
""".format(weed=weed, blank=blank)
        # superweed = "{w}\n{e}\n{e}\n{d}".format(w=w_char, e=e_char, d=d_char)
        # self.logger.info(superweed)
        await self.delete_message(msg)
        await self.send_message(msg.channel, w_char)
        await self.send_message(msg.channel, e_char)
        await self.send_message(msg.channel, e_char)
        await self.send_message(msg.channel, d_char)
        # await self.send_message(msg.channel, superweed) # too many characters

    @command("what ?(\d+)?$", access=-1, name='what',
             doc_brief="`what`: posts a random mega man sprite quote")
    async def mmquote(self, msg, arguments):
        with open(macro_path.format("megaman_quotes.json"), 'r') as whatfile:
            quotes = json.load(whatfile)
        # default state being random is good
        quote_num = random.randint(0, len(quotes['quotes']) - 1)
        if arguments[0] is not None:
            try:
                # this might go poorly if you force a call here
                quote_num = int(arguments[0])
            except ValueError:
                pass
        if quote_num > len(quotes['quotes']) or quote_num < 0:
            quote = {
                'quote': "what kind of stupid dumb idiot user requests a quote that doesn't exist",
                'name': 'mega man'
            }
        else:
            quote = quotes['quotes'][quote_num]
        icon_url = quotes['icons'][quote['name']]
        if type(arguments[0]) is str:
            if arguments[0] in quotes['custom']:
                # spooky override ~owo~
                quote = quotes['custom'][arguments[0]]
                icon_url = quotes['icons'][quotes['custom'][arguments[0]]['icon']]
                quote_num = arguments[0]
            elif arguments[0].lower() in quotes['custom']:
                # spooky override ~owo~
                quote = quotes['custom'][arguments[0]]
                icon_url = quotes['icons'][quotes['custom'][arguments[0]]['icon']]
                quote_num = arguments[0]
        em = discord.Embed(
            title="Megaman Sprite Game quotes",
            color=msg.server.get_member(self.core.user.id).color,
            url="http://megamanspritecomic.tumblr.com/post/65735240451/megaman-sprite-game-released-on-october-31st",
            description=quote['quote'],
            timestamp=datetime.utcfromtimestamp(1351682400)
        )
        em.set_thumbnail(url=icon_url)
        em.set_author(
            name=quote['name'],
            url="http://megamanspritecomic.tumblr.com/",
            icon_url=icon_url
        )
        em.set_footer(
            text="Quote #{}".format(quote_num),
            icon_url="https://66.media.tumblr.com/avatar_0d7144cecd81_128.pnj"
        )
        await self.send_message(msg.channel, embed=em)

    @command("what ?([A-Za-z ]+)?$", access=-1, name='what custom')
    async def mmquote_custom(self, msg, arguments):
        await self.mmquote(msg, arguments)
