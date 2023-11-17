from discord.ext.commands import Cog, Bot
from discord.app_commands import command, describe
from discord import Interaction, Embed
from nltk import sent_tokenize
from httpx import AsyncClient
from typing import Optional
from common.types import question_category
from components.TossupButtons import TossupButtons

class Tossup(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(name="tossup", description="gives a random tossup")
    @describe(category="The category to choose the question from (optional)")
    async def tossup(self, ctx: Interaction, category: Optional[question_category] = None):
        c = AsyncClient()

        params: dict = {"difficulties": [2, 3, 4, 5]}
        if category is not None:
            params["categories"] = category

        req = await c.get("https://qbreader.org/api/random-tossup", params=params)
        tossup: dict = req.json()["tossups"][0]
        tossup["sentences"] = await self.bot.loop.run_in_executor(
            None, sent_tokenize, tossup["question"]
        )

        view: TossupButtons = TossupButtons(tossup)
        embed = Embed(title="Random Tossup", description=tossup["sentences"][0])
        embed.set_author(
            name=f"{tossup['set']['name']} Packet {tossup['packetNumber']} Question {tossup['questionNumber']} (Category: {tossup['category']})"
        )
        embed.set_footer(text="Questions obtained from qbreader.org")
        await ctx.response.send_message(embed=embed, view=view)
        await c.aclose()


async def setup(bot: Bot) -> None:
    await bot.add_cog(Tossup(bot))
