from discord.ext.commands import GroupCog, Bot
from discord.ui import View, Button, Modal, button, TextInput
from discord.app_commands import command
from discord import Interaction, Embed, User, Member, ButtonStyle, Color
from httpx import AsyncClient
from nltk import sent_tokenize
from typing import Union, Optional
from common.types import question_category
from components.TossupButtons import SoloTossupButtons


class Solo(GroupCog, name="solo"):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        super().__init__()

    @command(description="Do a tossup in solo mode (only you can control the tossup)")
    async def tossup(self, ctx: Interaction, category: Optional[question_category] = None):
        c = AsyncClient()
        params: dict = {'difficulties': [2,3,4,5]}
        if category is not None:
            params['categories'] = category

        req = await c.get(
            "https://qbreader.org/api/random-tossup", params=params
        )
        tossup: dict = req.json()["tossups"][0]
        tossup['sentences'] = await self.bot.loop.run_in_executor(None, sent_tokenize, tossup['question'])


        view: SoloTossupButtons = SoloTossupButtons(tossup, ctx.user)
        embed = Embed(title="Random Tossup", description=tossup["sentences"][0])
        embed.set_author(
            name=f"{tossup['set']['name']} Packet {tossup['packetNumber']} Question {tossup['questionNumber']}"
        )
        embed.set_footer(text="Questions obtained from qbreader.org")
        await ctx.response.send_message(embed=embed, view=view)
        await c.aclose()

async def setup(bot: Bot) -> None:
    await bot.add_cog(Solo(bot))
