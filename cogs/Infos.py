from datetime import datetime
from nextcord import slash_command, Interaction, Embed, Color, Member, SlashOption
from nextcord.ext import application_checks
from nextcord.ext.commands import Cog, Bot

from numerize.numerize import numerize

from aiosqlite import Connection, Cursor


class Infos(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client
        client.loop.create_task(self.connect_db())

    async def connect_db(self):
        self.db: Connection = self.client.db
        self.cursor: Cursor = await self.db.cursor()

    @slash_command(name="stats")
    async def stats(self, interaction: Interaction):
        return

    @stats.subcommand(name="board")
    async def board(self, interaction: Interaction):
        await self.user_stats(interaction, interaction.user)

    @stats.subcommand(name="warnings")
    async def warnings(self, interaction: Interaction):
        await self.user_warnings(interaction, interaction.user)

    @stats.subcommand(name="level")
    async def level(self, interaction: Interaction):
        await self.user_level(interaction, interaction.user)

    @slash_command(name="user")
    async def user(self, interaction: Interaction):
        return

    @application_checks.has_permissions(administrator=True)
    @user.subcommand(name="stats")
    async def user_stats(
        self,
        interaction: Interaction,
        member: Member = SlashOption(
            name="member", description="The member to show his stats", required=False
        ),
    ):
        if not member:
            member = interaction.user

        await self.cursor.execute(
            """SELECT level, xp FROM "levels" WHERE memberId = ? AND guildId = ?""",
            (member.id, interaction.guild_id),
        )

        level, xp = await self.cursor.fetchone()

        needed = 250 * level

        infos = Embed(
            title=member.name,
            description=member.mention,
            color=Color.blue(),
        )
        infos.add_field(name="ID:", value=member.id, inline=False)
        infos.add_field(name="Level:", value=level)
        infos.add_field(name="XP:", value=f"{numerize(xp)}/{numerize(needed)}")

        await self.cursor.execute(
            """SELECT * FROM "warnings" WHERE memberId = ? AND guildId = ?""",
            (member.id, interaction.guild_id),
        )

        warnings = await self.cursor.fetchall()
        infos.add_field(
            name="Warnings:",
            value=f"{len(warnings) if warnings else 'No'} warning{'s' if len(warnings) > 1 else ''}",
            inline=False,
        )

        infos.add_field(
            name="Joined :",
            value=member.joined_at.strftime("%H:%M | %d %b %Y"),
            inline=True,
        )
        infos.add_field(name="|", value="|", inline=True)
        infos.add_field(
            name="Created :",
            value=member.created_at.strftime("%H:%M | %d %b %Y"),
            inline=True,
        )

        infos.set_thumbnail(url=member.display_avatar)
        infos.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar,
        )
        await interaction.send(embed=infos)

    @application_checks.has_permissions(administrator=True)
    @user.subcommand(name="warnings")
    async def user_warnings(
        self,
        interaction: Interaction,
        member: Member = SlashOption(
            name="member", description="The member to list his warnings", required=False
        ),
    ):
        if not member:
            member = interaction.user

        await self.cursor.execute(
            """SELECT * FROM "warnings" WHERE memberId = ? AND guildId = ?""",
            (member.id, interaction.guild_id),
        )

        warnings = await self.cursor.fetchall()
        if warnings:
            warnings_list = Embed(
                color=Color.blue(),
                title=member.name,
            )

            parser = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%H:%M | %d/%m/%Y"
            )

            i = 1
            for *_, reason, time in warnings:
                warnings_list.add_field(
                    name=f"Warning {i}",
                    value=f"""
                        Reason: {reason}
                        Date: {parser(time)}
                    """,
                    inline=False,
                )
                i += 1

            warnings_list.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.display_avatar,
            )
            warnings_list.set_thumbnail(url=member.display_avatar)
            await interaction.send(embed=warnings_list)

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

    @application_checks.has_permissions(administrator=True)
    @user.subcommand(name="level")
    async def user_level(
        self,
        interaction: Interaction,
        member: Member = SlashOption(
            name="member",
            description="The member to display his level board",
            required=False,
        ),
    ):
        member = member if member else interaction.user

        await self.cursor.execute(
            """SELECT level, xp FROM "levels" WHERE memberId = ? AND guildId = ?""",
            (member.id, interaction.guild_id),
        )

        level, xp = await self.cursor.fetchone()

        needed = 250 * level

        board = Embed(title=member.name, color=Color.blue())
        board.set_thumbnail(url=member.display_avatar)
        board.add_field(name="Level:", value=level)
        board.add_field(name="XP:", value=f"{numerize(xp)}/{numerize(needed)}")
        board.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.display_avatar,
            )

        await interaction.response.send_message(embed=board, ephemeral=True)


def setup(client: Bot):
    client.add_cog(Infos(client))
