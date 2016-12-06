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

logger = logging.getLogger(__name__)


class Macro(Plugin):
    async def activate(self):
        pass

    # @command("^emojify ([\u263a-\U0001f645]|(?:<:.*:\d*>)) (.*)", access=-1)
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
    @command("^emojify -f \"(.*|(?:<:.*:\d*>)*)\" (.*)", access=-1,
             name='emojify',
             doc_detail="`emojify -f \"<anything>\" <sentence>`: "
             "Like `emojify`, but instead of inserting an emoji, "
             "inserts `<anything>`")
    async def emojify_full(self, msg, arguments):
        self.logger.debug(arguments)
        emoji = arguments[0]
        reply = arguments[1].replace(' ', ' {} '.format(emoji))
        reply = "<@!{}>: {}".format(msg.author.id, reply)
        self.logger.info(reply)
        await self.delete_message(msg)
        await self.send_message(msg.channel, reply)

    @command("^emojify -w \"(.*|(?:<:.*:\d*>))\" (.*)", access=50,
             name='emojify',
             doc_detail="`emojify -w \"<anything>\" <sentence>`: as standard "
             "`emojify -f`, but sends output to the user in a DM.")
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

    @command("^waddle$", access=100, name='waddle',
             doc_brief="`waddle`: Prints out the dankest of \U0001F427 "
             "Penguin \U0001F427 memes")
    async def waddle(self, msg, arguments):
        dddcopypasta = "\U0001F427 **King Dedede** \U0001F427 is definitely **top tier**. The king's got it all: disjoint \U00002694, power \U0001F4AA, recovery \U00002708, and damaging throw combos \U0001F4A5. He is the hardest character in the game to kill vertically \U0001F480, and with the safest and strongest ways to kill \U0001F480 being traditionally vertical, that's huge \U000026F0. His presence at the ledge is not to be ignored, as with clever Gordo setups, he can cover most if not all ledge options with a potentially deadly hitbox \U0001F480. He might be combo food \U0001F356, but he wants all that \U0001F4A2 rage \U0001F4A2 so he can kill with his safe and powerful back air \U0001F528 even earlier than usual. **An obvious member of \U0001F427 top tier\U0001F427.**"  # noqa E501
        kingistoptier = "\U0001F427 **THE \U0001F427 KING \U0001F427 IS \U0001F427 TOP \U0001F427 TIER** \U0001F427"  # noqa E501
        await self.send_message(msg.channel, "{}\n{}".format(dddcopypasta, kingistoptier))

    @command("^plumber|cancer|<:mario:[0-9]*>$", access=100, name='plumber',
             doc_brief="`plumber`: Prints out the dankest of 🚽 Plumber 🚽 memes")
    async def plumber(self, msg, arguments):
        mariocopypasta = "<:mario:234535787117543425> Mario <:mario:234535787117543425> is definitely **not top tier**. The plumber's got nothing; no range ✖  , no power 😩  , mediocre recovery 😐  , and bad matchups <:sunglasses_mewtwo:230828762453770240> ☁ He isn't very fast 🐢 , and he doesn't have any strong kill set ups like other top tiers 🍌 ⬇ 👏 ⬆ ✊ The only reason Ally and ANTi were able to win supermajors with him 🏆 is because of **pure skill** , and we will be blessed 🙏  if we ever see two top players carry an upper mid-tier so far again. Obviously **not** a member of the <:mario:234535787117543425> top tier <:mario:234535787117543425>"
        await self.send_message(msg.channel, mariocopypasta)

    @command("^md|doc|doctor|💊$", access=100, name='doctor',
             doc_brief="`doctor`: Prints out the dankest of 💊 Doctor 💊 memes")
    async def doctor(self, msg, arguments):
        doccopypasta = ":pill:Dr Mario:pill: is definitely top tier. The doctor's got it all: good pokes :bear:, ko power :arrow_up::construction_worker::joy::ok_hand:, amazing oos:arrow_up::fist:, and damaging combos :construction_worker::construction_worker::construction_worker:. His presence offstage is not to be ignored, as with proper down b timing, he can cover several recoveries with a hitbox that sends opponents downwards for a gimp :cloud_tornado:. He can also use upsmash to cover several ledge options while being completely safe :construction_worker:. He might move slow :snail:, but he has a projectile :pill: that can force approaches that he can punish with his safe and powerful upsmash :construction_worker:. An obvious member of top 5, unlike that worthless clone <:mario:234535787117543425>:confused::weary::tired_face:.\n:pill: THE :pill: DOCTOR :pill: IS :pill: A :pill: TOP :pill: TIER :pill:"
        await self.send_message(msg.channel, doccopypasta)

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
             '"—GIMR wants to know what\'s the set count going to be against'
             'Chillin. **The people** wanna know."\n'
             '"..."\n"..."\n'
             '"...I don\'t need to *say* anything; everyone knows what I\'m '
             'going to say.\n'
             '<:5_0:252694352315285504> ***AND IT\'S GONNA BE FIVE-OH*** '
             '<:5_0:252694352315285504>\n'
             'That- that\'s how it\'s gonna be."')
    async def chillinrap(self, msg, arguments):
        verse = []
        verse.append("""<:my_b:232583716189241346> I'm not lawful, make <:5_0:252694352315285504> this pussy stop talking 🙊
You're not one of the gods 👼❌, you're one of the god-awfuls 👺✔
We all got gimped <:shine:255634528171851786> 😫 when looking at your Fox <:leffen_fox:230177630035378176>
Bitch, stick to 🚮 Smash 4 🚮  and losing by four stocks 🦊 🦊 🦊 🦊
😤 Not a fan of your style
<:5_0:252694352315285504> You ain't standing your ground
Get wins 🏆👌 while kicking a man when he's down 👢😩
Like, <:5_0:252694352315285504> "I beat Mango <:shine:255634528171851786>🍊, I'm the favorite if he chokes! <:notlikethis:234174248380399617>
As far as Armada 🍑 goes, I'll just wait 🤞 'til he's a host.😏"
Ain't no telling how foolish 😛 you'll be lookin' 👀
Evidence.zip 📁📂 can't contain the ass whooping 👊 🍑
Right when we realize the 💰 money match 💯💸 is over
That'll be your cue to throw your controller 😡 👋 🎮 ⬇""")

        verse.append("""Expose <:5_0:252694352315285504> you as a fraud
Yeah I'll be blowing you up 💥
Who said you were a god? 👼❓
I know it wasn't Plup 🚀🦊<:notlikethis:234174248380399617>👌
Been here 🔟 ten 🗓 years and you know <:my_b:232583716189241346> I'm showing up
For a man of many words <:5_0:252694352315285504>, I think you've said enough 🙊
But, the only way to make you hush
First I'll body bag your Fox 🦊<:shine:255634528171851786>💀 then .zip 📁 it shut
'Imma put you in your place
Kid 👦, you a disgrace 👺
Get killed quick like that missile hit you in the face 🚀<:leffen_fox:230177630035378176>💀
After all of this <:5_0:252694352315285504> you'll be watching 👀 your mouth 🙊
Ain't no telling who'll be calling you out
Salty <:pjsalt:231625734123159563> Suite 🎮 goes down
You better come correct ✔
Until you win a major 🏆 show your elders 👴 some respect 🤝""")

        verse.append("""💌 P.S. Leffen, I ain't done yet <:my_b:232583716189241346>
I'm the underdog 🐶 so place your bets 💸
Whoever want to see <:5_0:252694352315285504> Leffen looking dumb 😜
Throw your money 👋💯💸 on the line cause <:my_b:232583716189241346> I'm making some 💰👌
Gotta say bro 🤔 you're looking awfully weak 😩
Wait and see 👀 what happens at the Salty <:pjsalt:231625734123159563> Suite 🎮
Vanilla Fox 🍦🦊 don't suit you so go find another 🌈🦊
Teach you a lesson and take back my color <:5_0:252694352315285504><:my_b:232583716189241346>""")
        if (arguments[0] is not None):
            reply = verse[int(arguments[0])-1]
            await self.send_message(msg.channel, reply)
        else:
            for i in range(0, 3):
                await self.send_message(msg.channel, verse[i])

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
