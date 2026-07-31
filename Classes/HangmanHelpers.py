from typing import List
from os import path
import random



class HMUserStats:
    def __init__(self, u_id: int = 0, g_id: int = 0, egs: int = 0, hgs: int = 0, clg: int = 0, egw: int = 0,
                 hgw: int = 0, ilg: int = 0, egl: int = 0, hgl: int = 0, pe: int = 0, hmtb: int = 0,
                 cewg: int = 0, chwg: int = 0, iewg: int = 0, ihwg: int = 0):
        self.user_id = u_id
        self.guild_id = g_id
        self.easy_games_started = egs
        self.hard_games_started = hgs
        self.correct_letters_guessed = clg
        self.easy_games_won = egw
        self.hard_games_won = hgw
        self.incorrect_letters_guessed = ilg
        self.easy_games_lost = egl
        self.hard_games_lost = hgl
        self.points_earned = pe
        self.turns_bought = hmtb
        self.cor_easy_words_guessed = cewg
        self.cor_hard_words_guessed = chwg
        self.inc_easy_words_guessed = iewg
        self.inc_hard_words_guessed = ihwg

    def getUserId(self):
        return self.user_id

    def getGuildId(self):
        return self.guild_id

    def getTurnsBought(self):
        return self.turns_bought

    def getPointsEarned(self):
        return self.points_earned

    def getGamesStarted(self, diff: int) -> int:
        if diff == 1:
            return self.hard_games_started
        return self.easy_games_started

    def isDefault(self):
        return self.user_id == 0

    def getKey(self) -> int:
        return int(f'{self.user_id}{self.guild_id}')





    def __str__(self):
        return (f"User ID: {self.user_id}\n"
                f"Guild ID: {self.guild_id}\n"
                f"  Letters:\n"
                f"      Correct Guesses: {self.correct_letters_guessed}\n"
                f"      Incorrect Guesses: {self.incorrect_letters_guessed}\n"
                f"  Points:\n"
                f"      Points Earned in Hangman: {self.points_earned}\n"
                f"      Turns Bought: {self.turns_bought}\n"
                f"  Easy Games:\n"
                f"      Started: {self.easy_games_started}\n"
                f"      Won: {self.easy_games_won}\n"
                f"      Lost: {self.easy_games_lost}\n"
                f"      Correct Word Guesses: {self.cor_easy_words_guessed}\n"
                f"      Incorrect Word Guesses: {self.inc_easy_words_guessed}\n"
                f"  Hard Games:\n"
                f"      Started: {self.hard_games_started}\n"
                f"      Won: {self.hard_games_won}\n"
                f"      Lost: {self.hard_games_lost}\n"
                f"      Correct Word Guesses: {self.cor_hard_words_guessed}\n"
                f"      Incorrect Word GUesses: {self.inc_hard_words_guessed}")

    def incrementCorrectHardWordGuesses(self) -> None:
        self.cor_hard_words_guessed += 1
        self.hard_games_won += 1

    def incrementCorrectEasyWordGuesses(self) -> None:
        self.cor_easy_words_guessed += 1
        self.easy_games_won += 1


    def incrementIncorrectHardWordGuesses(self) -> None:
        self.inc_hard_words_guessed += 1

    def incrementIncorrectEasyWordGuesses(self) -> None:
        self.inc_easy_words_guessed += 1

    def incrementIncorrectLetterGuesses(self) -> None:
        self.incorrect_letters_guessed += 1

    def incrementIncorrectWordsGuessed(self, diff: int) -> None:
        if diff == 1:
            self.inc_hard_words_guessed += 1
        else:
            self.inc_easy_words_guessed += 1

    def incrementCorrectLetterGuesses(self) -> None:
        self.correct_letters_guessed += 1


    def incrementGamesWon(self, diff : int) -> None:
        if diff == 1:
            self.hard_games_won += 1
        else:
            self.easy_games_won += 1


    def incrementWordsGuessed(self, diff: int) -> None:
        if diff == 1:
            self.cor_hard_words_guessed += 1
        else:
            self.cor_easy_words_guessed += 1

    def incrementGamesStarted(self, diff: int = 0) -> None:
        if diff == 1:
            self.hard_games_started += 1
        else:
            self.easy_games_started += 1

    def getKey(self) -> int:
        return int(f"{self.user_id}{self.guild_id}")

    def getGamesWon(self, diff : int) -> int:
        if diff == 1:
            return self.hard_games_won
        else:
            return self.easy_games_won

    def getTotalWins(self) -> int:
        return self.getGamesWon(1) + self.getGamesWon(0)

    def getGamesLost(self, diff : int) -> int:
        if diff == 1:
            return self.hard_games_lost
        else:
            return self.easy_games_lost

    def getTotalLosses(self) -> int:
        return self.getGamesLost(1) + self.getGamesLost(0)

    def getTotalGames(self) -> int:
        return self.getTotalLosses() + self.getTotalWins()

    def getCorrectLettersGuessed(self) -> int:
        return self.correct_letters_guessed

    def getIncorrectLettersGuessed(self) -> int:
        return self.incorrect_letters_guessed

    def getTotalLettersGuessed(self) -> int:
        return self.getCorrectLettersGuessed() + self.getIncorrectLettersGuessed()

    def getCorrectWordsGuessed(self, diff: int) -> int:
        if diff == 1:
            return self.cor_hard_words_guessed
        else:
            return self.cor_easy_words_guessed

    def getTotalCorrectWordsGuessed(self) -> int:
        return self.getCorrectWordsGuessed(1) + self.getCorrectWordsGuessed(0)

    def getIncorrectWordsGuessed(self, diff: int) -> int:
        if diff == 1:
            return self.inc_hard_words_guessed
        else:
            return self.inc_easy_words_guessed

    def getTotalIncorrectWordsGuessed(self) -> int:
        return self.getIncorrectWordsGuessed(1) + self.getIncorrectWordsGuessed(0)

    def getTotalWordsGuessed(self) -> int:
        return self.getTotalCorrectWordsGuessed() + self.getTotalIncorrectWordsGuessed()

    def updateGamesLost(self, diff: int):
        if diff == 1:
            self.hard_games_lost += 1
        else:
            self.easy_games_lost += 1

    def updateGamesWon(self, diff : int):
        if diff == 1:
            self.hard_games_won += 1
        else:
            self.easy_games_won += 1

    def incrementTurnsBought(self) -> None:
        self.turns_bought += 1



