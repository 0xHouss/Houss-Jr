from datetime import datetime, timedelta
from aiosqlite import Connection, Cursor

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
        client.loop.create_task(self.connect_db())

    async def connect_db(self):
        self.db: Connection = self.client.db
        self.cursor: Cursor = await self.db.cursor()

    @Cog.listener()
    async def on_ready(self):

        await self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS "giveaways" (
                    "id"	INTEGER NOT NULL UNIQUE,
                    "channelId"	INTEGER NOT NULL,
                    "guildId"	INTEGER NOT NULL,
                    "authorId"  INTEGER NOT NULL,
                    "winners"	TEXT NOT NULL,
                    "prize"	TEXT NOT NULL,
                    "start"  TIMESTAMP NOT NULL,
                    "end"  TIMESTAMP NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT)
                );"""
        )

    @slash_command(name="giveaway")
    async def giveaway(self, interaction: Interaction):
        return

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
        embed.set_footer(text=f"Ends the {end.strftime('%d/%m/%Y at %H:%M:%S')}!")

        
        if not channel:
            await self.cursor.execute("""SELECT giveawaysChannelId FROM "configs" WHERE guildId = ?""", (interaction.guild_id,))

            giveaways_channel_id = await self.cursor.fetchone()

            if giveaways_channel_id[0]:
                channel = interaction.guild.get_channel(giveaways_channel_id[0])
            else:
                channel = interaction.channel


        confirmation = Embed(
            title=f"Giveaway!",
            description=f"Giveaway started in {channel.mention}",
            color=Color.blue(),
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

        ended = Embed(
            title="Giveaway ended!",
            description="The winners are:",
            color=Color.blue(),
        )

        ended.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar
        )

        for i, winner in enumerate(winners):
            ended.add_field(name=f"Winner {i+1}:", value=winner.mention)

        ended.set_footer(text=f"They have won: {prize}")

        await channel.send(embed=ended)
        
        await self.cursor.execute(
            """INSERT INTO "giveaways" (channelId, guildId, authorId, winners, prize, start, end) VALUES (?, ?, ?, ?, ?, ?, ?);""",
            (
                channel.id,
                channel.guild.id,
                interaction.user.id,
                ",".join([str(winner.id) for winner in winners]) if winners else "",
                prize,
                start,
                end,
            ),
        )

        await self.db.commit()

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
        
        await self.cursor.execute(
            f"""SELECT * FROM "giveaways" WHERE guildId = ? {'AND channelId = ?' if channel else ''}""",
            (interaction.guild.id, channel.id) if channel else (interaction.guild.id,),
        )

        giveaways = await self.cursor.fetchall()

        if giveaways:
            await self.cursor.execute(
                f"""DELETE FROM "giveaways" WHERE guildId = ? {'AND channelId = ?' if channel else ''}""",
                (interaction.guild.id, channel.id)
                if channel
                else (interaction.guild.id,),
            )
            await self.db.commit()

            cleared = Embed(
                color=Color.green(),
                title="Giveaways cleared!",
                description=f"{f'{channel.mention} g' if channel else 'G'}iveaways have been cleared!",
            )
            cleared.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.display_avatar,
            )
            cleared.set_thumbnail(url=interaction.guild.icon)
            await interaction.send(embed=cleared)
        else:
            no_giveaways = Embed(
                color=Color.red(),
                title="No giveaways!",
                description=f"No giveaways have been started{f' in {channel.mention}' if channel else ''}!",
            )
            no_giveaways.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            await interaction.response.send_message(embed=no_giveaways, ephemeral=True)

    @giveaway.subcommand(name="list", description="List giveaways")
    async def list(
        self,
        interaction: Interaction,
        channel: GuildChannel = SlashOption(
            name="channel",
            description="The channel to list it's giveaways",
            required=False,
        ),
    ):
        
        await self.cursor.execute(
            f"""SELECT * FROM "giveaways" WHERE guildId = ? {'AND channelId = ?' if channel else ''}""",
            (interaction.guild.id, channel.id) if channel else (interaction.guild.id,),
        )

        giveaways = await self.cursor.fetchall()

        if giveaways:
            giveaways_list = Embed(
                color=Color.green(),
                title=f"{channel.name if channel else'Guild'} Giveaways",
                description=f"{channel.mention if channel else interaction.guild.name} giveaways:",
            )
            for (
                id,
                channelId,
                guildId,
                authorId,
                winners,
                prize,
                start,
                end,
            ) in giveaways:
                parser = lambda x: datetime.strptime(
                    x, "%Y-%m-%d %H:%M:%S.%f"
                ).strftime("%d/%m/%Y at %H:%M:%S")

                giveaways_list.add_field(
                    name=f"Giveaway {id}",
                    value=f"""
                    From {parser(start)} to {parser(end)}
                    By: {interaction.guild.get_member(authorId).mention}
                    Winners: {', '.join([interaction.guild.get_member(int(winner)).mention for winner in winners.split(',')])}
                    Prize: {prize}""",
                    inline=False,
                )

            giveaways_list.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.display_avatar,
            )
            giveaways_list.set_thumbnail(url=interaction.guild.icon)
            await interaction.send(embed=giveaways_list)

        else:
            no_giveaways = Embed(
                color=Color.red(),
                title="No giveaways!",
                description=f"No giveaways have been started{f' in {channel.mention}' if channel else ''}!",
            )
            no_giveaways.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            await interaction.response.send_message(embed=no_giveaways, ephemeral=True)

        await self.db.commit()

    @giveaway.subcommand(name="remove", description="Remove a user's warning")
    async def remove(
        self,
        interaction: Interaction,
        id: int = SlashOption(
            name="id",
            description="The id of the giveaway to remove (use /giveaway list to see the giveaways",
            required=True,
        ),
    ):
        
        await self.cursor.execute(
            """SELECT * FROM "giveaways" WHERE id = ?""",
            (id,),
        )

        giveaways = await self.cursor.fetchall()
        if giveaways:
            await self.cursor.execute(
                """DELETE FROM "giveaways" WHERE id = ?""",
                (id,),
            )

            deleted = Embed(
                color=Color.green(),
                title="Giveaway Deleted!",
                description=f"Giveaway {id} has been deleted!",
            )
            deleted.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.display_avatar,
            )
            deleted.set_thumbnail(url=interaction.guild.icon)
            await interaction.send(embed=deleted)
        else:
            no_warnings = Embed(
                color=Color.red(),
                title="No Giveaway!",
                description=f"No giveaway with id: {id}!",
            )
            no_warnings.set_author(
                name=self.client.user.display_name,
                icon_url=self.client.user.display_avatar,
            )
            no_warnings.set_thumbnail(url=interaction.guild.icon)
            await interaction.response.send_message(embed=no_warnings, ephemeral=True)

        await self.db.commit()


def setup(client: Bot):
    client.add_cog(Giveaways(client))
