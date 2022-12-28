import asyncio
from aiosqlite import Connection, Cursor

from nextcord.ext.commands import Cog, Bot
from numerize.numerize import numerize

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
    utils,
)

from datetime import timedelta, datetime


class Moderation(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client
        client.loop.create_task(self.connect_db())

    async def connect_db(self):
        self.db: Connection = self.client.db
        self.cursor: Cursor = await self.db.cursor()

    @application_checks.has_permissions(manage_messages=True)
    @slash_command(name="clear", description="To clear a channel")
    async def clear_channel(
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
        cleared.set_author(
            icon_url=interaction.user.avatar.url,
            name=interaction.user.name,
        )

        response = await interaction.followup.send(embed=cleared)

        await asyncio.sleep(5)
        if channel != interaction.channel:
            await clearing.delete()
        await response.delete()

    @application_checks.has_permissions(kick_members=True)
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
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar,
        )
        kicked.set_thumbnail(url=interaction.guild.icon)
        await member.send(embed=kicked)

        # await member.kick(reason=reason)

    @application_checks.has_permissions(ban_members=True)
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
            color=Color.red(),
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

    @application_checks.has_permissions(ban_members=True)
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
            color=Color.green(),
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

        # await interaction.guild.unban(user=user)

        unbanned = Embed(
            color=Color.green(),
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

    @application_checks.has_permissions(kick_members=True)
    @slash_command(name="mute", description="To timeout a user")
    async def mute(
        self,
        interaction: Interaction,
        member: Member = SlashOption(
            name="member", description="The member to timeout", required=True
        ),
        duration: int = SlashOption(
            name="duration", description="The duration of the timeout", required=True
        ),
        reason: str = SlashOption(
            name="reason", description="The reason of the timeout", required=False
        ),
    ):
        await member.edit(timeout=utils.utcnow() + timedelta(seconds=duration))

        muted = Embed(
            color=Color.yellow(),
            title="Muted!",
            description=f"{member.mention} was muted in the server!",
        )
        muted.add_field(name="Duration", value=f"{duration}s")
        if reason:
            muted.add_field(name="Reason", value=reason)
        muted.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar,
        )
        muted.set_thumbnail(url=member.display_avatar)
        await interaction.send(embed=muted)

        muted = Embed(
            color=Color.yellow(),
            title="Muted!",
            description=f"You have been muted from the server: **{interaction.guild.name}**!",
        )
        muted.add_field(name="Duration", value=f"{duration}s")
        if reason:
            muted.add_field(name="Reason", value=reason)
        muted.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar,
        )
        muted.set_thumbnail(url=interaction.guild.icon)
        await member.send(embed=muted)

    @application_checks.has_permissions(kick_members=True)
    @slash_command(name="unmute", description="To remove user's timeout")
    async def unmute(
        self,
        interaction: Interaction,
        member: Member = SlashOption(
            name="member", description="The member to timeout", required=True
        ),
        reason: str = SlashOption(
            name="reason", description="The reason of the timeout", required=False
        ),
    ):
        await member.edit(timeout=None)

        unmute = Embed(
            color=Color.green(),
            title="Unmuted!",
            description=f"{member.mention} was unmuted in the server!",
        )
        if reason:
            unmute.add_field(name="Reason", value=reason)
        unmute.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar,
        )
        unmute.set_thumbnail(url=member.display_avatar)
        await interaction.send(embed=unmute)

        unmute = Embed(
            color=Color.green(),
            title="Unmuted!",
            description=f"You have been unmuted from the server: **{interaction.guild.name}**!",
        )
        if reason:
            unmute.add_field(name="Reason", value=reason)
        unmute.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar,
        )
        unmute.set_thumbnail(url=interaction.guild.icon)
        await member.send(embed=unmute)


def setup(client: Bot):
    client.add_cog(Moderation(client))