class HMGuildStats:
    def __init__(self, guild_id: int = 0, egs: int = 0, egw: int = 0, egl: int = 0, hgs: int = 0, hgw: int = 0,
                 hgl: int = 0, clg: int = 0, ilg: int = 0, ceg: int = 0, chg: int = 0, ieg: int = 0, ihg: int = 0):
        self.guild_id = guild_id
        self.easy_games_started = egs
        self.easy_games_won = egw
        self.easy_games_lost = egl
        self.hard_games_started = hgs
        self.hard_games_won = hgw
        self.hard_games_lost = hgl
        self.correct_letter_guesses = clg
        self.incorrect_letter_guesses = ilg
        self.correct_easy_word_guesses = ceg
        self.correct_hard_word_guesses = chg
        self.incorrect_easy_word_guesses = ieg
        self.incorrect_hard_word_guesses = ihg

    def getEasyGamesStarted(self):
        return self.easy_games_started

    def getEasyGamesWon(self):
        return self.easy_games_won

    def getEasyGamesLost(self):
        return self.easy_games_lost

    def getHardGamesStarted(self):
        return self.hard_games_started

    def getHardGamesWon(self):
        return self.hard_games_won

    def getHardGamesLost(self):
        return self.hard_games_lost


    def __str__(self):
        return (f"Guild ID: {self.guild_id}\n"
                f"  Letters:\n"
                f"      Correct Guesses: {self.correct_letter_guesses}\n"
                f"      Incorrect Guesses: {self.incorrect_hard_word_guesses} \n"
                f"  Easy Games:\n"
                f"      Started: {self.easy_games_started}\n"
                f"      Won: {self.easy_games_won}\n"
                f"      Lost: {self.easy_games_lost}\n"
                f"      Correct Word Guesses: {self.correct_easy_word_guesses}\n"
                f"      Incorrect Word Guesses: {self.incorrect_easy_word_guesses}\n"
                f"  Hard Games: \n"
                f"      Started: {self.hard_games_started}\n"
                f"      Won: {self.hard_games_won}\n"
                f"      Lost: {self.hard_games_lost}\n"
                f"      Correct Word Guesses: {self.correct_hard_word_guesses}\n"
                f"      Incorrect Word Guesses: {self.incorrect_hard_word_guesses}")

    def correctGuessedWord(self, difficulty: int) -> None:
        if difficulty == 1:
            self.incrementCorrectHardWordGuesses()
        else:
            self.incrementCorrectEasyWordGuesses()

    def updateGamesLost(self, diff: int) -> None:
        if diff == 1:
            self.hard_games_lost += 1
        else:
            self.easy_games_lost += 1

    def updateGamesWon(self, diff: int) -> None:
        if diff == 1:
            self.hard_games_won += 1
        else:
            self.easy_games_won += 1

    def incrementCorrectHardWordGuesses(self) -> None:
        self.correct_hard_word_guesses += 1
        self.hard_games_won += 1

    def incrementCorrectEasyWordGuesses(self) -> None:
        self.correct_easy_word_guesses += 1
        self.easy_games_won += 1

    def incorrectGuessedWord(self, difficulty: int) -> None:
        if difficulty == 1:
            self.incrementIncorrectHardWordGuesses()
        else:
            self.incrementIncorrectEasyWordGuesses()

    def incrementIncorrectHardWordGuesses(self) -> None:
        self.incorrect_hard_word_guesses += 1

    def incrementIncorrectEasyWordGuesses(self) -> None:
        self.incorrect_easy_word_guesses += 1

    def incrementIncorrectLetterGuesses(self) -> None:
        self.incorrect_letter_guesses += 1

    def incrementCorrectLetterGuesses(self) -> None:
        self.correct_letter_guesses += 1

    def incrementGamesStarted(self, diff: int = 0) -> None:
        if diff == 1:
            self.hard_games_started += 1
        else:
            self.easy_games_started += 1

    def incrementHardGamesWon(self) -> None:
        self.hard_games_won += 1

    def incrementWordsGuessed(self, diff: int) -> None:
        if diff == 1:
            self.correct_hard_word_guesses += 1
        else:
            self.correct_easy_word_guesses += 1

    def incrementIncorrectWordsGuessed(self, diff: int) -> None:
        if diff == 1:
            self.incorrect_hard_word_guesses += 1
        else:
            self.incorrect_easy_word_guesses += 1

    def incrementGamesWon(self, diff: int) -> None:
        if diff == 1:
            self.hard_games_won += 1
        else:
            self.easy_games_won += 1

    def getTotalGamesWon(self) -> int:
        return self.hard_games_won + self.easy_games_won

    def getTotalGamesLost(self) -> int:
        return self.hard_games_lost + self.easy_games_lost

    def getTotalGamesPlayed(self) -> int:
        return self.getTotalGamesWon() + self.getTotalGamesLost()

    def getTotalCorrectLettersGuessed(self) -> int:
        return self.correct_letter_guesses

    def getTotalIncorrectLettersGuessed(self) -> int:
        return self.incorrect_letter_guesses

    def getTotalLettersGuessed(self) -> int:
        return self.incorrect_letter_guesses + self.correct_letter_guesses

    def getCorrectWordsGuessed(self, diff: int) -> int:
        if diff == 1:
            return self.correct_hard_word_guesses
        else:
            return self.correct_easy_word_guesses

    def getTotalCorrectWordsGuessed(self) -> int:
        return self.getCorrectWordsGuessed(1) + self.getCorrectWordsGuessed(0)

    def getIncorrectWordsGuessed(self, diff: int) -> int:
        if diff == 1:
            return self.incorrect_hard_word_guesses
        else:
            return self.incorrect_easy_word_guesses

    def getTotalIncorrectWordsGuessed(self) -> int:
        return self.getIncorrectWordsGuessed(1) + self.getIncorrectWordsGuessed(0)

    def getTotalWordsGuessed(self) -> int:
        return self.getTotalIncorrectWordsGuessed() + self.getTotalCorrectWordsGuessed()

    def isDefault(self) -> bool:
        return self.guild_id == 0


