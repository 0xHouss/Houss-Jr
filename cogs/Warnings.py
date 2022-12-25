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

import asyncio
from datetime import datetime


class Warnings(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client

    @Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(2)
        curr = await self.client.db.cursor()
        await curr.execute(
            """CREATE TABLE IF NOT EXISTS "warnings" (
                    "id"	INTEGER NOT NULL UNIQUE,
                    "userId"	INTEGER NOT NULL,
                    "guildId"	INTEGER NOT NULL,
                    "reason"	TEXT NOT NULL,
                    "datetime"  TIMESTAMP NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT)
                );"""
        )
        await self.client.db.commit()

    @application_checks.is_owner()
    @slash_command(name="warn")
    async def warn(self, interaction: Interaction):
        return

    @application_checks.is_owner()
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
        curr = await self.client.db.cursor()
        await curr.execute(
            """INSERT INTO "warnings" (userId, guildId, reason, datetime) VALUES (?, ?, ?, ?);""",
            (member.id, interaction.guild_id, str(reason), datetime.now()),
        )

        warned = Embed(
            Color=Color.green(),
            title="Warned!",
            description=f"{member.mention} was warned {f'for: `{reason}`!' if reason else '!'}",
        )
        warned.set_author(
            name=self.client.user.display_name, icon_url=self.client.user.display_avatar
        )
        warned.set_thumbnail(url=member.display_avatar)
        warned.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar)
        await interaction.send(embed=warned)

        warned = Embed(
            Color=Color.yellow(),
            title="Warned!",
            description=f"You have been warned from {interaction.guild.name} {f'for: `{reason}`!' if reason else '!'}",
        )
        warned.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar
        )
        warned.set_thumbnail(url=interaction.guild.icon)
        warned.set_footer(
            text=f"warned by {interaction.user.name}",
            icon_url=interaction.user.display_avatar,
        )
        await member.send(embed=warned)

        await curr.execute(
            """SELECT * FROM "warnings" WHERE userId = ? AND guildId = ?""",
            (member.id, interaction.guild_id),
        )

        warnings = await curr.fetchall()

        if len(warnings) == 3:
            kicked = Embed(
                Color=Color.yellow(),
                title="Kicked!",
                description=f"{member.mention} was kicked for being warned 3 times!",
            )
            kicked.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            kicked.set_thumbnail(url=member.display_avatar)
            await interaction.send(embed=kicked)

            kicked = Embed(
                Color=Color.yellow(),
                title="Kicked!",
                description=f"You have been kicked from {interaction.guild.name} for being warned 3 times!",
            )
            kicked.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            kicked.set_thumbnail(url=interaction.guild.icon)
            await member.send(embed=kicked)

            # await member.kick(reason=reason)

        elif len(warnings) > 3:
            banned = Embed(
                Color=Color.red(),
                title="Banned!",
                description=f"{member.mention} was banned for being warned 4 times!",
            )
            banned.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            banned.set_thumbnail(url=member.display_avatar)
            await interaction.send(embed=banned)

            banned = Embed(
                Color=Color.red(),
                title="Banned!",
                description=f"You have been banned from {interaction.guild.name} for being warned 4 times!",
            )
            banned.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            banned.set_thumbnail(url=interaction.guild.icon)
            await member.send(embed=banned)

            # await member.ban(reason=reason)

            await curr.execute(
                """DELETE FROM "warnings" WHERE userId = ? AND guildId = ?""",
                (member.id, interaction.guild_id),
            )

        await self.client.db.commit()

    @warn.subcommand(name="clear", description="Clear user's warnings")
    async def clear(
        self,
        interaction: Interaction,
        member: Member = SlashOption(
            name="member", description="The member to clear his warnings", required=True
        )
    ):

        curr = await self.client.db.cursor()
        await curr.execute(
            """SELECT * FROM "warnings" WHERE userId = ? AND guildId = ?""",
            (member.id, interaction.guild_id),
        )

        warnings = await curr.fetchall()

        if warnings:
            await curr.execute(
                """DELETE FROM "warnings" WHERE userId = ? AND guildId = ?""",
                (member.id, interaction.guild_id),
            )

            cleared = Embed(Color=Color.green(), title="Warnings Cleared!", description=f"{member.mention} warnings have been cleared!")
            cleared.set_author(
            name=self.client.user.display_name, icon_url=self.client.user.display_avatar
            )
            cleared.set_thumbnail(url=member.display_avatar)
            cleared.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar)
            await interaction.send(embed=cleared)

        else:
            no_warnings = Embed(Color=Color.red(), title="No Warnings!", description=f"{member.mention} has no warnings!")
            no_warnings.set_author(
            name=self.client.user.display_name, icon_url=self.client.user.display_avatar
            )
            no_warnings.set_thumbnail(url=member.display_avatar)
            await interaction.response.send_message(embed=no_warnings, ephemeral=True)

        await self.client.db.commit()

    @warn.subcommand(name="list", description="List user's warnings")
    async def list(
        self,
        interaction: Interaction,
        member: Member = SlashOption(
            name="member", description="The member to list his warnings", required=True
        )
    ):

        curr = await self.client.db.cursor()
        await curr.execute(
            """SELECT * FROM "warnings" WHERE userId = ? AND guildId = ?""",
            (member.id, interaction.guild_id),
        )

        warnings = await curr.fetchall()
        print(warnings)
        if warnings:
            warnings_list = Embed(Color=Color.green(), title="User Warnings", description=f"{member.mention} warnings:")

            for id, userId, guildId, reason, datetime in warnings:
                warnings_list.add_field(name=f"Reason: {reason}", value=f"Date: {str(datetime).split('.')[0]}")

            warnings_list.set_author(
            name=self.client.user.display_name, icon_url=self.client.user.display_avatar
            )
            warnings_list.set_thumbnail(url=member.display_avatar)
            warnings_list.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar)
            await interaction.send(embed=warnings_list)

        else:
            no_warnings = Embed(Color=Color.red(), title="No Warnings!", description=f"{member.mention} has no warnings!")
            no_warnings.set_author(
            name=self.client.user.display_name, icon_url=self.client.user.display_avatar
            )
            no_warnings.set_thumbnail(url=member.display_avatar)
            await interaction.response.send_message(embed=no_warnings, ephemeral=True)

        await self.client.db.commit()


def setup(client: Bot):
    client.add_cog(Warnings(client))
