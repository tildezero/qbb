from discord.ui import Modal, TextInput, View
from httpx import AsyncClient
from discord import Interaction, Color


class Answer(Modal, title="Submit Answer"):
    def __init__(self, correct_answer: str, view: View) -> None:
        self.correct_answer = correct_answer
        self.view = view
        super().__init__()

    answer = TextInput(label="Answer", placeholder="Your answer here")

    async def on_submit(self, interaction: Interaction) -> None:
        c = AsyncClient()
        answer_check_resp = await c.get(
            "https://qbreader.org/api/check-answer",
            params={
                "answerline": self.correct_answer,
                "givenAnswer": self.answer.value,
            },
        )
        answer_check_data = answer_check_resp.json()

        if answer_check_data["directive"] == "accept":
            e = interaction.message.embeds[0]
            e.color = Color.green()
            e.title = '[CORRECT!] Random Tossup'
            e.description = ".".join(self.view.tossup['sentences'][0:self.view.i+1]) + " **(BUZZ)** " + ".".join(self.view.tossup['sentences'][self.view.i+1:])
            e.add_field(name='Your answer', value=self.answer.value)
            e.add_field(name='Official answer', value=self.view.tossup['answer'])
            e.add_field(name='Answered by', value=interaction.user.mention)
            items = self.view.children
            for item in items:
                item.disabled = True
            await interaction.response.edit_message(embed=e, view=self.view)
        elif answer_check_data['directive'] == 'prompt':
            await interaction.response.send_message("Prompt! Try answering the question again", ephemeral=True)
        else:
            await interaction.response.send_message(f"Incorrect! You've been locked out from the question. The correct answer was {self.view.tossup['answer']}", ephemeral=True)
            self.view.already_answered.append(interaction.user.id)
        await c.aclose()

class SoloAnswer(Modal, title="Submit Answer"):
    def __init__(self, correct_answer: str, view: View) -> None:
        self.correct_answer = correct_answer
        self.view = view
        super().__init__()

    answer = TextInput(label="Answer", placeholder="your answer here!")

    async def on_submit(self, interaction: Interaction) -> None:
        c = AsyncClient()
        answer_check_resp = await c.get(
            "https://qbreader.org/api/check-answer",
            params={
                "answerline": self.correct_answer,
                "givenAnswer": self.answer.value,
            },
        )
        answer_check_data = answer_check_resp.json()

        if answer_check_data["directive"] == "accept":
            e = interaction.message.embeds[0]
            e.color = Color.green()
            e.title = '[CORRECT!] Random Tossup'
            e.description = ".".join(self.view.tossup['sentences'][0:self.view.i+1]) + " **(BUZZ)** " + ".".join(self.view.tossup['sentences'][self.view.i+1:])
            e.add_field(name='Your answer', value=self.answer.value)
            e.add_field(name='Official answer', value=self.view.tossup['answer'])
            items = self.view.children
            for item in items:
                item.disabled = True
            await interaction.response.edit_message(embed=e, view=self.view)
        else:
            e = interaction.message.embeds[0]
            e.color = Color.red()
            e.title = '[INCORRECT] Random Tossup'
            e.description = ".".join(self.view.tossup['sentences'][0:self.view.i+1]) + " **(BUZZ)** " + ".".join(self.view.tossup['sentences'][self.view.i+1:])
            e.add_field(name='Correct answer was...', value=self.view.tossup['answer'])
            e.add_field(name='Your answer', value=self.answer.value)
            items = self.view.children
            for item in items:
                item.disabled = True
            await interaction.response.edit_message(embed=e, view=self.view)
        await c.aclose()
