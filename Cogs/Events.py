# Events.py

"""
This bot is currently designed to host a hangman game for multiple Discord guilds.  More games will be added
in the future.  This file forms the processes to run upon specific Discord events.
Author = Mackenzie Carter
Latest version = KamBotV1
Date = 08/18/2022

"""
import discord
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is connected to Discord!")



    # Defines the functions to complete when a guild adds the bot to the server
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Adds the guild information to the appropriate tables in the DB
        await self.bot.db.depositNewGuild(guild.id, guild.name)
        # Searches the roles in the guild to find the bot's role.
        for role in guild.roles:
            if role.name.lower() == "kambot":
                kambot_role = role
                break
        # Cycles through the channels in the guild to remove the bot from unnecessary ones.
        for cat in guild.channels:
            try:
                await cat.set_permissions(kambot_role, read_message_history=False,
                                          read_messages=False,
                                          send_messages=False,
                                          view_channel=False)
            except discord.Forbidden:
                pass
        # Creates a category for the game text channels to reside in
        kb_cat = await guild.create_category(name="KAMBOT", position=len(guild.by_category()))
        # Creates the text channels inside the category
        await guild.create_text_channel(name="KB-Hangman", category=kb_cat, position=0)
        await guild.create_text_channel(name="KB-Food-Fight", category=kb_cat, position=1)
        ab_channel = await guild.create_text_channel(name="KB-AlphaBot", category=kb_cat, position=2)

        await self.bot.db.depositNewABGuild(guild.id, ab_channel.id)
        await self.bot.db.depositNewHMGuild(guild.id)


    # This event listener is run when a guild removes KamBot from their server
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        guild_id = guild.id
        try:
            # This removes the guild from the master guild table, most others delete automatically.
            await self.removeGuild(guild_id)
            self.bot.logInfo(0, guild_id, f'Removed guild {guild.name}')
        except Exception as e:
            self.bot.logWarning(0, guild_id,
                                f'Guild <{guild.name}> was unable to be removed due to the following error: ', str(e))


    async def removeGuild(self, guild_id) -> None:
        ab = self.bot.get_cog('AlphaBot')
        ab.removeABGuild(guild_id)

        ff = self.bot.get_cog('FoodFight')
        ff.removeFFGuild(guild_id)

        hm = self.bot.get_cog('Hangman')
        hm.removeHMGuild(guild_id)

        await self.bot.db.removeHMGuild(guild_id)

    @commands.Cog.listener()
    async def on_member_remove(self, member : discord.Member):
        user_id = member.id
        guild_id = member.guild.id
        try:
            await self.removeUser(user_id, guild_id)
            self.bot.logInfo(user_id, guild_id, f'Removed user {user_id}')
        except Exception as e:
            self.bot.logWarning(user_id, guild_id, f'Failed to remove user: {str(e)}')

    async def removeUser(self, user_id : int, guild_id : int) -> None:
        ff = self.bot.get_cog('FoodFight')
        ff.removeFFUser(user_id, guild_id)

        hm = self.bot.get_cog('Hangman')
        hm.removeHMUser(user_id, guild_id)

        await self.bot.db.removeUser(user_id, guild_id)


async def setup(bot):
    await bot.add_cog(Events(bot))
