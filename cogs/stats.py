from discord.ext.commands import Cog, Bot
from discord.app_commands import command
from discord import Interaction, Embed, Color
from prisma import Prisma
from common.types import category_field_translations

reverse_categories = {v: k for k, v in category_field_translations.items()}

class Stats(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        super().__init__()

    @command(description="Get your statistics for qbb")
    async def stats(self, ctx: Interaction):
        db = Prisma()
        await db.connect()
        stats = await db.user.find_first(where={'id': ctx.user.id})
        cb = await db.categorybreakdown.find_first(where={'userId': ctx.user.id})
        if stats is None or cb is None:
            embed = Embed(title="No Stats!", description="You have no stats! Trying using the bot and then running this command", color=Color.red())
            return await ctx.response.send_message(embed=embed)
        embed = Embed(title="Your Stats!", description=f"""**Number of correct tossups:** {stats.questions_correct}
        **Number of incorrect tossups:** {stats.questions_incorrect}
        """)
        for cat in category_field_translations.values():
            corr = getattr(cb, f'{cat}_correct')
            incorr = getattr(cb, f'{cat}_incorrect')
            embed.add_field(name=reverse_categories[cat], value=f'{corr+incorr} heard ({corr} correct)')
        await ctx.response.send_message(embed=embed)
        await db.disconnect()

async def setup(bot: Bot) -> None:
    await bot.add_cog(Stats(bot))