class HMGuildGame:
    def __init__(self, guild_id: int = 0, word: str = "", guessed_letters: str = "", turn: int = 0,
                 game_status: int = 0, game_difficulty: int = 0, game_starter: int = 0):
        self.guild_id = guild_id
        self.game_word = word
        self.game_guesses = guessed_letters
        self.game_turn = turn
        self.game_status = game_status
        self.game_difficulty = game_difficulty
        self.game_starter_id = game_starter

    def __str__(self):
        return (f"guild ID: {self.guild_id}\n"
                f"  Word: {self.game_word}\n"
                f"  Guesses: {self.game_guesses}\n"
                f"  Turn: {self.game_turn}\n"
                f"  Status: {self.game_status}\n"
                f"  Difficulty: {"easy" if self.getDifficulty() == 0 else "hard"}\n"
                f"  Starter ID: {self.game_starter_id}")


    def getGuildID(self) -> int:
        return self.guild_id

    def getGameWord(self) -> str:
        return self.game_word.strip()

    def getGameTurn(self) -> int:
        return self.game_turn

    def gameStatus(self) -> int:
        return self.game_status

    def gameOn(self) -> int:
        return self.game_status

    def getDifficulty(self) -> int:
        return self.game_difficulty

    def getStarter(self) -> int:
        return self.game_starter_id

    def getGuessedLetters(self):
        return self.game_guesses.strip()

    def hasCustomWordLists(self) -> bool:
        if path.exists(f"./TextFiles/{self.guild_id}/{self.guild_id}.easy.txt"):
            return True
        return False

    def setWord(self, word: str):
        self.game_word = word

    def setDifficulty(self, difficulty: str) -> None:
        self.game_difficulty = difficulty

    def startGame(self, word: str, difficulty : int, starter_id: int):
        self.game_word = word
        self.game_difficulty = difficulty
        self.game_starter_id = starter_id
        self.game_status = True
        self.game_turn = 0


    def incrementTurn(self) -> int:
        self.game_turn += 1
        return self.game_turn

    def getBlankSpaces(self) -> str:
        word = self.getGameWord()
        blank_spaces = ""
        for letter in word:
            if letter in self.getGuessedLetters():
                blank_spaces += f"{letter} "
            else:
                blank_spaces += "\_ "
        return blank_spaces

    def inGuessedLetters(self, guess):
        if guess in self.game_guesses:
            return True
        return False

    def inGameWord(self, letter: str) -> bool:
        for let in self.game_word:
            if letter.lower().strip() == let.lower().strip():
                return True
        return False

    def resetGame(self):
        self.game_word = ""
        self.game_difficulty = 0
        self.game_starter_id = 0
        self.game_status = 0
        self.game_turn = 0
        self.game_guesses = ""

    def addGuessedLetter(self, letter):
        self.game_guesses += letter.lower()

    def getFormattedGuessedLetters(self) -> str:
        x = 0
        formatted_guesses = ""
        for letter in self.game_guesses:
            if x < (len(self.game_guesses) - 1):
                formatted_guesses += f"{letter.upper()}, "
                x += 1
            else:
                formatted_guesses += letter.upper()
        return formatted_guesses

    def decrementTurn(self) -> None:
        self.game_turn -= 1

    def isDefault(self):
        return self.guild_id == 0

