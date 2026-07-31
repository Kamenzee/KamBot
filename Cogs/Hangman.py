# Hangman.py

"""
This Cog is a game of hangman designed for use within Discord servers/guilds.

Author = Mackenzie Carter
Latest version = KamBotV1
Date = 08/18/2022

To Do List:
1. Get custom word list if guild has it, if not, draw from default word list.
2. Rest of game.

"""

# Importing the modules needed for functionality
import asyncio
import discord
from discord.ext import commands, tasks
from discord import app_commands
import os.path
import shutil
from Classes.HangmanHelpers import *



class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_manager = HMGameManager()

    async def cog_load(self):
        await self.cacheGuilds()
        await self.cacheUsersStats()
        self.depositGames.start()

    @tasks.loop(minutes=10)
    async def depositGames(self):
        games_list = self.game_manager.getGuildsForDeposit()
        user_list = self.game_manager.getUsersForDeposit()
        try:
            await self.bot.db.depositBulkHMGuildData(games_list)
            self.bot.logInfo(0, 0, f'Hangman guild stats were successfully updated.')
        except Exception as e:
            self.bot.logWarning(0, 0,
                                f'Hangman guild stats were unable to be updated due to the following error: ', str(e))
        try:
            await self.bot.db.depositBulkHMUserData(user_list)
            self.bot.logInfo(0, 0, f'Hangman user stats were successfully updated.')
        except Exception as e:
            self.bot.logWarning(0, 0,
                                f'Hangman user stats were unable to be updated due to the following error: ', str(e))


    async def cacheGuilds(self):
        guilds = await self.bot.db.fetchHangmanGuildData()
        self.cacheGuildGames(guilds)
        self.cacheGuildStats(guilds)

    def cacheGuildGames(self, guilds: list) -> None:
        for guild in guilds:
            self.game_manager.storeGame(guild)

    def cacheGuildStats(self, guilds: list) -> None:
        for guild in guilds:
            self.game_manager.hm_stats.storeGuildStats(guild)

    async def cacheUsersStats(self):
        users = await self.bot.db.fetchHangmanUserData()
        for user in users:
            self.game_manager.hm_stats.storeUserStats(user)

    @app_commands.command(name='hmhelp', description='Get the Hangman rules.')
    async def hmHelp(self, intr: discord.Interaction) -> None:
        await intr.response.send_message("""
Hangman is a game in which random word is selected from a predefined and editable list.

You can use /hmstart <difficulty> to begin a game.

The words are separated and defined by their usage of common (such as e, a, r) or uncommon (such as x, q, z) letters, 
how often they are used in daily language and general obscurity. 

Once a game has begun, guess letters and words using the command /hmguess <guess>.  For example, "/hmguess x" to guess the letter "x" 
and "/hmguess hangman" to guess the word "hangman".

You have 7 chances to guess a letter in the word.  Each incorrect guess takes away 1 
chance and adds a piece of the hangman.  Once the hangman is fully pieced together and... well, no longer with us the game is over.

You get one KamKoin for every letter guessed in an easy game and two KamKoins for every letter guessed in a hard game.

When correctly guessing a word you are awarded with a KamKoin for every blank space plus a modifier for difficulty, so don't forget
 to guess words, too!  They don't take but one turn, but do not give any advantage on known letters.

Feeling nervous for the poor hangman?  You can bribe the officials to get back an extra turn for 15 KamKoins using /hmbuy.

If you need to stop a game before it is finished you may use the command "/hmstop" to end an ongoing game.

To view the server and user stats you can use "/hmstats".

To view the current available words you can run "/hmlist" and you will be greeted with the contents of both word 
lists!

If you have admin capabilities on the server, you can also add or remove words from your server's word lists!  All 
you need to do is specify the difficulty and word.

To add a word run the command "/hmadd-word <difficulty> <word>". I.E. "/hmadd-word hard bologna" will add "bologna" to the 
hard word list.

To remove a word run the command "/hmremove-word <difficulty> <word>" I.E. "/hmremove-word easy cat" will remove "cat" from the 
easy word list if it is there.  

**Can you save the hangman?***
""")
    # Defines the generic instructions for the hm commands.
    async def hm(self, ctx):
        response = "Please type k.help hm for detailed instructions or 'k.hm e'/'k.hm h' to begin a game."
        await ctx.send(response)

    @app_commands.command(name="hmstart",
                          description="Begins a game of hangman with the specified difficulty.")
    @app_commands.choices(difficulty=[
            app_commands.Choice(name="Easy", value="easy"),
            app_commands.Choice(name="Hard", value="hard")
        ])
    async def startHangman(self, intr: discord.Interaction, difficulty: app_commands.Choice[str]) -> None:
        guild_id = intr.guild.id
        await self.userAndGameChecks(intr.user.id, intr.guild)
        if not await self.startGameChecks(intr, guild_id, difficulty.value):
            return
        else:
            await self.startGame(guild_id, intr, 1 if difficulty.value == 'hard' else 0, intr.user.id)

    async def createUserIfNeeded(self, player_id: int, guild_id: int) -> None:
        user_key = int(f'{player_id}{guild_id}')
        if user_key not in self.game_manager.hm_stats.hm_user_stats:
            await self.bot.addNewKamBotUser(player_id, guild_id)
            await self.bot.db.depositNewHMUser(player_id, guild_id)
            self.game_manager.hm_stats.hm_user_stats[user_key] = HMUserStats(player_id, guild_id)



    async def userAndGameChecks(self, player_id : int, guild : discord.Guild) -> None:
        await self.createGuildIfNeeded(guild)
        await self.createUserIfNeeded(player_id, guild.id)


    async def createGuildIfNeeded(self, guild : discord.Guild) -> None:
        guild_id = guild.id
        if guild_id not in self.game_manager.hm_games:
            await self.bot.addNewGuild(guild)
            await self.bot.db.depositNewHMGuild(guild_id)
            self.game_manager.hm_games[guild_id] = HMGuildGame(guild_id)
            self.game_manager.hm_stats.hm_guild_stats[guild_id] = HMGuildStats(guild_id)





    async def startGame(self, guild_id: int, intr: discord.Interaction,
                        difficulty: int, starter_id: int):
        self.game_manager.startGame(guild_id, difficulty, starter_id)
        await self.startGameMessage(intr)
        print(self.game_manager.getGuildGame(guild_id).getGameWord())

    async def startGameMessage(self, intr: discord.Interaction) -> None:
        guild = self.game_manager.getGuildGame(intr.guild.id)
        first_turn_embed = self.createGallowsEmbed(guild)
        await intr.response.send_message(f"A game of hangman has started!  Can " + f"<@!{guild.getStarter()}>" + " and the rest of " +
                        str(intr.guild) + " save the hangman?")
        await intr.channel.send(file=self.gallowImg(guild.getGameTurn()), embed=first_turn_embed)

    def createGallowsEmbed(self, guild: HMGuildGame) -> discord.Embed:
        gallows = discord.Embed(title="The Gallows")
        gallows.set_image(url=f"attachment://image{guild.getGameTurn()}.jpg")
        gallows.add_field(name="\u200b", value="Your word has " + str(len(guild.getGameWord())) + " letters.",
                         inline=False)
        if guild.getGuessedLetters() != "":
            gallows.add_field(name="Guessed Letters", value=guild.getFormattedGuessedLetters())
        gallows.add_field(name="\u200b", value=f"\u200b{guild.getBlankSpaces()}", inline=False)
        gallows.add_field(name="\u200b", value="Please guess a letter.", inline=False)
        return gallows

    def gallowImg(self, guess_number):
        gallows_img = discord.File(f"KamBotFiles/Hangman{guess_number}.jpg", filename=f"image{guess_number}.jpg")
        return gallows_img

    async def startGameChecks(self, intr: discord.Interaction, guild_id: int, difficulty: str = 'Easy') -> bool:
        if not self.acceptedDifficulty(difficulty):
            await intr.response.send_message(f"Something went wrong!  Please select a difficulty from the start game menu")
            return False
        if self.game_manager.gameIsActive(guild_id):
            await intr.response.send_message(f"A game is already started.  Please finish it or run the command '/hmstop' to end it "
                           f"before starting a new game.")
            return False
        return True

    def acceptedDifficulty(self, difficulty: str):
        if difficulty == 'hard' or difficulty == 'easy':
            return True
        return False



    # A command is initiated when the prefix and command name are combined and sent as a message in Discord.
    @app_commands.command(name="hmguess", description="Try to guess the full hangman word!")
    async def hmGuess(self, intr: discord.Interaction, guess: str) -> None:
        await self.userAndGameChecks(intr.user.id, intr.guild)
        # self.game_manager.addGameIfNeeded(intr.guild.id, intr.user.id)  removed due to issues?
        if not await self.passGuessChecks(guess, intr):
            return
        else:
            await self.makeGuess(guess, intr, intr.user)


    async def passGuessChecks(self, guess, intr: discord.Interaction):
        guild_id = intr.guild.id
        if not self.game_manager.gameIsActive(guild_id):
            await intr.response.send_message(f"I'm no expert, but you should probably start a game before trying to make a guess.")
            return False
        if not await self.acceptGuess(guess, intr):
            return False
        return True

    async def acceptGuess(self, guess: str, intr: discord.Interaction) -> bool:
        if not guess.isalpha():
            await intr.response.send_message(f"Is that even in the English lexicon?")
            return False
        if self.guessedPreviously(guess, intr.guild.id):
            await intr.response.send_message(f"You've already guessed the letter '{guess.upper()}', you might want to try another!")
            return False
        return True


    def guessedPreviously(self, guess: str, guild_id: int):
        return self.game_manager.guessInGuessedLetters(guild_id, guess)


    async def makeGuess(self, guess: str, intr: discord.Interaction, author: discord.User):
        if len(guess) > 1:
            await self.guessWord(guess, intr, author)
        elif len(guess) == 1:
            await self.guessLetter(guess, intr, author.id)
            pass
        else:
            await intr.response.send_message(f"Something went wrong with your guess thanks to a lousy dev, try again!")


    async def guessLetter(self, guess: str, intr: discord.Interaction, guesser_id: int):
        guild_id = intr.guild.id
        self.game_manager.addGuessedLetter(guess, guild_id)
        if not self.letterInWord(guess, guild_id):
            await self.incorrectLetter(intr, guesser_id, guess)
        else:
            await self.correctLetter(intr, guesser_id, guess)
            if self.game_manager.checkForWin(guild_id):
                guild = self.game_manager.hm_games.get(guild_id)
                guild.resetGame()
                self.game_manager.updateGuild(guild)
                self.game_manager.hm_stats.updateWins(guild)
                await self.winGame(intr)
            else:
                await self.sendNextTurnMessage(intr.channel, guild_id)


    async def correctLetter(self, intr: discord.Interaction, guesser_id: int, guess: str) -> None:
        guild_id = intr.guild.id
        self.game_manager.correctLetterGuess(guild_id, guesser_id)
        self.bot.kambot_users.get(int(f'{intr.user.id}{guild_id}')).increasePoints(
            self.game_manager.getDifficultyPointOffset(guild_id)
        )
        await intr.response.send_message(f"Awesome! {guess.upper()} is in the word!  One step closer to saving the hangman!")


    async def incorrectLetter(self, intr: discord.Interaction, guesser_id, guess):
        self.game_manager.incorrectLetterGuess(intr.guild.id, guesser_id)
        await intr.response.send_message(f"Oh no! '{guess.upper()}' was not a correct letter.")
        await self.sendNextTurnMessage(intr.channel, intr.guild.id)
        await self.lossConditionsMet(intr.channel)


    async def lossConditionsMet(self, channel: discord.TextChannel) -> None:
        guild = self.game_manager.getGuildGame(channel.guild.id)
        if guild.getGameTurn() == 8:
            await channel.send(f'Oh no!  You failed to save the hangman!  The word was \'{guild.getGameWord()}\'.')
            self.game_manager.updateLosses(guild.getGuildID())
            guild.resetGame()
            self.game_manager.updateGuild(guild)




    def letterInWord(self, guess, guild_id):
        return self.game_manager.inGameWord(guild_id, guess)


    async def guessWord(self, guess: str, intr: discord.Interaction, author: discord.User) -> None:
        if not await self.confirmWord(guess, intr, author):
            return
        else:
            guild_id = intr.guild.id
            if self.game_manager.isCorrectWord(guild_id, guess, author.id):
                self.bot.kambot_users.get(int(f'{author.id}{guild_id}')).increasePoints(
                    self.game_manager.getPointsEarnedForWord(guild_id)
                )
                self.game_manager.correctWordActions(guild_id, author.id)
                await self.winGame(intr)
            else:
                self.game_manager.incorrectWordActions(guild_id, author.id)
                await intr.followup.send(f"Whoops! '{guess}' is not the correct word!")
                await self.sendNextTurnMessage(intr.channel, guild_id)
                await self.lossConditionsMet(intr.channel)


    async def sendNextTurnMessage(self, channel: discord.TextChannel, guild_id: int):
        guild = self.game_manager.getGuildGame(guild_id)
        gallows_embed = self.createGallowsEmbed(guild)
        gallows_img = self.gallowImg(guild.getGameTurn())
        await channel.send(file=gallows_img, embed=gallows_embed)


    async def winGame(self, intr: discord.Interaction):
        win_embed = await self.createWinEmbed(intr.guild.id)
        win_gif = self.getWinGif()
        await intr.channel.send(file=win_gif, embed=win_embed)


    def getWinGif(self):
        return discord.File(f"KamBotFiles/hangmanSaved.gif", filename=f"hangmanSaved.gif")

    async def createWinEmbed(self, guild_id: int) -> discord.Embed:
        win_embed = discord.Embed(title="The Gallows")
        guild = self.game_manager.getGuildGame(guild_id)
        win_embed.set_image(url="attachment://hangmanSaved.gif")
        win_embed.add_field(name="\u200b", value="Congratulations!", inline=False)
        win_embed.add_field(name="\u200b", value=f"You guessed the word '{guild.getGameWord()}' and saved the hangman!",
                            inline=False)
        return win_embed

    async def confirmWord(self, guess: str, intr : discord.Interaction, author: discord.User) -> bool:
        await intr.response.send_message(f"Are you sure you want to guess '{guess.lower()}' as the word?")
        confirm_guess_message = await intr.channel.send(f'Guess {guess.lower()} as the word?')
        if not await self.confirmMessage(confirm_guess_message, author):
            await intr.channel.send(f"{guess.capitalize()} was not guessed and no turns were used.")
            return False
        return True

    async def confirmMessage(self, message: discord.Message, author: discord.User):
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




    # A command is initiated when the prefix and command name are combined and sent as a message in Discord.
    @app_commands.command(name="hmstop",
                          description="Stops an ongoing game.")
    # Defines the function to manually stop the game
    async def stop(self, intr: discord.Interaction):
        await self.userAndGameChecks(intr.user.id, intr.guild)
        # Creates the variables needed.
        guild_id = intr.guild.id
        # Retrieves the game status for the appropriate guild.
        game_status = self.game_manager.hm_games.get(guild_id).gameStatus()
        # Checks the game status.
        if not bool(game_status):
            # If no game is running, a message is sent alerting the user that no game is in progress.
            await intr.response.send_message("There is no game to stop!")
        else:
            # If a game is running, the game is stopped and a message is sent alerting the user that the game has been stopped.
            self.game_manager.hm_games.get(guild_id).resetGame()
            await intr.response.send_message("The game of hangman has been stopped.")


    # A command is initiated when the prefix and command name are combined and sent as a message in Discord.
    @app_commands.command(name="hmstats", description="Shows the server and user stats for hangman.")
    # Defines the command to retrieve the stats for the appropriate guild.
    async def get_stats(self, intr: discord.Interaction):
        await self.userAndGameChecks(intr.user.id, intr.guild)
        guild_id = intr.guild.id
        author_id = intr.user.id
        author_nick = intr.user.nick
        guild_name = intr.guild.name
        hm_guild_stats = self.game_manager.hm_stats.hm_guild_stats.get(guild_id)
        user_stats = self.game_manager.hm_stats.hm_user_stats.get(int(f'{author_id}{guild_id}'))
        if intr.user.nick is None:
            author_nick = intr.user.name
        g_stats = await self.create_stats(guild_name, hm_guild_stats)
        u_stats = await self.create_user_stats(user_stats, guild_id, author_nick)
        await intr.response.send_message(embed=g_stats)
        await intr.followup.send(embed=u_stats)

    # Defines the function to create the embed for the guild stats message.
    async def create_stats(self, guild_name: str, guild: HMGuildStats):
        embed_stats = discord.Embed(title=f"{guild_name}'s hangman stats.")
        embed_stats.add_field(name="Games",
                              value=f"Hangmen saved = {guild.getTotalGamesWon()}\nHangmen condemned = "
                                    f"{guild.getTotalGamesLost()}\nTotal completed games = {guild.getTotalGamesPlayed()}")
        embed_stats.add_field(name="Letters",
                              value=f"Correct letters guessed = {guild.getTotalCorrectLettersGuessed()}\n"
                                    f"Incorrect letters guessed = {guild.getTotalIncorrectLettersGuessed()}\n"
                                    f"Total letters guessed = {guild.getTotalLettersGuessed()}",
                              inline=False)
        embed_stats.add_field(name="Words",
                              value=f"Correct words guessed = {guild.getTotalCorrectWordsGuessed()}\n"
                                    f"Incorrect words guessed = {guild.getTotalIncorrectWordsGuessed()}\n"
                                    f"Total words guessed = {guild.getTotalWordsGuessed()}")
        return embed_stats

    # Defines the function to create the embed for the user stats message.
    async def create_user_stats(self, hm_user: HMUserStats, guild_id: int, author_nick: str):
        embed_user_stats = discord.Embed(title=f"{author_nick}'s hangman stats.")
        embed_user_stats.add_field(name="KamKoins",
                                   value=f"You currently have {self.bot.kambot_users.get(hm_user.getKey()).getUserPoints()} "
                                         f"KamKoins.", inline=False)
        embed_user_stats.add_field(name="Games",
                                   value=f"Hangmen saved = {hm_user.getTotalWins()}\n"
                                         f"Hangmen condemned = {hm_user.getTotalLosses()}\n"
                                         f"Total games = {hm_user.getTotalGames()}",
                                   inline=False)
        embed_user_stats.add_field(name="Letters",
                                   value=f"Correct letters guessed = {hm_user.getCorrectLettersGuessed()}\n"
                                         f"Incorrect letters guessed = {hm_user.getIncorrectLettersGuessed()}\n"
                                         f"Total letters guessed = {hm_user.getTotalLettersGuessed()}",
                                   inline=False)
        embed_user_stats.add_field(name="Words",
                                   value=f"Correct words guessed = {hm_user.getTotalCorrectWordsGuessed()}\n"
                                         f"Incorrect words guessed = {hm_user.getTotalIncorrectWordsGuessed()}\n"
                                         f"Total words guessed = {hm_user.getTotalWordsGuessed()}")
        return embed_user_stats

    # Defines the function to give a user their base stats.


    @app_commands.command(name="hmbuy", description="Use KamKoins to buy back a turn in hangman!")
    # Defines the function to buy back a turn for the appropriate guild.
    async def buy_turn(self, intr: discord.Interaction):
        await self.userAndGameChecks(intr.user.id, intr.guild)
        # Sets the appropriate variables to be used in the following processes
        author = intr.user
        guild_name = intr.guild.name
        guild = self.game_manager.getGuildGame(intr.guild.id)
        user_id = intr.user.id
        turn = guild.getGameTurn()
        points = self.bot.kambot_users.get(int(f'{user_id}{intr.guild.id}')).getUserPoints()
        if turn <= 0:
            await intr.response.send_message("You cannot buy back a turn if zero have been used.")
        # However, if a turn has been taken, the process begins to buy a turn
        elif turn > 0:
            # If the user does not have enough points to buy a turn, a message is sent to inform the user.
            if points < 15:
                await intr.response.send_message("You don't have enough KamKoins to buy a turn.")
            # If the user has enough points, the points are removed from their account, the turn is decreased by one, and stats are updated.
            elif points >= 15:
                self.buyTurn(guild, user_id)
                await intr.response.send_message(f"{author.mention} has bought back a turn for {guild_name}!  Thanks!")

    def buyTurn(self, guild: HMGuildGame, user_id: int) -> None:
        self.game_manager.buyTurn(guild, user_id)
        self.bot.kambot_users.get(int(f'{user_id}{guild.getGuildID()}')).decreasePoints(15)



    @app_commands.command(name="hmadd-word", description="Add a word to your hangman word list!")
    @app_commands.choices(difficulty=[
            app_commands.Choice(name="Easy", value="easy"),
            app_commands.Choice(name="Hard", value="hard")
        ])
    async def hm_add(self, intr: discord.Interaction, difficulty: app_commands.Choice[str], word: str):
        await self.userAndGameChecks(intr.user.id, intr.guild)
        guild_id = intr.guild.id
        if not intr.permissions.administrator:
            await intr.response.send_message(f"Only administrators have the ability to add or remove words from the server word lists.")
            return
        if not path.exists(f"./TextFiles/{guild_id}/{guild_id}.hard.txt") or not path.exists(
                f"./TextFiles/{guild_id}/{guild_id}.easy.txt"):
            os.mkdir(f"TextFiles/{guild_id}")
            shutil.copy(f"KamBotFiles/DataFiles/HMWordsHard.txt", f"./TextFiles/{guild_id}/{guild_id}.hard.txt")
            shutil.copy(f"KamBotFiles/DataFiles/HMWordsEasy.txt", f"./TextFiles/{guild_id}/{guild_id}.easy.txt")
        if self.check_for_word(guild_id, difficulty.value, word):
            await intr.response.send_message(f"{word} already exists in your {difficulty.value.lower()} word list.")
            return
        with open(f"./TextFiles/{guild_id}/{guild_id}.{difficulty.value.lower()}.txt", "a") as file:
            file.write(f"\n{word.lower()}")
        await intr.response.send_message(f"{word.lower()} was added to your {difficulty.value} word list!")

    def check_for_word(self, guild_id: int, difficulty: str, word: str):
        word_file = open(f"TextFiles/{guild_id}/{guild_id}.{difficulty.lower()}.txt", "r")
        for line in word_file:
            if line.strip() == word.strip():
                word_file.close()
                return True
        word_file.close()
        return False

    @app_commands.command(name="hmremove-word",
                          description="remove a word to your hangman word list!")
    @app_commands.choices(difficulty=[
            app_commands.Choice(name="Easy", value="easy"),
            app_commands.Choice(name="Hard", value="hard")
        ])
    async def hm_remove(self, intr: discord.Interaction, difficulty: app_commands.Choice[str], word: str):
        await self.userAndGameChecks(intr.user.id, intr.guild)
        guild_id = intr.guild.id
        if not intr.permissions.administrator:
            await intr.response.send_message(f"Only administrators have the ability to add or remove words from the server word lists.")
            return
        if not path.exists(f"./TextFiles/{guild_id}/{guild_id}.hard.txt") or not path.exists(
                f"./TextFiles/{guild_id}/{guild_id}.easy.txt"):
            try:
                os.mkdir(f"./TextFiles/{guild_id}")
                shutil.copy(f"KamBotFiles/DataFiles/HMWordsHard.txt", f"./TextFiles/{guild_id}/{guild_id}.hard.txt")
                shutil.copy(f"KamBotFiles/DataFiles/HMWordsEasy.txt", f"./TextFiles/{guild_id}/{guild_id}.easy.txt")
            except Exception as e:
                print(f'Exception occured creating custom word list while removing word {word}: {e}')
        with open(f"./TextFiles/{guild_id}/{guild_id}.{difficulty.value.lower()}.txt", "r+") as file:
            reader = file.readlines()
            file.seek(0)
            found_word = False
            for line in reader:
                if line.strip() != word.lower().strip():
                    file.write(line)
                else:
                    found_word = True
            file.truncate()
        if found_word:
            await intr.response.send_message(f"{word.capitalize()} was found in your {difficulty.value.lower()} word list, it has been removed!")
        else:
            await intr.response.send_message(f'{word.capitalize()} was not found in your {difficulty.value.lower()} word list!')

    @app_commands.command(name="hmlist", description="Check out your word lists!")
    async def hm_list(self, intr: discord.Interaction):
        await self.userAndGameChecks(intr.user.id, intr.guild)
        wordlist_easy = ""
        wordlist_hard = ""
        guild_id = intr.guild.id
        if not path.exists(f"./TextFiles/{guild_id}/{guild_id}.hard.txt") or not path.exists(
                f"./TextFiles/{guild_id}/{guild_id}.easy.txt"):
            for word in self.game_manager.default_easy_word_list:
                wordlist_easy += word + ", "
            for word in self.game_manager.default_hard_word_list:
                wordlist_hard += word + ", "
        else:
            with open(f"./TextFiles/{guild_id}/{guild_id}.easy.txt") as efile:
                for word in efile:
                    wordlist_easy += word.strip() + ", "
            with open(f"./TextFiles/{guild_id}/{guild_id}.hard.txt") as hfile:
                for word in hfile:
                    wordlist_hard += word.strip() + ", "
        await intr.response.send_message(f"**Your easy word list contains the following words:** {wordlist_easy}")
        await intr.followup.send(f"**Your hard word list contains the following words:** {wordlist_hard}")

    def removeHMGuild(self, guild_id: int) -> None:
        self.game_manager.removeHMGuild(guild_id)

    def removeHMUser(self, user_id : int, guild_id : int) -> None:
        self.game_manager.hm_stats.removeUser(user_id, guild_id)

async def setup(bot):
    await bot.add_cog(Hangman(bot))

