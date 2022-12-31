from aiosqlite import Connection, Cursor
from nextcord.ext.commands import Bot, Cog

from nextcord import Member, Embed, Color


class Greetings(Cog):
    def __init__(self, client: Bot):
        self.client = client
        client.loop.create_task(self.connect_db())

    async def connect_db(self):
        self.db: Connection = self.client.db
        self.cursor: Cursor = await self.db.cursor()

    @Cog.listener()
    async def on_ready(self):
        return

    @Cog.listener()
    async def on_member_join(self, member: Member):
        if not member.bot:
            await self.cursor.execute(
                """SELECT greetingsChannelId FROM "configs" WHERE guildId = ?""",
                (member.guild.id,),
            )

            greetings_channel_id = await self.cursor.fetchone()

            if greetings_channel_id[0]:
                channel = member.guild.get_channel(greetings_channel_id[0])

                joined = Embed(
                    title="Welcome!",
                    description=f"{member.mention} has joined the server!",
                    color=Color.blue(),
                )
                joined.set_thumbnail(url=member.display_avatar)

                await channel.send(embed=joined)

    @Cog.listener()
    async def on_member_remove(self, member: Member):
        if not member.bot:

            await self.cursor.execute(
                """SELECT greetingsChannelId FROM "configs" WHERE guildId = ?""",
                (member.guild.id,),
            )

            greetings_channel_id = await self.cursor.fetchone()

            if greetings_channel_id[0]:
                channel = member.guild.get_channel(greetings_channel_id[0])

                left = Embed(
                    title="Goodbye!",
                    description=f"{member.mention} has left the server!",
                    color=0xFFA500,
                )
                left.set_thumbnail(url=member.display_avatar)

                await channel.send(embed=left)


def setup(client: Bot):
    client.add_cog(Greetings(client))
