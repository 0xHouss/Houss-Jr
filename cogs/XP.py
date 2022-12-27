import asyncio

from nextcord.ext.commands import Cog, Bot

import math

from nextcord.abc import GuildChannel
from nextcord.ext import application_checks
from nextcord import (
    User,
    Member,
    Embed,
    SlashOption,
    Guild,
    Color,
    Message,
    Interaction,
    Member,
    slash_command,
    utils,
)

from datetime import timedelta


class XP(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client

    @Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(2)
        curr = await self.client.db.cursor()
        await curr.execute(
            """CREATE TABLE IF NOT EXISTS "levels" (
                    "memberId"	INTEGER NOT NULL,
                    "guildId"	INTEGER NOT NULL,
                    "level"	INTEGER NOT NULL,
                    "xp"  INTEGER NOT NULL
                );"""
        )

        for guild in self.client.guilds:
            for member in guild.members:
                if not member.bot:
                    await curr.execute(
                        """SELECT * FROM "levels" WHERE memberId = ? AND guildId = ?""",
                        (member.id, guild.id),
                    )

                    level = await curr.fetchone()

                    if not level:
                        await curr.execute(
                            """INSERT INTO "levels" (memberId, guildId, level, xp) VALUES (?, ?, ?, ?);""",
                            (member.id, guild.id, 1, 0),
                        )

        await self.client.db.commit()

    @Cog.listener()
    async def on_member_join(self, member: Member):
        if not member.bot:
            curr = await self.client.db.cursor()

            await curr.execute(
                """SELECT * FROM "levels" WHERE memberId = ? AND guildId = ?""",
                (member.id, member.guild.id),
            )

            level = await curr.fetchone()

            if not level:
                await curr.execute(
                    """INSERT INTO "levels" (memberId, guildId, level, xp) VALUES (?, ?, ?, ?);""",
                    (member.id, member.guild.id, 1, 0),
                )

            await self.client.db.commit()

    @Cog.listener()
    async def on_message(self, message: Message):
        member: Member = message.author
        if not member.bot:
            curr = await self.client.db.cursor()

            add = 10 * math.floor(len(message.content) / 30)

            await curr.execute(
                """SELECT * FROM "levels" WHERE memberId = ? AND guildId = ?""",
                (member.id, member.guild.id),
            )

            memberId, guildId, level, xp = await curr.fetchone()

            needed = 250 * level

            if xp + add >= needed:
                remaining = xp + add - needed

                await curr.execute(
                    """UPDATE "levels" SET level = ?, xp = ? WHERE memberId = ? AND guildId = ?""",
                    (level + 1, remaining, memberId, guildId),
                )

                await self.levelup()

            else:
                await curr.execute(
                    """UPDATE "levels" SET xp = ? WHERE memberId = ? AND guildId = ?""",
                    (xp + add, memberId, guildId),
                )

            await self.client.db.commit()

    @Cog.listener()
    async def on_message_delete(self, message: Message):
        print(message.content)

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        print(before.content + "->" + after.content)

    @Cog.listener()
    async def on_member_ban(guild: Guild, user: User):
        pass

    async def levelup(message):
        print("leved up")


def setup(client: Bot):
    client.add_cog(XP(client))
