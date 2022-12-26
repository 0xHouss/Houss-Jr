import asyncio

from nextcord.ext.commands import Cog, Bot

from nextcord.abc import GuildChannel
from nextcord.ext import application_checks
from nextcord import (
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

    @application_checks.is_owner()
    @slash_command(name="who")
    async def who(self, interaction: Interaction):
        return

    @who.subcommand(name="is", description="Get user's infos")
    async def who_is(self, interaction: Interaction, member: Member):
        embed = Embed(
            title=member.name,
            description=member.mention,
            color=member.accent_color if member.accent_color else member.color,
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

    @application_checks.is_owner()
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

        if not channel: channel = interaction.channel

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


def setup(client: Bot):
    client.add_cog(Moderation(client))