class HMGameManager:
    def __init__(self):
        self.default_easy_word_list = self.createDefaultEasyWords()
        self.default_hard_word_list = self.createDefaultHardWords()
        self.hm_games = {}
        self.hm_stats = HMStatManager()

    def storeGame(self, guild_record: tuple):
        self.hm_games[guild_record[0]] = HMGuildGame(guild_record[0], guild_record[1], guild_record[10],
                                                     guild_record[11], guild_record[12], guild_record[13],
                                                     guild_record[14])

    def getGuildsForDeposit(self) -> list:
        guild_list = []
        for guild_id in self.hm_games:
            guild = self.getGuildGame(guild_id)
            guild_stats = self.hm_stats.getGuildStats(guild_id)
            guild_list.append(self.createListFromGuildAndStats(guild, guild_stats))
        return guild_list

    def getUsersForDeposit(self):
        user_list = []
        for user_id in self.hm_stats.hm_user_stats:
            user = self.hm_stats.hm_user_stats.get(user_id)
            user_list.append(self.createUserStatList(user))
        return user_list

    def createListFromGuildAndStats(self, guild: HMGuildGame, stats: HMGuildStats) -> list:
        return [
            guild.getGuildID(),
            guild.getGameWord(),
            stats.getEasyGamesStarted(),
            stats.getEasyGamesWon(),
            stats.getEasyGamesLost(),
            stats.getHardGamesStarted(),
            stats.getHardGamesWon(),
            stats.getHardGamesLost(),
            stats.getTotalCorrectLettersGuessed(),
            stats.getTotalIncorrectLettersGuessed(),
            guild.getGuessedLetters(),
            guild.getGameTurn(),
            guild.gameStatus(),
            guild.getDifficulty(),
            guild.getStarter(),
            stats.getCorrectWordsGuessed(0),
            stats.getCorrectWordsGuessed(1),
            stats.getIncorrectWordsGuessed(0),
            stats.getIncorrectWordsGuessed(1)
        ]

    def createUserStatList(self, user: HMUserStats):
        return [
            user.getUserId(),
            user.getGuildId(),
            user.getGamesStarted(0),
            user.getGamesStarted(1),
            user.getCorrectLettersGuessed(),
            user.getGamesWon(0),
            user.getGamesWon(1),
            user.getIncorrectLettersGuessed(),
            user.getGamesLost(0),
            user.getGamesLost(1),
            user.getPointsEarned(),
            user.getTurnsBought(),
            user.getCorrectWordsGuessed(0),
            user.getCorrectWordsGuessed(1),
            user.getIncorrectWordsGuessed(0),
            user.getIncorrectWordsGuessed(1)
        ]


    def printGuilds(self):
        print(f"Hangman Guilds:")
        for guild in self.hm_games:
            print(f"{self.getGuildGame(guild)}\n")

    def createDefaultEasyWords(self) -> List[str]:
        easy_words = []
        with open('KamBotFiles/DataFiles/HMWordsEasy.txt', 'r') as easy_word_list:
            for word in easy_word_list:
                easy_words.append(word.strip())
        return easy_words

    def createDefaultHardWords(self) -> List[str]:
        hard_words = []
        with open('KamBotFiles/DataFiles/HMWordsHard.txt', 'r') as hard_word_list:
            for word in hard_word_list:
                hard_words.append(word.strip())
        return hard_words

    def updateGuild(self, guild: HMGuildGame) -> None:
        self.hm_games[guild.getGuildID()] = guild


    def getWordFromFile(self, guild_id, diff : int):
        wordlist = []
        diff_string = "easy" if diff == 0 else "hard"
        with open(f"./TextFiles/{guild_id}/{guild_id}.{diff_string}.txt") as file:
            for line in file:
                wordlist.append(line)
        word = random.choice(wordlist)
        if word == "\n":
            word = self.getWordFromFile(guild_id, diff)
        return word.strip()

    def gameIsActive(self, guild_id) -> bool:
        return self.getGuildGame(guild_id).gameStatus() == 1


    def startGame(self, guild_id: int, difficulty: int, starter_id: int) -> None:
        # self.addGameIfNeeded(guild_id, starter_id)
        self.giveGameWord(guild_id, difficulty, starter_id)
        self.hm_stats.updateNewGameStats(starter_id, guild_id, difficulty)



    def addGameIfNeeded(self, guild_id, starter_id) -> bool:
        if self.gameExists(guild_id) or self.statsExist(guild_id, starter_id):
            return False
        return True


    def statsExist(self, guild_id: int, user_id: int) -> None:
        self.hm_stats.addGuildStats(guild_id)
        self.hm_stats.addUserStats(guild_id, user_id)


    def gameExists(self, guild_id):
        if guild_id not in self.hm_games:
            self.hm_games[guild_id] = HMGuildGame(guild_id)

    def giveGameWord(self, guild_id: int, difficulty: int, starter_id: int):
        if self.getGuildGame(guild_id).hasCustomWordLists():
            self.giveCustomWord(guild_id, difficulty, starter_id)
        else:
            self.giveDefaultWord(guild_id, difficulty, starter_id)

    def giveDefaultWord(self, guild_id: int, difficulty: int, starter_id: int):
        if difficulty == 1:
            game_word = self.getHardWord()
        else:
            game_word = self.getEasyWord()
        self.hm_games[guild_id].startGame(game_word, difficulty, starter_id)

    def getEasyWord(self):
        return random.choice(self.default_easy_word_list)

    def getHardWord(self):
        return random.choice(self.default_hard_word_list)

    def giveCustomWord(self, guild_id: int, difficulty: int, starter_id: int):
        game_word = self.getCustomWord(guild_id, difficulty)
        self.getGuildGame(guild_id).startGame(game_word, difficulty, starter_id)

    def getCustomWord(self, guild_id: int, difficulty: int) -> str:
        wordlist = []
        diff_string = "easy" if difficulty == 0 else "hard"
        with open(f"./TextFiles/{guild_id}/{guild_id}.{diff_string}.txt") as file:
            for line in file:
                wordlist.append(line)
        word = random.choice(wordlist)
        if word == "\n":
            word = self.getCustomWord(guild_id, difficulty)
        return word.strip()


    def isHard(self, diff_arg: str) -> bool:
        for diff_str in ["h", "hard"]:
            if diff_arg == diff_str:
                return True
        return False

    def isEasy(self, diff_arg: str) -> bool:
        for diff_str in ["e", "easy"]:
            if diff_arg == diff_str:
                return True
        return False

    def getBlankSpaces(self, guild_id: int) -> str:
        word = self.hm_games[guild_id].getGameWord()
        blank_spaces = ""
        for letter in word:
            if letter in self.hm_games[guild_id].getGuessedLetters():
                blank_spaces += f"{letter} "
            else:
                blank_spaces += "\_ "
        return blank_spaces

    def getGameWord(self, guild_id) -> str:
        return self.getGuildGame(guild_id).getGameWord().strip()


    def getGuildGame(self, guild_id) -> HMGuildGame:
        guild = self.hm_games.get(guild_id, HMGuildGame())
        if guild.isDefault():
            print(f'Guild not found in HMGameManager <{guild_id}>')
            guild = HMGuildGame(guild_id)
            self.hm_games[guild_id] = guild
        return guild


    def guessInGuessedLetters(self, guild_id, guess):
        if self.getGuildGame(guild_id).inGuessedLetters(guess):
            return True
        return False


    def isCorrectWord(self, guild_id: int, word: str, author_id: int) -> bool:
        if word.strip().lower() == self.getGameWord(guild_id).lower().strip():
            return True
        return False


    def correctWordActions(self, guild_id: int, guesser_id: int):
        difficulty = self.getGuildGame(guild_id).getDifficulty()
        starter_id = self.getGuildGame(guild_id).getStarter()
        self.hm_stats.correctWordIncrements(guild_id, guesser_id, starter_id, difficulty)
        self.getGuildGame(guild_id).resetGame()

    def incorrectWordActions(self, guild_id: int, guesser_id: int):
        difficulty = self.getGuildGame(guild_id).getDifficulty()
        self.hm_stats.incorrectWordIncrements(guild_id, guesser_id, difficulty)
        self.incrementGameTurn(guild_id)

    def incrementGameTurn(self, guild_id: int) -> int:
        return self.getGuildGame(guild_id).incrementTurn()

    def inGameWord(self, guild_id, guess) -> bool:
        return self.getGuildGame(guild_id).inGameWord(guess)

    def addGuessedLetter(self, letter: str, guild_id: int) -> None:
        self.hm_games[guild_id].addGuessedLetter(letter.lower())

    def incorrectLetterGuess(self, guild_id: int, guesser_id: int) -> None:
        self.getGuildGame(guild_id).incrementTurn()
        self.hm_stats.incorrectLetterIncrement(guild_id, guesser_id)

    def correctLetterGuess(self, guild_id: int, guesser_id: int) -> None:
        self.hm_stats.correctLetterIncrement(guild_id, guesser_id)


    def getGameTurn(self, guild_id: int) -> int:
        return self.hm_games[guild_id].getGameTurn()

    def checkForWin(self, guild_id: int) -> bool:
        game = self.getGuildGame(guild_id)
        game_word = game.getGameWord()
        guessed_letters = game.getGuessedLetters()
        guessed_portion = ''
        for letter in game_word:
            if letter in guessed_letters:
                guessed_portion += letter
        return guessed_portion == game_word

    #Hard games net the number of unguessed letter + 2, easy games net the number of unguessed letters + 1
    def getPointsEarnedForWord(self, guild_id: int) -> int:
        guild = self.getGuildGame(guild_id)
        word = guild.getGameWord()
        guessed_letters = guild.getGuessedLetters()
        x = 0
        for letter in word:
            if letter in guessed_letters:
                x += 1
        return (len(word) - x) + self.getDifficultyPointOffset(guild_id)


    def getDifficultyPointOffset(self, guild_id: int) -> int:
        if self.getGuildGame(guild_id).getDifficulty() == 1:
            return 2
        else:
            return 1

    def updateLosses(self, guild_id: int) -> None:
        guild = self.getGuildGame(guild_id)
        self.hm_stats.updateLosses(guild)

    def buyTurn(self, guild: HMGuildGame, buyer_id: int) -> None:
        guild.decrementTurn()
        self.updateGuild(guild)
        self.hm_stats.hm_user_stats.get(int(f'{buyer_id}{guild.getGuildID()}')).incrementTurnsBought()

    def removeHMGuild(self, guild_id) -> None:
        if guild_id in self.hm_games:
            del self.hm_games[guild_id]
        self.hm_stats.removeGuild(guild_id)



