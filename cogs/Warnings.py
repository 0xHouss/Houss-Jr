from nextcord.ext.commands import Cog, Bot

from nextcord.ext import application_checks
from nextcord import (
    Color,
    Embed,
    Interaction,
    Member,
    SlashOption,
    slash_command,
)

from aiosqlite import Connection, Cursor
from datetime import datetime


class Warnings(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client
        client.loop.create_task(self.connect_db())

    async def connect_db(self):
        self.db: Connection = self.client.db
        self.cursor: Cursor = await self.db.cursor()

    @Cog.listener()
    async def on_ready(self):
        await self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS "warnings" (
                    "id"	INTEGER NOT NULL UNIQUE,
                    "memberId"	INTEGER NOT NULL,
                    "guildId"	INTEGER NOT NULL,
                    "reason"	TEXT NOT NULL,
                    "datetime"  TIMESTAMP NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT)
                );"""
        )

    @slash_command(name="warn")
    async def warn(self, interaction: Interaction):
        return

    @application_checks.has_permissions(kick_members=True)
    @warn.subcommand(name="give", description="Warn a user")
    async def give(
        self,
        interaction: Interaction,
        member: Member = SlashOption(
            name="member", description="The member to warn", required=True
        ),
        reason: str = SlashOption(
            name="reason", description="The reason of the warning", required=False
        ),
    ):

        await self.cursor.execute(
            """INSERT INTO "warnings" (memberId, guildId, reason, datetime) VALUES (?, ?, ?, ?);""",
            (member.id, interaction.guild_id, str(reason), datetime.now()),
        )

        warned = Embed(
            color=Color.green(),
            title="Warned!",
            description=f"{member.mention} was warned!",
        )

        if reason:
            warned.add_field(name="Reason", value=reason)

        warned.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar,
        )
        warned.set_thumbnail(url=member.display_avatar)
        await interaction.send(embed=warned)

        warned = Embed(
            color=Color.yellow(),
            title="Warned!",
            description=f"You have been warned in {interaction.guild.name}!",
        )

        if reason:
            warned.add_field(name="Reason", value=reason)

        warned.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar
        )
        warned.set_thumbnail(url=interaction.guild.icon)
        await member.send(embed=warned)

        await self.cursor.execute(
            """SELECT * FROM "warnings" WHERE memberId = ? AND guildId = ?""",
            (member.id, interaction.guild_id),
        )

        warnings = await self.cursor.fetchall()

        if len(warnings) == 3:
            kicked = Embed(
                color=Color.yellow(),
                title="Kicked!",
                description=f"{member.mention} was kicked from the server!",
            )
            if reason:
                kicked.add_field(name="Reason", value="3 Warnings")
            kicked.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            kicked.set_thumbnail(url=member.display_avatar)
            await interaction.send(embed=kicked)

            kicked = Embed(
                color=Color.yellow(),
                title="Kicked!",
                description=f"You have been kicked from the server: **{interaction.guild.name}**!",
            )
            if reason:
                kicked.add_field(name="Reason", value="3 Warnings")
            kicked.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            kicked.set_thumbnail(url=interaction.guild.icon)
            await member.send(embed=kicked)

            # self.client.get_cog("Moderation").kick(interaction, member, reason="3 Warnings")

        elif len(warnings) > 3:
            banned = Embed(
                color=Color.red(),
                title="Banned!",
                description=f"{member.mention} was banned from the server!",
            )
            if reason:
                banned.add_field(name="Reason", value="4 Warnings")
            banned.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            banned.set_thumbnail(url=member.display_avatar)
            await interaction.send(embed=banned)

            banned = Embed(
                color=Color.red(),
                title="Banned!",
                description=f"You have been banned from the server: **{interaction.guild.name}**!",
            )
            if reason:
                banned.add_field(name="Reason", value="4 Warnings")
            banned.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            banned.set_thumbnail(url=interaction.guild.icon)
            await member.send(embed=banned)

            # self.client.get_cog("Moderation").ban(interaction, member, reason="4 Warnings")

            await self.cursor.execute(
                """DELETE FROM "warnings" WHERE memberId = ? AND guildId = ?""",
                (member.id, interaction.guild_id),
            )

        await self.db.commit()

    @application_checks.has_permissions(kick_members=True)
    @warn.subcommand(name="remove", description="Remove a user's warning")
    async def remove(
        self,
        interaction: Interaction,
        member: Member = SlashOption(
            name="member", description="The member to remove a warning", required=True
        ),
        number: int = SlashOption(
            name="id",
            description="The number of the warning to remove (use /warn list to see the warnings",
            required=True,
        ),
        reason: str = SlashOption(
            name="reason", description="The reason of the warning", required=False
        ),
    ):

        await self.cursor.execute(
            """SELECT * FROM "warnings" WHERE memberId = ? AND guildId = ?""",
            (member.id, interaction.guild_id),
        )

        warnings = await self.cursor.fetchall()
        if warnings:
            if number - 1 in range(len(warnings)):
                await self.cursor.execute(
                    """DELETE FROM "warnings" WHERE id = ?""",
                    (warnings[number - 1][0],),
                )

                removed = Embed(
                    color=Color.green(),
                    title="Warning Removed!",
                    description=f"{member.mention}'s warning {number} has been removed!",
                )
                removed.set_author(
                    name=interaction.user.name,
                    icon_url=interaction.user.display_avatar,
                )
                removed.set_thumbnail(url=member.display_avatar)
                await interaction.send(embed=removed)

                warned = Embed(
                    color=Color.green(),
                    title="Warning Removed!",
                    description=f"Your warning number {number} in {interaction.guild.name} has been removed!",
                )

                if reason:
                    warned.add_field(name="Reason", value=reason)

                warned.set_author(
                    name=interaction.user.name, icon_url=interaction.user.display_avatar
                )
                warned.set_thumbnail(url=interaction.guild.icon)
                await member.send(embed=warned)
            else:
                no_warnings = Embed(
                    color=Color.red(),
                    title="Wrong ID!",
                    description=f"{member.mention} has no warning with id {number}!",
                )
                no_warnings.set_author(
                    name=self.client.user.display_name,
                    icon_url=self.client.user.display_avatar,
                )
                no_warnings.set_thumbnail(url=member.display_avatar)
                await interaction.response.send_message(
                    embed=no_warnings, ephemeral=True
                )
        else:
            no_warnings = Embed(
                color=Color.red(),
                title="No Warnings!",
                description=f"{member.mention} has no warnings!",
            )
            no_warnings.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            no_warnings.set_thumbnail(url=member.display_avatar)
            await interaction.response.send_message(embed=no_warnings, ephemeral=True)

        await self.db.commit()

    @application_checks.has_permissions(kick_members=True)
    @warn.subcommand(name="clear", description="Clear user's warnings")
    async def clear(
        self,
        interaction: Interaction,
        member: Member = SlashOption(
            name="member", description="The member to clear his warnings", required=True
        ),
    ):
        
        await self.cursor.execute(
            """SELECT * FROM "warnings" WHERE memberId = ? AND guildId = ?""",
            (member.id, interaction.guild_id),
        )

        warnings = await self.cursor.fetchall()

        if warnings:
            await self.cursor.execute(
                """DELETE FROM "warnings" WHERE memberId = ? AND guildId = ?""",
                (member.id, interaction.guild_id),
            )

            cleared = Embed(
                color=Color.green(),
                title="Warnings Cleared!",
                description=f"{member.mention} warnings have been cleared!",
            )
            cleared.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.display_avatar,
            )
            cleared.set_thumbnail(url=member.display_avatar)
            await interaction.send(embed=cleared)

        else:
            no_warnings = Embed(
                color=Color.red(),
                title="No Warnings!",
                description=f"{member.mention} has no warnings!",
            )
            no_warnings.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            no_warnings.set_thumbnail(url=member.display_avatar)
            await interaction.response.send_message(embed=no_warnings, ephemeral=True)

        await self.db.commit()


def setup(client: Bot):
    client.add_cog(Warnings(client))
