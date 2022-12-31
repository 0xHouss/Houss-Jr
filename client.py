import asyncio
import os
import time
import nextcord

from os import environ as env

from nextcord import Intents, Interaction
from nextcord.ext.commands import Bot, errors, Context
from nextcord.ext.application_checks import errors as application_errors

import aiosqlite


class Client(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop.create_task(self.get_ready())

    async def get_ready(self):
        self.db = await aiosqlite.connect("main.db")

        self.load_extensions()

    def load_extensions(self) -> None:
        loaded = []
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                self.load_extension(f"cogs.{filename[:-3]}")
                print(f"system: {filename[:-3]} cog loaded.")
                loaded.append(filename[:-3])
        return loaded

    def unload_extensions(self) -> None:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                self.unload_extension(f"cogs.{filename[:-3]}")
                print(f"system: {filename[:-3]} cog loaded.")

    async def on_ready(self):
        print("Ready !")

    async def on_command_error(self, ctx: Context, error):
        if isinstance(error, errors.CommandNotFound):
            return
        elif isinstance(error, errors.TooManyArguments):
            await ctx.send("You are giving too many arguments!")
            return
        elif isinstance(error, errors.BadArgument):
            await ctx.send(
                "The library ran into an error attempting to parse your argument."
            )
            return
        elif isinstance(error, errors.MissingRequiredArgument):
            await ctx.send("You're missing a required argument.")

        # kinda annoying and useless error.
        elif isinstance(error, nextcord.NotFound) and "Unknown interaction" in str(
            error
        ):
            return
        elif isinstance(error, errors.MissingRole):
            role = ctx.guild.get_role(int(error.missing_role))
            await ctx.send(f'"{role.name}" is required to use this command.')
            return
        else:
            await ctx.send(
                f"This command raised an exception: `{type(error)}:{str(error)}`"
            )

    async def on_application_command_error(
        self, interaction: Interaction, error: Exception
    ) -> None:
        if isinstance(error, application_errors.ApplicationMissingRole):
            role = interaction.guild.get_role(int(error.missing_role))
            await interaction.send(
                f"The role {role.mention} is required to use this command.",
                ephemeral=True,
            )
            return

        elif isinstance(error, application_errors.ApplicationMissingPermissions):
            permissions = error.missing_permissions
            await interaction.send(
                f"the permission{'s' if len(permissions) > 1 else ''}: **{', '.join(permissions)}**. {'are' if len(permissions) > 1 else 'is'} required to use this command.",
                ephemeral=True,
            )
            return

        else:
            await interaction.send(
                f"The command has encountred an error: `{type(error)}:{str(error)}`",
                ephemeral=True,
            )


client = Client(
    "=", intents=Intents(messages=True, guilds=True, members=True, message_content=True)
)

if __name__ == "__main__":
    client.run(env["TOKEN"])
