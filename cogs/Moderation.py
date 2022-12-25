import nextcord

from nextcord.ext.commands import Cog, Bot

from nextcord.ext import application_checks
from nextcord import (
    Button,
    ButtonStyle,
    Member,
    Colour,
    Embed,
    Interaction,
    Member,
    SelectOption,
    SlashOption,
    User,
    TextChannel,
    TextInputStyle,
    User,
    ui,
    utils,
    PartialInteractionMessage,
    slash_command,
)


class Moderation(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client

    @slash_command(name="whois", description="Get user infos")
    async def who_is(self, interaction: Interaction, member: Member):
        embed = Embed(
            title=member.name,
            description=member.mention,
            color=member.accent_colour if member.accent_colour else member.colour,
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
        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(client: Bot):
    client.add_cog(Moderation(client))
