import asyncio

from nextcord.ext.commands import Cog, Bot

from nextcord.abc import GuildChannel
from nextcord.ext import application_checks
from nextcord import (
    User,
    Member,
    Embed,
    SlashOption,
    Color,
    Interaction,
    Member,
    slash_command,
)


class Moderation(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client

    @slash_command(name="who")
    async def who(self, interaction: Interaction):
        return

    @who.subcommand(name="is", description="Get user's infos")
    async def who_is(self, interaction: Interaction, member: Member):
        embed = Embed(
            title=member.name,
            description=member.mention,
            color=Color.blue(),
        )
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(
            name="Joined :",
            value=member.joined_at.strftime("%H:%M | %d %b %Y"),
            inline=True,
        )
        embed.add_field(name="|", value="|", inline=True)
        embed.add_field(
            name="Created :",
            value=member.created_at.strftime("%H:%M | %d %b %Y"),
            inline=True,
        )

        embed.set_thumbnail(url=member.display_avatar)
        embed.set_footer(
            icon_url=interaction.user.display_avatar,
            text=f"Requested by {interaction.user.name}",
        )
        await interaction.send(embed=embed)

    @slash_command(name="clear", description="To clear the channel")
    async def clear(
        self,
        interaction: Interaction,
        channel: GuildChannel = SlashOption(
            name="channel", description="The channel to clear", required=False
        ),
        limit: int = SlashOption(
            name="limit", description="Number of messages to clear", required=False
        ),
    ):

        if not channel:
            channel = interaction.channel

        clearing = Embed(title="Clearing the channel...", color=Color.green())

        await interaction.send(embed=clearing)

        await channel.purge(limit=int(limit) if limit else None)

        cleared = Embed(title="The channel has been cleared", color=Color.green())
        cleared.set_footer(
            icon_url=interaction.user.avatar.url,
            text=f"Cleared by {interaction.user.name}",
        )

        response = await interaction.followup.send(embed=cleared)

        await asyncio.sleep(5)
        await response.delete()

    @slash_command(name="kick", description="To kick a member")
    async def kick(
        self,
        interaction: Interaction,
        member: Member = SlashOption(name="membre", description="The member to kick"),
        reason: str = SlashOption(
            name="reason", description="The reason of the kick", required=False
        ),
    ):
        kicked = Embed(
            color=Color.yellow(),
            title="Kicked!",
            description=f"{member.mention} was kicked from the server!",
        )
        if reason:
            kicked.add_field(name="Reason", value=reason)
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
            kicked.add_field(name="Reason", value=reason)
        kicked.set_author(
            name=self.client.user.display_name,
            icon_url=self.client.user.display_avatar,
        )
        kicked.set_footer(
            icon_url=interaction.user.display_avatar,
            text=f"Kicked by {interaction.user.name}",
        )
        kicked.set_thumbnail(url=interaction.guild.icon)
        await member.send(embed=kicked)

        # await member.kick(reason=reason)

    @slash_command(name="ban", description="To ban a member")
    async def ban(
        self,
        interaction: Interaction,
        member: Member = SlashOption(name="membre", description="The member to kick"),
        reason: str = SlashOption(
            name="reason", description="The reason of the kick", required=False
        ),
    ):
        banned = Embed(
            color=Color.red(),
            title="Banned!",
            description=f"{member.mention} was banned from the server!",
        )
        if reason:
            banned.add_field(name="Reason", value=reason)
        banned.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar,
        )
        banned.set_thumbnail(url=member.display_avatar)
        await interaction.send(embed=banned)

        banned = Embed(
            color=Color.yellow(),
            title="Banned!",
            description=f"You have been banned from the server: **{interaction.guild.name}**!",
        )
        if reason:
            banned.add_field(name="Reason", value=reason)
        banned.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar,
        )
        banned.set_thumbnail(url=interaction.guild.icon)
        await member.send(embed=banned)

        # await member.ban(reason=reason)

    @slash_command(name="unban", description="To unban a user")
    async def unban(
        self,
        interaction: Interaction,
        user: User = SlashOption(
            name="user", description="The user to unban", required=False
        ),
        reason: str = SlashOption(
            name="reason", description="The reason of the unban", required=False
        ),
    ):
        unbanned = Embed(
            color=Color.red(),
            title="Unbanned!",
            description=f"{user.mention} was unbanned from the server!",
        )
        if reason:
            unbanned.add_field(name="Reason", value=reason)
        unbanned.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar,
        )
        unbanned.set_thumbnail(url=user.display_avatar)
        await interaction.send(embed=unbanned)

        await interaction.guild.unban(user=user)

        unbanned = Embed(
            color=Color.yellow(),
            title="Unbanned!",
            description=f"You have been unbanned from the server: **{interaction.guild.name}**!",
        )
        if reason:
            unbanned.add_field(name="Reason", value=reason)
        unbanned.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar,
        )
        unbanned.set_thumbnail(url=interaction.guild.icon)
        await user.send(embed=unbanned)

    # @slash_command(name="", description="")
    # async def cmd(self, interaction: Interaction):
    #     return

    # @slash_command(name="", description="")
    # async def cmd(self, interaction: Interaction):
    #     return


def setup(client: Bot):
    client.add_cog(Moderation(client))
