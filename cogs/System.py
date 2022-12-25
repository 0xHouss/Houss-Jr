from nextcord.ext.commands import Cog, Bot

from nextcord.ext import application_checks
from nextcord import (
    Embed,
    Interaction,
    slash_command,
)

class System(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client

    @slash_command(name="ping", description="Get bot's latency")
    async def ping(self, interaction: Interaction):
        embed = Embed(title=f"Bot's Ping")
        embed.add_field(name="My latency is:", value=f"{round(self.client.latency*1000)}ms")
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar.url)
        await interaction.send(embed=embed)

def setup(client: Bot):
    client.add_cog(System(client))