# bot.py

"""
This bot is currently designed to host a hangman game for multiple Discord guilds.  More games will be added
in the future.
Author = Mackenzie Carter
Latest version = KamBotV1
Date = 06/11/2022

"""
import asyncio
import datetime
import logging
import os
from pathlib import Path
import discord
from Classes.KBDB import KamBotDatabase
from Classes.Users import Users
from discord.ext import commands, tasks
from dotenv import load_dotenv
import traceback

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DBASE_FILE = os.getenv("DBASE_FILE_LOCATION")
APP_ID = os.getenv("APP_ID")


# logging.basicConfig(encoding='utf-8', level=logging.DEBUG,
#                     format='%(asctime)s - %(levelname)s User ID:[%(user_id)s] Guild ID:[%(guild_id)s] - '
#                            '%(message)s %(exception)s')

class DefaultContextFilter(logging.Filter):
    """Ensures user_id/guild_id/exception always exist on log records."""
    def filter(self, record):
        if not hasattr(record, 'user_id'):
            record.user_id = 'N/A'
        if not hasattr(record, 'guild_id'):
            record.guild_id = 'N/A'
        if not hasattr(record, 'exception'):
            record.exception = ''
        return True

handler = logging.StreamHandler()
handler.addFilter(DefaultContextFilter())
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s User ID:[%(user_id)s] Guild ID:[%(guild_id)s] - '
    '%(message)s %(exception)s'
))

logging.basicConfig(
    encoding='utf-8',
    level=logging.DEBUG,
    handlers=[handler]
)

logging.getLogger('aiosqlite').setLevel(logging.WARNING)


class KamBot(commands.Bot):
    def __init__(self, *args, log_dir: str = 'TextFiles/Logs', **kwargs):
        super().__init__(*args, **kwargs)
        self.db : KamBotDatabase | None = None
        self.kambot_users = {}
        self.log_dir = Path(log_dir)
        self._current_log_date = None
        self.logger = self._createLogger()

    async def addKamBotUsers(self) -> None:
        users = await self.db.fetchUsers()
        for user in users:
            self.addKamBotUser(user)

    def _createLogger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        self._rotateHandlerIfNeeded(logger)
        logging.getLogger('discord').setLevel(logging.WARNING)
        return logger

    def _logFilePath(self) -> Path:
        return self.log_dir / f"{datetime.datetime.now().strftime('%Y-%m-%d')}-kambot.log"

    def _rotateHandlerIfNeeded(self, logger: logging.Logger = None):
        logger = logger or self.logger
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        if today == self._current_log_date:
            return  # already pointing at the right file

        self.log_dir.mkdir(parents=True, exist_ok=True)
        file_path = self._logFilePath()

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s User ID:[%(user_id)s] '
            'Guild ID:[%(guild_id)s] - %(message)s %(exception)s'
        ))
        logger.addHandler(file_handler)
        self._current_log_date = today

    def logInfo(self, user_id: int = 0, guild_id: int = 0, message: str = '', error: str = ''):
        self._rotateHandlerIfNeeded()
        self.logger.info(message, extra=dict(user_id=user_id, guild_id=guild_id, exception=error))

    def logWarning(self, user_id: int = 0, guild_id: int = 0, message: str = '', error: str = ''):
        self._rotateHandlerIfNeeded()
        self.logger.warning(message, extra=dict(user_id=user_id, guild_id=guild_id, exception=error))

    def addKamBotUser(self, user : Users = Users()):
            if user.getKey() not in self.kambot_users:
                self.kambot_users[user.getKey()] = user


    async def addNewKamBotUser(self, player_id: int, guild_id: int, points: int = 75) -> None:
        if self.getUserKey(player_id, guild_id) not in self.kambot_users:
            await self.db.depositUser(player_id, guild_id)
            self.addKamBotUser(Users(player_id, guild_id, points))

    async def addNewGuild(self, guild : discord.Guild):
        await self.db.depositNewGuild(guild.id, guild.name)



    async def fetchKamBotUsers(self) -> list:
        try:
            async with self.pool.acquire() as conn:
                users = await conn.fetch("""
                    SELECT * FROM users ORDER BY guild_id;
                    """)
            return users
        except Exception as e:
            print(f"An error has occurred in getFFUsers: {e}")

    def getUserKey(self, player_id, guild_id):
        return int(f"{player_id}{guild_id}")

    @tasks.loop(minutes=10)
    async def updateKamBotPoints(self):
        for user in self.kambot_users:
            kb_user = self.kambot_users.get(user)
            try:
                await self.db.depositUserPoints(kb_user)
            except Exception as e:
                print(f"The following error has occurred in updateKamBotPoints(): {e}")

    async def setup_hook(self):
        await self.addKamBotUsers()
        self.updateKamBotPoints.start()
        try:
            await self.tree.sync()
        except Exception as e:
            print(f'The following error has occurred: {e}')


    def setPool(self, pool):
        self.pool = pool

async def main():
    try:
        bot = KamBot(command_prefix=["k.", "K."], description="Kambot, for your server's entertainment needs.", intents=getIntents(),
                     application_id=APP_ID)
        cogs = ['Cogs.Events', 'Cogs.Hangman', 'Cogs.FoodFight', 'Cogs.AlphaBot', 'Cogs.Sync']

        db_manager = KamBotDatabase(DBASE_FILE)
        await db_manager.connect()

        bot.db = db_manager

        for cog in cogs:
            await bot.load_extension(cog)

        await bot.start(TOKEN)
    except Exception as e:
        error_stack = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        print(f"The following error has occurred in main(): {str(error_stack)}")
    finally:
        # Ensure the DB closes cleanly when bot.start completes or throws an exception
        if "db_manager" in locals():
            await db_manager.close()

def getIntents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.members = True
    intents.guilds = True
    intents.message_content = True
    return intents


asyncio.run(main())
