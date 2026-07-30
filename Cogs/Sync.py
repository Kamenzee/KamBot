#
# import discord
# from discord import app_commands
# from discord.ext import commands
# from dotenv import load_dotenv
# import os
#
# # MY_GUILD = self.bot.get_guild(651642217857024000)
# # print(f'My guild is {MY_GUILD}')
# # await self.bot.tree.sync(guild=MY_GUILD)
#
# load_dotenv()
# APP_OWNER_ID = int(os.getenv("APP_OWNER_ID"))
# APP_OWNER_GUILD_ID = int(os.getenv("APP_OWNER_GUILD_ID"))
#
#
# class Sync(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#
#     @app_commands.command(name='sync', description='Sync your stuff.')
#     async def sync(self, intr: discord.Interaction) -> None:
#         if intr.user.id != APP_OWNER_ID:
#             return
#         try:
#             await intr.response.defer()
#             await self.bot.tree.sync()
#             self.bot.logInfo(0, 0, 'Successfully synced Bot.')
#             await intr.response.send_message('Successfully synced bot.')
#         except Exception as e:
#             self.bot.logWarning(0, 0, f'Unable to sync bot: ', {str(e)})
#             await intr.response.send_message(f'Unable to sync bot: {e}')
#
#
#
# async def setup(bot):
#     await bot.add_cog(Sync(bot), guilds=[discord.Object(id=APP_OWNER_GUILD_ID)])
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
APP_OWNER_ID = int(os.getenv("APP_OWNER_ID"))
APP_OWNER_GUILD_ID = int(os.getenv("APP_OWNER_GUILD_ID"))


class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self._synced = False

    #Leaving this in just in case a manual re-sync is needed.  
    # @commands.Cog.listener()
    # async def on_ready(self):
    #     if not self._synced:  # simple guard so it only fires once per boot, not required
    #         await self.bot.tree.sync(guild=discord.Object(id=APP_OWNER_GUILD_ID))
    #         self._synced = True
    #         print(f'successfully synced {self.bot.user}')

    @app_commands.command(name='sync', description='Sync your stuff.')
    async def sync(self, intr: discord.Interaction) -> None:
        await intr.response.defer()
        if intr.user.id != APP_OWNER_ID:
            return
        try:
            await self.bot.tree.sync()
            self.bot.logInfo(0, 0, 'Successfully synced Bot for global scope.')
            await intr.followup.send('Successfully synced Bot for global scope.')
        except Exception as e:
            self.bot.logWarning(0, 0, f'Unable to sync bot for for global scope: {e}')
            await intr.followup.send(f'Unable to sync bot for for global scope, check logs for more information.')

        try:

            await self.bot.tree.sync(guild=discord.Object(id=APP_OWNER_GUILD_ID))
            self.bot.logInfo(0, 0, 'Successfully synced Bot for app owner guild.')
            await intr.followup.send('Successfully synced bot for app owner guild.')
        except Exception as e:
            self.bot.logWarning(0, 0, f'Unable to sync bot for app owner guild: {e}')
            await intr.followup.send(f'Unable to sync bot for app owner guild, check logs for more information.')


async def setup(bot):
    await bot.add_cog(Sync(bot), guilds=[discord.Object(id=APP_OWNER_GUILD_ID)])