class HMStatManager:
    def __init__(self):
        self.hm_guild_stats = {}
        self.hm_user_stats = {}

    def updateWins(self, guild: HMGuildGame):
        guild_id = guild.getGuildID()
        starter_id = guild.getStarter()
        difficulty = guild.getDifficulty()
        self.hm_user_stats.get(self.getUserKey(starter_id, guild_id)).updateGamesWon(difficulty)
        self.getGuildStats(guild_id).updateGamesWon(difficulty)

    def updateLosses(self, guild: HMGuildGame) -> None:
        guild_id = guild.getGuildID()
        starter_id = guild.getStarter()
        difficulty = guild.getDifficulty()
        self.getUserStats(starter_id, guild_id).updateGamesLost(difficulty)
        self.getGuildStats(guild_id).updateGamesLost(difficulty)

    def storeGuildStats(self, guild_stats: tuple) -> None:
        self.hm_guild_stats[guild_stats[0]] = HMGuildStats(guild_stats[0], guild_stats[2], guild_stats[3],
                                                           guild_stats[4], guild_stats[5], guild_stats[6],
                                                           guild_stats[7], guild_stats[8], guild_stats[9],
                                                           guild_stats[15], guild_stats[16], guild_stats[17],
                                                           guild_stats[18])

    def storeUserStats(self, user_stats: tuple) -> None:
        self.hm_user_stats[int(f"{user_stats[0]}{user_stats[1]}")] = HMUserStats(user_stats[0], user_stats[1], user_stats[2], user_stats[3],
                                                        user_stats[4], user_stats[5], user_stats[6], user_stats[7],
                                                        user_stats[8], user_stats[9], user_stats[10], user_stats[11],
                                                        user_stats[12], user_stats[13], user_stats[14],
                                                        user_stats[15])

    def printGuildStats(self) -> None:
        for guild in self.hm_guild_stats:
            print(self.getGuildStats(guild))

    def printUserStats(self) -> None:
        for user in self.hm_user_stats:
            print(self.hm_user_stats.get(user))

    def correctGuessedWord(self, guild_id: int, guesser_id: int, difficulty: str, starter_id: int) -> None:
        if difficulty.lower().strip() == 1:
            self.correctHardWordIncrements(guild_id, guesser_id, starter_id)
        else:
            self.correctEasyWordIncrements(guild_id, guesser_id, starter_id)

    def correctWordIncrements(self, guild_id : int, guesser_id: int, starter_id: int, diff : int) -> None:
        self.getGuildStats(guild_id).incrementGamesWon(diff)
        self.getGuildStats(guild_id).incrementWordsGuessed(diff)
        self.getUserStats(guesser_id, guild_id).incrementWordsGuessed(diff)
        self.getUserStats(starter_id, guild_id).incrementGamesWon(diff)


    def correctHardWordIncrements(self, guild_id: int, guesser_id: int, starter_id: int) -> None:
        self.getGuildStats(guild_id).incrementGamesWon(1)
        self.getGuildStats(guild_id).incrementWordsGuessed(1)
        self.getUserStats(guesser_id, guild_id).incrementWordsGuessed(1)
        self.getUserStats(starter_id, guild_id).incrementGamesWon(1)

    def correctEasyWordIncrements(self, guild_id: int, guesser_id: int, starter_id: int) -> None:
        self.getGuildStats(guild_id).incrementGamesWon(0)
        self.getGuildStats(guild_id).incrementWordsGuessed(0)
        self.getUserStats(guesser_id, guild_id).incrementWordsGuessed(0)
        self.getUserStats(starter_id, guild_id).incrementGamesWon(0)

    def getUserKey(self, user_id: int, guild_id: int) -> int:
        return int(f"{user_id}{guild_id}")


    def incorrectWordIncrements(self, guild_id: int, guesser_id: int, diff: int) -> None:
        self.getGuildStats(guild_id).incrementIncorrectWordsGuessed(diff)
        self.getUserStats(guesser_id, guild_id).incrementWordsGuessed(diff)


    def addGuildStats(self, guild_id: int) -> bool:
        if guild_id not in self.hm_guild_stats:
            self.hm_guild_stats[guild_id] = HMGuildStats(guild_id)
            return True

    def addUserStats(self, guild_id: int, user_id: int) -> bool:
        user_key = self.getUserKey(user_id, guild_id)
        if user_key not in self.hm_user_stats:
            self.hm_user_stats[user_key] = HMUserStats(user_id, guild_id)
            return True

    def incorrectLetterIncrement(self, guild_id, guesser_id):
        self.getGuildStats(guild_id).incrementIncorrectLetterGuesses()
        self.getUserStats(guesser_id, guild_id).incrementIncorrectLetterGuesses()


    def correctLetterIncrement(self, guild_id, guesser_id):
        self.getGuildStats(guild_id).incrementCorrectLetterGuesses()
        user_key = self.getUserKey(guesser_id, guild_id)
        self.getUserStats(guesser_id, guild_id).incrementCorrectLetterGuesses()

    def updateNewGameStats(self, user_id: int, guild_id: int, difficulty: int) -> None:
        self.getGuildStats(guild_id).incrementGamesStarted(difficulty)
        self.getUserStats(user_id, guild_id).incrementGamesStarted(difficulty)

    def getGuildStats(self, guild_id: int) -> HMGuildStats:
        guild = self.hm_guild_stats.get(guild_id, HMGuildStats())
        if guild.isDefault():
            print(f'Guild not found in HMStatManager <{guild_id}>')
            guild = HMGuildStats(guild_id)
            self.hm_guild_stats[guild_id] = guild
        return guild

    def getUserStats(self, user_id: int, guild_id: int) -> HMUserStats:
        user_key = self.getUserKey(user_id, guild_id)
        user = self.hm_user_stats.get(user_key, HMUserStats())
        if user.isDefault():
            print(f'User not found in HMStatManager. user ID: <{user_id}> guild ID: <{guild_id}>')
            user = HMUserStats(user_id, guild_id)
            self.hm_guild_stats[user_key] = user
        return user

    def removeGuild(self, guild_id) -> None:
        if guild_id in self.hm_guild_stats:
            del self.hm_guild_stats[guild_id]
        for user in self.hm_user_stats:
            if user.getGuildId() == guild_id:
                del self.hm_user_stats[user.getKey()]

    def removeUser(self, user_id : int, guild_id : int) -> None:
        if self.getUserKey(user_id, guild_id) in self.hm_user_stats:
            del self.hm_user_stats[self.getUserKey(user_id, guild_id)]