from __future__ import annotations
from discord.ui import Modal, TextInput
from httpx import AsyncClient
from discord import Interaction, Color
from prisma import Prisma
from prisma.models import User 
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from .TossupButtons import TossupButtons, SoloTossupButtons
from discord import Button
from common.types import category_field_translations


class Answer(Modal, title="Submit Answer"):
    def __init__(self, correct_answer: str, view: TossupButtons) -> None:
        self.correct_answer = correct_answer
        self.view = view
        self.stop_working = False
        super().__init__()

    answer = TextInput(label="Answer", placeholder="Your answer here")

    async def on_submit(self, interaction: Interaction) -> None:
        c = AsyncClient()
        db = Prisma(auto_register=True)
        answer_check_resp = await c.get(
            "https://qbreader.org/api/check-answer",
            params={
                "answerline": self.correct_answer,
                "givenAnswer": self.answer.value,
            },
        )
        answer_check_data = answer_check_resp.json()
        await db.connect()

        if answer_check_data["directive"] == "accept":
            if self.stop_working:
                return await interaction.response.send_message('Someone has already answered this correctly!', ephemeral=True)
            if interaction.message is None:
                return 
            e = interaction.message.embeds[0]
            e.color = Color.green()
            e.title = '[CORRECT!] Random Tossup'
            e.description = ".".join(self.view.tossup['sentences'][0:self.view.i+1]) + " **(BUZZ)** " + ".".join(self.view.tossup['sentences'][self.view.i+1:])
            e.add_field(name='Your answer', value=self.answer.value)
            e.add_field(name='Official answer', value=self.view.tossup['answer'])
            e.add_field(name='Answered by', value=interaction.user.mention)
            items = self.view.children
            for item in items:
                if isinstance(item, Button):
                    item.disabled = True
            self.stop_working = True
            await interaction.response.edit_message(embed=e, view=self.view)
            await User.prisma().upsert(where={'id': interaction.user.id}, data={
                'create': {'questions_correct': 1, 'id': interaction.user.id, 'questions_incorrect': 0},
                'update': {'questions_correct': {'increment': 1}}
            })
            category = category_field_translations[self.view.tossup['category']]
            await db.execute_raw(f"""
                INSERT INTO CategoryBreakdown(userId, {category}_correct) VALUES (?, 0)
                    ON CONFLICT(userId) DO UPDATE SET {category}_correct={category}_correct+1
            """, interaction.user.id)
        elif answer_check_data['directive'] == 'prompt':
            await interaction.response.send_message("Prompt! Try answering the question again", ephemeral=True)
        else:
            await interaction.response.send_message(f"Incorrect! You've been locked out from the question. The correct answer was {self.view.tossup['answer']}", ephemeral=True)
            self.view.already_answered.append(interaction.user.id)
            await User.prisma().upsert(
                where={'id': interaction.user.id},
                data={
                    'create': {'questions_correct': 0, 'id': interaction.user.id, 'questions_incorrect': 1},
                    'update': {'questions_incorrect': {'increment': 1}}
                }
            )
            category = category_field_translations[self.view.tossup['category']]
            await db.execute_raw(f"""
                INSERT INTO CategoryBreakdown(userId, {category}_incorrect) VALUES (?, 0)
                    ON CONFLICT(userId) DO UPDATE SET {category}_incorrect={category}_incorrect+1
            """, interaction.user.id)
        await db.disconnect()
        await c.aclose()

class SoloAnswer(Modal, title="Submit Answer"):
    def __init__(self, correct_answer: str, view: SoloTossupButtons) -> None:
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
            if interaction.message is None:
                return
            e = interaction.message.embeds[0]
            e.color = Color.green()
            e.title = '[CORRECT!] Random Tossup'
            e.description = ".".join(self.view.tossup['sentences'][0:self.view.i+1]) + " **(BUZZ)** " + ".".join(self.view.tossup['sentences'][self.view.i+1:])
            e.add_field(name='Your answer', value=self.answer.value)
            e.add_field(name='Official answer', value=self.view.tossup['answer'])
            items = self.view.children
            for item in items:
                if isinstance(item, Button):
                    item.disabled = True
            await interaction.response.edit_message(embed=e, view=self.view)
        else:
            if interaction.message is None:
                return
            e = interaction.message.embeds[0]
            e.color = Color.red()
            e.title = '[INCORRECT] Random Tossup'
            e.description = ".".join(self.view.tossup['sentences'][0:self.view.i+1]) + " **(BUZZ)** " + ".".join(self.view.tossup['sentences'][self.view.i+1:])
            e.add_field(name='Correct answer was...', value=self.view.tossup['answer'])
            e.add_field(name='Your answer', value=self.answer.value)
            items = self.view.children
            for item in items:
                if isinstance(item, Button):
                    item.disabled = True
            await interaction.response.edit_message(embed=e, view=self.view)
        await c.aclose()
