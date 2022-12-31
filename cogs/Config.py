from aiosqlite import Connection, Cursor
from nextcord.ext.commands import Bot, Cog

from nextcord.ext import application_checks

from nextcord import slash_command, Embed, Color, Interaction, SlashOption, TextChannel


class Config(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client
        client.loop.create_task(self.connect_db())

    async def connect_db(self):
        self.db: Connection = self.client.db
        self.cursor: Cursor = await self.db.cursor()

    @Cog.listener()
    async def on_ready(self):
        await self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS "configs" (
                    "guildId"	INTEGER NOT NULL UNIQUE,
                    "greetingsChannelId"	INTEGER,
                    "levelsChannelId"	INTEGER,
                    "giveawaysChannelId"	INTEGER
                );"""
        )

        for guild in self.client.guilds:
            await self.cursor.execute(
                """SELECT * FROM "configs" WHERE guildId = ?""", (guild.id,)
            )

            config = await self.cursor.fetchone()

            if not config:
                await self.cursor.execute(
                    """INSERT INTO "configs" (guildId) VALUES (?)""", (guild.id,)
                )

            await self.db.commit()

    @slash_command(name="config", description="To config the bot")
    async def config(self, interaction: Interaction):
        return

    @config.subcommand(name="greetings")
    async def greetings(self, interaction: Interaction):
        return

    @application_checks.has_permissions(administrator=True)
    @greetings.subcommand(name="channel", description="Config greetings channel")
    async def greetings_channel(
        self,
        interaction: Interaction,
        channel: TextChannel = SlashOption(
            name="channel", description="The greetings channel", required=True
        ),
    ):

        await self.cursor.execute(
            """UPDATE "configs" SET greetingsChannelId = ? WHERE guildId = ?""",
            (channel.id, interaction.guild_id),
        )
        await self.db.commit()

        configured = Embed(
            title="Cofigured!",
            description=f"The greetings channel has been set to {channel.mention}",
            color=Color.green(),
        )
        configured.set_author(
            icon_url=interaction.user.avatar.url,
            name=interaction.user.name,
        )
        await interaction.send(embed=configured)

    @config.subcommand(name="levels")
    async def levels(self, interaction: Interaction):
        return

    @application_checks.has_permissions(administrator=True)
    @levels.subcommand(name="channel", description="Config levels channel")
    async def levels_channel(
        self,
        interaction: Interaction,
        channel: TextChannel = SlashOption(
            name="channel", description="The levels channel", required=True
        ),
    ):

        await self.cursor.execute(
            """UPDATE "configs" SET levelsChannelId = ? WHERE guildId = ?""",
            (channel.id, interaction.guild_id),
        )
        await self.db.commit()

        configured = Embed(
            title="Cofigured!",
            description=f"The levels channel has been set to {channel.mention}",
            color=Color.green(),
        )
        configured.set_author(
            icon_url=interaction.user.avatar.url,
            name=interaction.user.name,
        )
        await interaction.send(embed=configured)

    @config.subcommand(name="giveaways")
    async def giveaways(self, interaction: Interaction):
        return

    @application_checks.has_permissions(administrator=True)
    @giveaways.subcommand(name="channel", description="Config giveaways channel")
    async def giveaways_channel(
        self,
        interaction: Interaction,
        channel: TextChannel = SlashOption(
            name="channel", description="The giveaways channel", required=True
        ),
    ):

        await self.cursor.execute(
            """UPDATE "configs" SET giveawaysChannelId = ? WHERE guildId = ?""",
            (channel.id, interaction.guild_id),
        )
        await self.db.commit()

        configured = Embed(
            title="Cofigured!",
            description=f"The giveaways channel has been set to {channel.mention}",
            color=Color.green(),
        )
        configured.set_author(
            icon_url=interaction.user.avatar.url,
            name=interaction.user.name,
        )
        await interaction.send(embed=configured)


def setup(client: Bot):
    client.add_cog(Config(client))
