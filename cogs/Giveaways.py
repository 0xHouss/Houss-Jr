from datetime import datetime, timedelta

from nextcord.ext.commands import Cog, Bot

from nextcord.ext import application_checks
from nextcord.abc import GuildChannel
from nextcord import (
    Embed,
    Interaction,
    Member,
    SlashOption,
    Message,
    Color,
    slash_command,
)

import random
import asyncio


class Giveaways(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client

    @Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(2)
        curr = await self.client.db.cursor()
        await curr.execute(
            """CREATE TABLE IF NOT EXISTS "giveaways" (
                    "id"	INTEGER NOT NULL UNIQUE,
                    "channelId"	INTEGER NOT NULL,
                    "guildId"	INTEGER NOT NULL,
                    "numberOfWinners" INTEGER NOT NULL,
                    "winners"	TEXT NOT NULL,
                    "prize"	TEXT NOT NULL,
                    "start"  TIMESTAMP NOT NULL,
                    "end"  TIMESTAMP NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT)
                );"""
        )
        await self.client.db.commit()

    @slash_command(name="giveaway")
    async def giveaway(self, interaction: Interaction):
        return

    @application_checks.is_owner()
    @giveaway.subcommand(name="start", description="To start a giveaway")
    async def start(
        self,
        interaction: Interaction,
        duration: int = SlashOption(
            name="duration",
            description="The duration of the giveaway in seconds",
            required=True,
        ),
        winners_num: int = SlashOption(
            name="winners", description="The number of winners", required=True
        ),
        prize: str = SlashOption(
            name="prize", description="The prize to win", required=True
        ),
        channel: GuildChannel = SlashOption(
            name="channel",
            description="The channel where to start the giveaway",
            required=False,
        ),
    ):

        start = datetime.now()
        end = start + timedelta(seconds=duration)

        embed = Embed(
            title="There is a Giveaway!",
            description=f"React with the 🎉 emoji to try to win the prize",
            color=Color.green(),
        )
        embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar
        )
        embed.add_field(name="Prize: ", value=prize)
        embed.add_field(name="Number of winners: ", value=winners_num)
        embed.set_footer(text=f"Ends at {str(end).split('.')[0]}!")

        if not channel:
            channel = interaction.channel

        confirmation = Embed(
            title=f"Giveaway!",
            description=f"Giveaway started in {channel.mention}",
            color=Color.green(),
        )

        await interaction.response.send_message(embed=confirmation, ephemeral=True)

        giveaway: Message = await channel.send(embed=embed)
        await giveaway.add_reaction("🎉")

        await asyncio.sleep(duration)

        # refreshing message
        giveaway = await channel.fetch_message(giveaway.id)

        participants = await giveaway.reactions[0].users().flatten()
        participants.remove(self.client.user)

        winners: list[Member] = []

        for i in range(winners_num):
            if not len(participants):
                break

            winner = random.choice(participants)
            participants.remove(winner)
            winners.append(winner)

        end = Embed(
            title="Giveaway ended!",
            description="The winners are:",
            color=Color.green(),
        )

        end.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar
        )

        for i, winner in enumerate(winners):
            end.add_field(name=f"Winner {i+1}:", value=winner.mention)

        end.set_footer(text=f"They have won: {prize}")

        await channel.send(embed=end)

        curr = await self.client.db.cursor()
        await curr.execute(
            """INSERT INTO "giveaways" (channelId, guildId, numberOfWinners, winners, start, end) VALUES (?, ?, ?, ?, ?, ?);""",
            (
                channel.id,
                channel.guild.id,
                winners_num,
                ",".join([winner.id for winner in winners]),
                start,
                end,
            ),
        )

        await self.client.db.commit()

    @giveaway.subcommand(name="clear", description="Delete all giveaways")
    async def clear(
        self,
        interaction: Interaction,
        channel: GuildChannel = SlashOption(
            name="channel",
            description="The channel to clear it's giveaways",
            required=False,
        ),
    ):
        curr = await self.client.db.cursor()
        await curr.execute(
            f"""DELETE FROM "giveaways" WHERE guildId = ? {'AND channelId = ?' if channel else ''}""",
            (interaction.guild.id, channel.id) if channel else (interaction.guild.id,),
        )
        await self.client.db.commit()


def setup(client: Bot):
    client.add_cog(Giveaways(client))
