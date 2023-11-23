import discord
from discord import Interaction, Intents, Embed
from discord.ext.commands import Bot, Context, when_mentioned
from dotenv import load_dotenv
from os import getenv
from sys import exit
from typing import Literal
import httpx
import nltk
import asyncio

load_dotenv()

token = getenv('TOKEN')
owner_id = getenv('OWNER_ID')
if token is None or owner_id is None:
    print('please set a TOKEN and OWNER_ID environment variable')
    exit(1)

class QBBBot(Bot):
    def __init__(self) -> None:
        i = Intents.default()
        i.members = True
        super().__init__(command_prefix=when_mentioned, intents=i)

    async def setup_hook(self):
        await self.load_extension('cogs.tossup')
        await self.load_extension('cogs.solo')
        await self.load_extension('cogs.stats')
        await self.load_extension('cogs.search')
        await self.load_extension('jishaku')


bot = QBBBot()



@bot.command()
async def sync(ctx: Context):
    if str(ctx.author.id) == owner_id:
        await bot.tree.sync()
        await ctx.send('ok')
    else:
        await ctx.send('no')

bot.run(token)
