from discord.ui import View, button, Button
from discord import ButtonStyle, Interaction, User, Member, Color
from .AnswerModal import Answer, SoloAnswer
from typing import Union

class TossupButtons(View):
    def __init__(self, tossup) -> None:
        self.tossup = tossup
        self.already_answered = []
        self.already_voted = []
        self.i = 0
        self.final_answer_votes = 0
        super().__init__()

    @button(label="Answer!", style=ButtonStyle.green)
    async def answer(self, interaction: Interaction, button: Button):
        if interaction.user.id not in self.already_answered:
            await interaction.response.send_modal(
                Answer(self.tossup.get('formatted_answer', self.tossup['answer']), self)
            )
        else:
            await interaction.response.send_message(
                "you've already answered!", ephemeral=True
            )

    @button(label="Add sentence", style=ButtonStyle.blurple)
    async def add_sentence(self, interaction: Interaction, button: Button):
        if interaction.user.id in self.already_answered:
            return await interaction.response.send_message(
                "you've already answered!", ephemeral=True
            )
        if interaction.message is None:
            return interaction.response.send_message("Couldn't find the message!", ephemeral=True)
        e = interaction.message.embeds[0]
        self.i += 1
        if self.i == len(self.tossup["sentences"]):
            button.disabled = True
        e.description = "\n".join(self.tossup["sentences"][0 : self.i + 1])
        await interaction.response.edit_message(embed=e, view=self)

    @button(label="Vote to Reveal Answer (0/3)", style=ButtonStyle.red)
    async def reveal_answer(self, interaction: Interaction, button: Button):
        if interaction.user.id in self.already_voted:
            return await interaction.response.send_message(
                "you've already voted!", ephemeral=True
            )
        self.already_voted.append(interaction.user.id)
        self.final_answer_votes += 1
        button.label = f"vote to reveal answer ({self.final_answer_votes}/3)"
        if self.final_answer_votes >= 3:
            if interaction.message is None:
                return interaction.response.send_message("Couldn't find the message!", ephemeral=True)
            e = interaction.message.embeds[0]
            e.title = '[SKIPPED] Random Tossup'
            e.color = Color.orange()
            e.description = self.tossup["question"]
            e.add_field(name="Answer", value=self.tossup["answer"])
            for item in self.children:
                if isinstance(item, Button):
                    item.disabled = True
            return await interaction.response.edit_message(embed=e, view=self)
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("you've voted!", ephemeral=True)

class SoloTossupButtons(View):
    def __init__(self, tossup, user: Union[User, Member]) -> None:
        self.user = user
        self.tossup = tossup
        self.i = 0
        super().__init__()

    @button(label="Answer!", style=ButtonStyle.green)
    async def answer(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.user.id:
            return interaction.response.send_message('This is not your tossup!', ephemeral=True)
        await interaction.response.send_modal(SoloAnswer(self.tossup.get('formatted_answer', self.tossup['answer']), self))

    @button(label="Add sentence", style=ButtonStyle.blurple)
    async def add_sentence(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(
                "not your tossup!", ephemeral=True
            )
        if interaction.message is None:
            return interaction.response.send_message("Couldn't find the message!", ephemeral=True)
        e = interaction.message.embeds[0]
        self.i += 1
        if self.i == len(self.tossup["sentences"]) - 1:
            button.disabled = True
        e.description = "\n".join(self.tossup["sentences"][0 : self.i + 1])
        await interaction.response.edit_message(embed=e, view=self)

    @button(label="Reveal Answer", style=ButtonStyle.red)
    async def reveal_answer(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(
                "not your tossup!", ephemeral=True
            )
        if interaction.message is None:
            return await interaction.response.send_message('Error!')
        e = interaction.message.embeds[0]
        e.title = f'[SKIPPED] Random Tossup'
        e.color = Color.orange()
        e.description = self.tossup["question"]
        e.add_field(name="Answer", value=self.tossup["answer"])
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        return await interaction.response.edit_message(embed=e, view=self)
