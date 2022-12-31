import asyncio
from aiosqlite import Connection, Cursor
from nextcord.ext.commands import Cog, Bot

import math

from numerize.numerize import numerize

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


class Levels(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client
        client.loop.create_task(self.connect_db())

    async def connect_db(self):
        self.db: Connection = self.client.db
        self.cursor: Cursor = await self.db.cursor()

    @Cog.listener()
    async def on_ready(self):
        await self.cursor.execute(
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
                    await self.cursor.execute(
                        """SELECT * FROM "levels" WHERE memberId = ? AND guildId = ?""",
                        (member.id, guild.id),
                    )

                    level = await self.cursor.fetchone()

                    if not level:
                        await self.cursor.execute(
                            """INSERT INTO "levels" (memberId, guildId, level, xp) VALUES (?, ?, ?, ?);""",
                            (member.id, guild.id, 1, 0),
                        )

                    level_role = utils.get(member.guild.roles, name=f"Level 1")

                    if not level_role:
                        await guild.create_role(name=f"Level 1")
                        level_role = utils.get(guild.roles, name=f"Level 1")

                    await member.add_roles(level_role)

        await self.db.commit()

    @Cog.listener()
    async def on_member_join(self, member: Member):
        if not member.bot:
            await self.cursor.execute(
                """SELECT * FROM "levels" WHERE memberId = ? AND guildId = ?""",
                (member.id, member.guild.id),
            )

            level = await self.cursor.fetchone()

            if not level:
                await self.cursor.execute(
                    """INSERT INTO "levels" (memberId, guildId, level, xp) VALUES (?, ?, ?, ?);""",
                    (member.id, member.guild.id, 1, 0),
                )

            await self.db.commit()

            level_role = utils.get(member.guild.roles, name=f"Level 1")

            if not level_role:
                await member.guild.create_role(name=f"Level 1")
                level_role = utils.get(member.guild.roles, name=f"Level 1")

            await member.add_roles(level_role)

    @Cog.listener()
    async def on_message(self, message: Message):
        member: Member = message.author
        if not member.bot:
            add = 10 * math.floor(len(message.content) / 30)

            await self.cursor.execute(
                """SELECT xp FROM "levels" WHERE memberId = ? AND guildId = ?""",
                (member.id, member.guild.id),
            )

            xp = await self.cursor.fetchone()

            await self.cursor.execute(
                """UPDATE "levels" SET xp = ? WHERE memberId = ? AND guildId = ?""",
                (xp[0] + add, member.id, member.guild.id),
            )

            await self.levelup(member)

            await self.db.commit()

    @Cog.listener()
    async def on_member_ban(self, guild: Guild, user: User):
        if not user.bot:

            await self.cursor.execute(
                """SELECT * FROM "levels" WHERE memberId = ? AND guildId = ?""",
                (user.id, guild.id),
            )

            level = await self.cursor.fetchone()

            if level:
                await self.cursor.execute(
                    """DELETE FROM "levels" WHERE memberId = ? AND guildId = ?""",
                    (user.id, guild.id),
                )

            await self.db.commit()

    async def levelup(self, member: Member):
        if not member.bot:

            await self.cursor.execute(
                """SELECT * FROM "levels" WHERE memberId = ? AND guildId = ?""",
                (member.id, member.guild.id),
            )

            memberId, guildId, level, xp = await self.cursor.fetchone()

            needed = 250 * level

            if xp >= needed:
                await self.cursor.execute(
                    """UPDATE "levels" SET level = ?, xp = ? WHERE memberId = ? AND guildId = ?""",
                    (level + 1, xp - needed, memberId, guildId),
                )

                await self.db.commit()

                await self.cursor.execute(
                    """SELECT levelsChannelId FROM "configs" WHERE guildId = ?""",
                    (member.guild.id,),
                )

                levels_channel_id = await self.cursor.fetchone()

                if levels_channel_id[0]:
                    channel = member.guild.get_channel(levels_channel_id[0])

                    await self.cursor.execute(
                        """SELECT level FROM "levels" WHERE memberId = ? AND guildId = ?""",
                        (member.id, member.guild.id),
                    )

                    level = await self.cursor.fetchone()

                    board = Embed(
                        title=f"{member.name} is now level {level[0]}",
                        color=Color.blue(),
                    )
                    board.set_thumbnail(url=member.display_avatar)

                    await channel.send(embed=board)

                level_role = utils.get(member.guild.roles, name=f"Level {level}")

                if not level_role:
                    await member.guild.create_role(name=f"Level {level}")
                    level_role = utils.get(member.guild.roles, name=f"Level {level}")

                for role in member.roles:
                    if role.name.startswith("Level"):
                        print(role)
                        await member.remove_roles(role)

                await member.add_roles(level_role)

                await self.levelup(member)

    @slash_command(name="level", description="Level commands")
    async def level(self, interaction: Interaction):
        return

    @level.subcommand(name="give", description="Give xp/levels to a member")
    async def give(
        self,
        interaction: Interaction,
        member: Member = SlashOption(
            name="member", description="The member to who'm give xp", required=True
        ),
        xp: int = SlashOption(
            name="xp", description="The number of xp to add", required=True
        ),
        add_levels: int = SlashOption(
            name="levels", description="The number of levels to add", required=True
        ),
        add_xp: int = SlashOption(
            name="xp", description="The number of xp to add", required=True
        ),
    ):

        await self.cursor.execute(
            """SELECT level, xp FROM "levels" WHERE memberId = ? AND guildId = ?""",
            (member.id, member.guild.id),
        )

        level, xp = await self.cursor.fetchone()

        for i in range(add_levels):
            add_xp += (level + i) * 250

        await self.cursor.execute(
            """UPDATE "levels" SET xp = ? WHERE memberId = ? AND guildId = ?""",
            (xp + add_xp, member.id, member.guild.id),
        )

        await self.db.commit()

        added = Embed(
            title="Added", description=f"{member.mention} gained:", color=Color.green()
        )
        added.set_thumbnail(url=member.display_avatar)
        added.set_author(
            icon_url=interaction.user.avatar.url,
            name=interaction.user.name,
        )
        added.add_field(name="XP:", value=add_xp)

        await interaction.send(embed=added)

        await self.levelup(member)

    @level.subcommand(name="clear", description="Clear member's xp")
    async def clear(
        self,
        interaction: Interaction,
        member: Member = SlashOption(
            name="member", description="The member to who'm clear xp", required=True
        ),
    ):
        await self.cursor.execute(
            """UPDATE "levels" SET level = ?, xp = ? WHERE memberId = ? AND guildId = ?""",
            (1, 0, member.id, member.guild.id),
        )

        cleared = Embed(
            title="Cleared!",
            description=f"{member.mention} xp has been cleared!",
            color=Color.green(),
        )
        cleared.set_thumbnail(url=member.display_avatar)
        cleared.set_author(
            icon_url=interaction.user.avatar.url,
            name=interaction.user.name,
        )

        await interaction.send(embed=cleared)

        await self.cursor.execute(
            """SELECT levelsChannelId FROM "configs" WHERE guildId = ?""",
            (member.guild.id,),
        )

        await self.db.commit()

        levels_channel_id = await self.cursor.fetchone()

        if levels_channel_id[0]:
            channel = member.guild.get_channel(levels_channel_id[0])

            board = Embed(
                title=f"{member.name} is now back at level 1", color=Color.blue()
            )
            board.set_thumbnail(url=member.display_avatar)

            await channel.send(embed=board)


def setup(client: Bot):
    client.add_cog(Levels(client))
