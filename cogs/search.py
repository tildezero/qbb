from discord.ext.commands import GroupCog, Bot
from discord.app_commands import command, describe
from discord import Interaction, Embed
from httpx import AsyncClient
from textwrap import dedent

from urllib.parse import urlencode
from bs4 import BeautifulSoup, Tag
from tabulate import tabulate


class Search(GroupCog, name="search"):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        super().__init__()

    @command(description="Do a tossup in solo mode (only you can control the tossup)")
    @describe(first_name="The first name of the player you are trying to find", last_name="The last name of the player you are trying to find")
    async def player(self, ctx: Interaction, first_name: str, last_name: str):
        c = AsyncClient()
        req = await c.get(f'https://www.naqt.com/stats/player/search.jsp?PASSBACK=PLAYER_SEARCH&first_name={first_name}&last_name={last_name}')
        data = BeautifulSoup(req.text, 'lxml')
        results = data.find('section', attrs={'id': 'results'})
        if results.table is not None:
            # multiple results
            return await ctx.response.send_message("There are more than one of you and im too lazy to do the logic for this")
        if results.p.get('class') is not None:
            return await ctx.response.send_message('Person with this name not found in NAQT database')
        link_to_person = results.p.a.get('href')
        assert isinstance(link_to_person, str)
        person_req = await c.get(f'https://www.naqt.com/{link_to_person}')
        person = BeautifulSoup(person_req.text, 'lxml')
        tbl = person.find('section', attrs={'id': 'results'}).table

        headers = [e.text for e in tbl.thead.tr.find_all('th')]
        print(headers)

        data = []

        elem: Tag
        for elem in tbl.tbody.find_all('tr'):
            temp = []
            z: Tag
            for z in elem.find_all(['th', 'td']):
                temp.append(z.text)
            print(temp)
            data.append(temp)

        tbl = tabulate(data, headers, showindex=False)
        affil = person.find('section', attrs={'id': 'affiliations'}).p.text
        

        # await ctx.response.send_message(f"```\n{tbl}\n```")
        await ctx.response.send_message(dedent(f"""## Stats for {person.h1.text}
### Affiliations
{affil}
### Tournament Results
```
{tbl}
```
Key: TUH=Tossups Heard, P=Powers, T=Tossups (10 pts), I=Interrupts, P%=Power Percentage, PP20TUH=Pts per 20 Tossups Heard"""))
        await c.aclose()

async def setup(bot: Bot) -> None:
    await bot.add_cog(Search(bot))
