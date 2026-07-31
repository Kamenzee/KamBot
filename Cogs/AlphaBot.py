# AlphaBot.py

import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
from Classes.AlphaBotHelpers import AlphaBotGuild

"""
This Cog/Class is a game designed to allow users to cycle through letters to reach the highest letter sequence that 
they can.

Add high score, highest correct guesser ID, highest MesserUpper ID, Number value of letter sequence.


Author = Mackenzie Carter
Latest version = KamBotV1.1
Latest Update = 07/31/2026
"""


# ************************************** Start Up/Routine Procedures ***************************************************

class AlphaBot(commands.Cog):
    def __init__(self, bot: commands.Bot, /) -> None:
        self.bot: commands.Bot = bot
        self.ab_guilds = {}

    # Defines a function to run when the Cog is loaded with the bot
    async def cog_load(self) -> None:
        guilds = await self.bot.db.fetchABGuildData()
        for guild in guilds:
            self.addGuildToABGuilds(guild)
        self.updateGuildInt10Mins.start()
        await self.startup()

    def addGuildToABGuilds(self, guild):
        self.ab_guilds[guild[0]] = AlphaBotGuild(guild[0], guild[1], guild[2], guild[3], guild[4], guild[5],
                                                 guild[6], guild[7], guild[8], guild[9], guild[10])

    async def getGuildsFromDB(self):
        async with self.bot.pool.acquire() as conn:
            guilds = await conn.fetch("""
            SELECT * FROM guild_ab_stats;
            """)
        return guilds

    @app_commands.command(name='abhelp', description='Get a full description of AlphaBot!')
    async def abhelp(self, intr: discord.Interaction) -> None:
        await intr.response.send_message("""
AlphaBot is a game that tests your alphabetical skills.

Much like numbers, letters can also be used to count.  However, instead of using a base 10 numbering system like 
the one we're used to, it turns into a base 26 numbering system.

This means that instead of repeating 10 digits (0-9), 26 characters are repeated to create a numbering system (A-Z).

To count using letters, we being with the letter "A" and cycle all the way through to "Z".  What do we do next?  
It's simple!  We add another character!

Just like we do when counting numbers, once we reach the last character, we cycle back around and indicate the 
number of cycles completed with the first digit.

After "Z" we begin a second cycle with "AA".  The letter furthest to the right is the one that is singly 
incremented per turn.  After each cycle of the alphabet on the last letter, the letter on the left gets 
incremented by one.

For example: "A" "B" "C" ... "Y" "Z" "AA" "AB" "AC" ... "AZ" "BA" ... "ZY" "ZZ" "AAA" "AAB" AAC" and so on.  

Once a game is started with the "k.abc" command, the bot begins listening in the same channel for letter 
sequences. This means ANY message that is only text will be read by the bot and counted as a turn.

To prevent accidentally messing up a turn, make sure to include a number or punctuation.

AlphaBot is as simple as that!

***CAN YOU REACH THE END?***
    """)

    # Defines the generic instructions for the hm commands.
    async def ab(self, ctx):
        response = "Please type 'k.help ab' for detailed instructions or 'k.abc' to begin a game."
        await ctx.send(response)

    # Creates a task that runs in the background at a regular interval, in this case every 10 minutes the current values
    # are updated in the DB if necessary
    @tasks.loop(minutes=10)
    async def updateGuildInt10Mins(self):
        try:
            ab_guilds = self.ab_guilds
            for ab_guild in ab_guilds:
                guild = ab_guilds.get(ab_guild)
                await self.bot.db.depositABGuildData(guild)
            self.bot.logInfo(0, 0, 'Successfully updated ABGuilds.')
        except Exception as e:
            self.bot.logWarning(0, 0, f'Unable to update ABGuilds due to the following error: {str(e)}')



    # Defines a startup procedure that checks whether a game was started on the latest DB deposit.
    async def startup(self):
        for guild in self.ab_guilds:
            if self.ab_guilds.get(guild).gameOn():
                self.ab_guilds.get(guild).setGameOff()

    # ************************************ Commands/Main Procedures ***************************************************

    @app_commands.command(name="abstart",
                          description="Begin to learn your ABC's.")
    async def abstart(self, interaction: discord.Interaction) -> None:
        await self.userGameChecks(interaction.user.id, interaction.guild, interaction.channel)
        guild_id = interaction.guild.id
        ab_guild = self.getABGuild(guild_id)
        await interaction.response.send_message(f'Starting AlphaBot...')
        if not await self.passStartNewGameChecks(interaction.user, interaction.channel, ab_guild):
            return
        else:
            ab_guild.startNewGame()
            await interaction.channel.send(
                f"A game of AlphaBot has started.  ANY message in this channel past this point will be evaluated for "
                f"the game.  Typing anything but the next letter may result in a loss.  Good luck!")

    @app_commands.command(name="absave",
                          description="Bookmark your progress!")
    async def save_point(self, interaction: discord.Interaction):
        await self.userGameChecks(interaction.user.id, interaction.guild, interaction.channel)
        guild_stats = self.ab_guilds[interaction.guild.id]
        await interaction.response.send_message('Saving Progress...')
        if guild_stats.getSavepointVal() != -1:
            message = await interaction.channel.send(
                f"The current savepoint_seq is at \"{guild_stats.getSavepointSeq()}\", are you sure you want to "
                f"purchase the savepoint_seq at \"{guild_stats.getLastLetterSeq()}\"?")
        else:
            message = await interaction.channel.send(
                f"Are you sure you want to set a save point for {interaction.guild.name} at the sequence "
                f"\"{guild_stats.getLastLetterSeq()}\" for 15 KamKoins?")
        save_yn = await self.confirmChange(interaction.user, message)
        if save_yn:
            points = self.getUserPoints(interaction.user.id, interaction.guild.id)
            if points < 15:
                await interaction.channel.send(f"You don't have enough KamKoins to buy a savepoint.  Add some more letters to get "
                               f"more!")
                return
            guild_stats.updateSavepoint(guild_stats.getLastLetterSeq(), guild_stats.getLetterValue())
            self.buySave(interaction.user.id, interaction.guild.id)
            name = self.getDiscUserName(interaction.user)
            await interaction.channel.send(f"{name} was kind enough to bookmark the place!  WORSHIP THEIR KINDNESS!")
        else:
            await interaction.channel.send(f"A savepoint was not purchased.")
        return

    @app_commands.command(name="abstats",
                          description="Show your progress!")
    async def abstats(self, intr: discord.Interaction) -> None:
        guild_id = intr.guild.id
        await self.userGameChecks(intr.user.id, intr.guild, intr.channel)
        guild = self.getABGuild(guild_id)
        stats_embed = discord.Embed(title=f"{intr.guild.name}'s AlphaBot Stats")
        stats_embed = self.buildABStatEmbed(stats_embed, guild)
        await intr.response.send_message(embed=stats_embed)

    def buildABStatEmbed(self, stats_embed: discord.Embed, guild: AlphaBotGuild) -> discord.Embed:
        stats_embed.add_field(name=f"Current Letter Sequence", value=f"{guild.getLastLetterSeq()}", inline=False)
        stats_embed.add_field(name=f"Current Letter Sequence Value", value=f"{guild.getLetterValue()}", inline=False)
        stats_embed.add_field(name=f"Record Sequence", value=f"{guild.getRecordSeq()}", inline=False)
        stats_embed.add_field(name=f"Record Sequence Value", value=f"{guild.getRecordValue()}", inline=False)
        stats_embed.add_field(name=f"Record Holder", value=f"<@!{guild.getRecordHolder()}>", inline=False)
        return stats_embed

    @commands.Cog.listener('on_message')
    async def alphabot_message(self, message):
        if self.evaluatableMessage(message):
            await self.userGameChecks(message.author.id, message.guild, message.channel)
            ab_guild = self.getABGuild(message.guild.id)
            await self.runGameChecks(ab_guild, message)


    # *********************************** Abstraction/Helper functions *************************************************

    async def userGameChecks(self, player_id: int, guild: discord.Guild, channel : discord.TextChannel) -> None:
        if guild.id not in self.ab_guilds:
            await self.bot.addNewGuild(guild)
            await self.bot.db.depositNewABGuild(guild.id, channel.id)
        if self.getUserKey(player_id, guild.id) not in self.bot.kambot_users:
            await self.bot.addNewKamBotUser(player_id, guild.id, 75)




    async def passStartNewGameChecks(self, user: discord.Member, channel: discord.TextChannel,
                                     ab_guild: AlphaBotGuild) -> bool:
        user_is_admin = user.guild_permissions.administrator
        if not ab_guild.abChannelSet() and not user_is_admin:
            await channel.send(f"A channel for AlphaBot has not been set. Please ask a server administrator to "
                                       f"set the channel by running the command \"/abstart\" in the desired channel.")
            return False
        if not ab_guild.abChannelMatch(channel.id) and not user_is_admin:
            await channel.send(
                f"A channel is already assigned for AlphaBot, try again there!  If it needs to move, ask an "
                f"administrator to run the command \"/abstart\" in the desired channel.")
            return False
        if not ab_guild.abChannelSet() and user_is_admin:
            set_channel_message = await channel.send(
                f"Do you want to set the AlphaBot channel to {channel.mention} "
                f"and begin a game?")
            return await self.changeChannelOption(user, ab_guild, set_channel_message)
        if not ab_guild.abChannelMatch(channel.id) and user_is_admin:
            change_channel_message = await channel.send(f"Do you want to change the AlphaBot channel to "
                                                                f"{channel.mention} and begin a game?")
            return await self.changeChannelOption(user, ab_guild, change_channel_message)
        if ab_guild.abChannelMatch(channel.id) and ab_guild.getLastLetterSeq() != '':
            ab_guild.resetGame()
            self.updateGuildInABGuilds(ab_guild)
            await channel.send(
                f"Uh oh!  It looks like the KamBot servers might have had some issues and lost some info!  "
                f"The last letter sequence is \"{ab_guild.getLastLetterSeq()}\".  The game has started, "
                f"begin with the next sequence!  Good Luck!")
            return False
        if ab_guild.abChannelMatch(channel.id) and ab_guild.getSavepointVal() != -1:
            resume = await channel.send(
                f"Would you like to resume the game from the last save point?  This will start the "
                f"game at the sequence '{ab_guild.getSavepointSeq()}'.")
            return await self.resumeGame(user, ab_guild, resume)
        if ab_guild.abChannelMatch(channel.id):
            return True

    def getABGuild(self, guild_id) -> AlphaBotGuild:
        if self.ab_guilds.get(guild_id) is None:
            self.ab_guilds[guild_id] = AlphaBotGuild(guild_id, 0, "", False, 0, "", "", -1)
        return self.ab_guilds.get(guild_id)

    async def changeChannelOption(self, author, guild, change_channel_message) -> bool:
        channel = change_channel_message.channel
        ch_ch_yn = await self.confirmChange(author, change_channel_message)
        if ch_ch_yn:
            await guild.setGuildABChannel(channel.id)
            self.updateGuildInABGuilds(guild)
            return True
        elif not ch_ch_yn:
            await channel.send(f"The AlphaBot channel was not changed and a game was not started.")
            return False

    async def resumeGame(self, author, guild, resume_message) -> bool:
        channel = resume_message.channel
        resume_yn = await self.confirmChange(author, resume_message)
        if resume_yn:
            guild.resetFromSave()
            self.updateGuildInABGuilds(guild)
            await channel.send(
                f"A game of AlphaBot has started with the sequence '{guild.getLastLetterSeq()}'.  "
                f"ANY message in this channel past this point will be evaluated for the game.  Typing anything but "
                f"the next letter sequence may result in a loss.  Good luck!")
            return False
        else:
            return True

    async def confirmChange(self, author: discord.Member, message: discord.Message):
        confirmation = False
        con_deny = ["\U00002705", "\U0000274E"]
        for react in con_deny:
            await message.add_reaction(react)

        def check(reaction, user):
            return user == author and str(reaction.emoji) in con_deny and reaction.message == message
        try:
            confirmation = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            for r in con_deny:
                await message.clear_reaction(r)
        try:
            emoji = confirmation[0]
        except UnboundLocalError:
            emoji = None
        if str(emoji) == "\U0000274E":
            return False
        elif str(emoji) == "\U00002705":
            return True

    def evaluatableMessage(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return False
        ab_guild = self.getABGuild(message.guild.id)
        if message.channel.id != ab_guild.getChannelId():
            return False
        if not ab_guild.gameOn():
            return False
        message_content = message.content.upper()
        if not message_content.isalpha():
            return False
        if "k." in message_content or "K." in message_content:
            return False
        if message.channel.id == ab_guild.getChannelId() and ab_guild.gameOn():
            return True
        return False

    async def runGameChecks(self, ab_guild, message: discord.Message):
        letter_seq = message.content.upper()
        if await self.doubleGuess(message.author.id, ab_guild, message.channel):
            return
        elif not await self.letterSeqPass(letter_seq, ab_guild, message.author.id, message.channel):
            return
        else:
            self.continueGame(ab_guild, message.author.id, letter_seq)
            await message.add_reaction("\U00002705")
            return

    async def doubleGuess(self, player_id: int, ab_guild: AlphaBotGuild,
                          channel: discord.TextChannel):
        if player_id == ab_guild.getLastAcceptedMember():
            await channel.send(f"<@!{player_id}> MESSED IT UP!  HOW DARE THEY TRY AND ANSWER TWICE IN "
                               f"A ROW!  WHAT SORT OF HACK GAME DO THEY THINK THIS IS?")
            self.endGame(ab_guild)
            return True
        return False

    def endGame(self, ab_guild: AlphaBotGuild):
        ab_guild.endGame()
        self.updateGuildInABGuilds(ab_guild)

    def continueGame(self, ab_guild: AlphaBotGuild, player_id, letter_seq):
        ab_guild.increaseTurn(player_id, letter_seq)
        self.incrementPlayerPoints(player_id, ab_guild.getGuildId())
        self.updateGuildInABGuilds(ab_guild)

    def incrementPlayerPoints(self, player_id, guild_id):
        self.bot.kambot_users.get(int(f"{player_id}{guild_id}")).increasePoints(1)

    async def letterSeqPass(self, letter_seq: str, ab_guild: AlphaBotGuild, player_id, channel) -> bool:
        letters_val = self.getLettersValue(letter_seq)
        if letters_val == (ab_guild.getLetterValue() + 1):
            return True
        else:
            self.endGame(ab_guild)
            await channel.send(f"<@!{player_id}> MESSED IT UP!  HAHAHAHA LAUGH AT THEM EVERYONE!!!")
            return False

    def getUserPoints(self, player_id, guild_id):
        user_key = self.getUserKey(player_id, guild_id)
        return self.bot.kambot_users.get(user_key).getUserPoints()

    def buySave(self, player_id, guild_id):
        user_key = self.getUserKey(player_id, guild_id)
        self.bot.kambot_users.get(user_key).decreasePoints(15)

    def getUserKey(self, player_id, guild_id):
        return int(f"{player_id}{guild_id}")

    def getLettersValue(self, letter: str):
        if len(letter) == 1:
            return self.getLetterVal(letter)
        else:
            letters = []
            for let in letter:
                letters.append(let)
            alphabet_iteration = len(letters) - 1
            current_letter = letters.pop(0)
            remaining_letters = ''.join(letters)
            return (self.getTotalCurrentValue(current_letter, alphabet_iteration) +
                    self.getLettersValue(remaining_letters))

    def getLetterVal(self, letter):
        return ord(letter) - 64

    def getAlphabetIterationValue(self, alphabet_iteration):
        return 26 ** alphabet_iteration

    def getTotalCurrentValue(self, letter, alpha_iter):
        return self.getLetterVal(letter) * self.getAlphabetIterationValue(alpha_iter)

    def updateGuildInABGuilds(self, ab_guild: AlphaBotGuild):
        self.ab_guilds[ab_guild.getGuildId()] = ab_guild

    def getDiscUserName(self, disc_user: discord.Member) -> str:
        if disc_user.nick is None:
            return disc_user.name
        else:
            return disc_user.nick

    def removeABGuild(self, guild_id):
        if guild_id in self.ab_guilds:
            del self.ab_guilds[guild_id]


async def setup(bot):
    await bot.add_cog(AlphaBot(bot))

