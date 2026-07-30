import aiosqlite
from Classes.Users import Users
from Classes.AlphaBotHelpers import AlphaBotGuild


class KamBotDatabase:
    def __init__(self, db_file : str) -> None:
        self.db_path = db_file
        self.connection: aiosqlite.Connection | None = None


    async def connect(self):
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row

        await self.connection.execute("PRAGMA foreign_keys = ON;")

        await self.buildTables()

    async def buildTables(self) -> None:
        with open("KamBotFiles/DataFiles/kambot.sqlite.sql", "r") as f:
            sql_script = f.read()

            await self.connection.executescript(sql_script)

    async def close(self):
        if self.connection:
            await self.connection.close()

    async def fetchUsers(self) -> list[Users]:
        users = []
        async with self.connection.execute(
            "SELECT * FROM users ORDER BY guild_id"
        ) as cursor:
            for user_row in await cursor.fetchall():
                user_id_str = str(user_row["user_id"])
                guild_id_str = str(user_row["guild_id"])
                points = user_row["points"]

                users.append(Users(int(user_id_str), int(guild_id_str), points))

        return users


    async def fetchHangmanGuildData(self) -> list[aiosqlite.Row]:
        async with self.connection.execute("""
            SELECT * FROM g_hangman ORDER BY guild_id;
            """) as cursor:
            return await cursor.fetchall()

    async def fetchHangmanUserData(self) -> list[aiosqlite.Row]:
        async with self.connection.execute('''
            SELECT * FROM u_hangman ORDER BY user_id, guild_id;''') as cursor:
            return await cursor.fetchall()

    async def fetchFFUserData(self) -> list[aiosqlite.Row]:
        async with self.connection.execute('''
            SELECT * FROM ff_user_stats ORDER BY user_id, guild_id;''') as cursor:
            return await cursor.fetchall()

    async def fetchABGuildData(self) -> list[aiosqlite.Row]:
        async with self.connection.execute('''
            SELECT * FROM guild_ab_stats ORDER BY guild_id;''') as cursor:
            return await cursor.fetchall()

    async def depositUserPoints(self, user : Users) -> None:
        await self.connection.execute('''
            INSERT INTO users (user_id, guild_id, points) VALUES (?, ?, ?)
            ON CONFLICT (user_id, guild_id) 
            DO UPDATE SET points = excluded.points;''',
              (user.getUserId(), user.getUserGuildId(), user.getUserPoints()))

        await self.connection.commit()

    async def depositABGuildData(self, guild : AlphaBotGuild) -> None:
            await self.connection.execute("""
            INSERT INTO guild_ab_stats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (guild_id) 
            DO UPDATE SET 
            ab_channel = excluded.ab_channel, 
            let_val = excluded.let_val, 
            game_on = excluded.game_on, 
            last_id = excluded.last_id, 
            latest_lets = excluded.latest_lets, 
            savepoint = excluded.savepoint, 
            savepoint_val = excluded.savepoint_val, 
            record_sequence = excluded.record_sequence, 
            record_holder = excluded.record_holder, 
            record_seq_value = excluded.record_seq_value  
            WHERE guild_ab_stats.guild_id = excluded.guild_id;
            """, (int(guild.getGuildId()), int(guild.getChannelId()), guild.getLetterValue(), guild.getGameStatus(),
                  (guild.getLastAcceptedMember()),
                   guild.getLastLetterSeq(), guild.getSavepointSeq(), guild.getSavepointVal(),
                               guild.getRecordSeq(), guild.getRecordHolder(), guild.getRecordValue()))
            await self.connection.commit()

    async def depositBulkHMGuildData(self, guilds : list[list]) -> None:
            await self.connection.executemany("""
             INSERT INTO g_hangman
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
             ON CONFLICT (guild_id)
             DO UPDATE SET 
             guild_hm_word = excluded.guild_hm_word, 
             easy_games_started = excluded.easy_games_started, 
             easy_games_won = excluded.easy_games_won, 
             easy_games_lost = excluded.easy_games_lost, 
             hard_games_started = excluded.hard_games_started, 
             hard_games_won = excluded.hard_games_won, 
             hard_games_lost = excluded.hard_games_lost, 
             cor_let_guesses = excluded.cor_let_guesses, 
             inc_let_guesses = excluded.inc_let_guesses, 
             game_guessed_letters = excluded.game_guessed_letters, 
             game_turn = excluded.game_turn, 
             game_on = excluded.game_on, 
             hm_diff = excluded.hm_diff, 
             starter = excluded.starter, 
             cor_eword_guesses = excluded.cor_eword_guesses, 
             cor_hword_guesses = excluded.cor_hword_guesses, 
             inc_eword_guesses = excluded.inc_eword_guesses, 
             inc_hword_guesses = excluded.inc_hword_guesses;
             """, guilds)
            await self.connection.commit()

    async def depositBulkHMUserData(self, users : list[list]) -> None:
        await self.connection.executemany("""
         INSERT INTO u_hangman
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
         ON CONFLICT (user_id, guild_id) 
         DO UPDATE SET 
         easy_games_started = excluded.easy_games_started,
         hard_games_started = excluded.hard_games_started, 
         cor_let_guesses = excluded.cor_let_guesses, 
         easy_game_wins = excluded.easy_game_wins, 
         hard_game_wins = excluded.hard_game_wins, 
         inc_let_guesses = excluded.inc_let_guesses, 
         easy_game_losses = excluded.easy_game_losses,
         hard_game_losses = excluded.hard_game_losses, 
         points_earned = excluded.points_earned, 
         hm_turns_bought = excluded.hm_turns_bought, 
         cor_eword_guesses = excluded.cor_eword_guesses, 
         cor_hword_guesses = excluded.cor_hword_guesses,
         inc_eword_guesses = excluded.inc_eword_guesses, 
         inc_hword_guesses = excluded.inc_hword_guesses;
         """, users)

        await self.connection.commit()


    async def depositBulkFFUserStats(self, users : list[list]) -> None:
        await self.connection.executemany("""
         INSERT INTO ff_user_stats
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
         ON CONFLICT (user_id, guild_id) 
         DO UPDATE SET 
         health = excluded.health, 
         timeout = excluded.timeout, 
         hits = excluded.hits, 
         misses = excluded.misses, 
         crit_hits = excluded.crit_hits, 
         crit_misses = excluded.crit_misses, 
         inventory = excluded.inventory, 
         points_spent = excluded.points_spent, 
         points_earned = excluded.points_earned, 
         hit_percent = excluded.hit_percent, 
         exp_points = excluded.exp_points, 
         level = excluded.level;
         """, users)

        await self.connection.commit()

    async def depositNewGuild(self, guild_id : int, guild_name : str) -> None:
        await self.connection.execute(
            "INSERT INTO Guilds (guild_id, guild_name) VALUES (?, ?) ON CONFLICT (guild_id) DO NOTHING;",
            (guild_id, guild_name))

        await self.connection.commit()

    async def removeGuild(self, guild_id : int) -> None:

        await self.connection.execute("""
            DELETE FROM guilds WHERE guild_id = ?;
            """, (guild_id,))

        await self.connection.execute("""
            DELETE FROM users WHERE guild_id = ?;
        """, (guild_id,))

        await self.connection.commit()

    async def depositNewHMGuild(self, guild_id : int) -> None:
        await self.connection.execute("""
            INSERT INTO g_hangman (guild_id) VALUES (?);
        """, (guild_id,))

        await self.connection.commit()

    async def depositNewABGuild(self, guild_id : int, ab_channel_id : int) -> None:
        await self.connection.execute("""
            INSERT INTO guild_ab_stats (guild_id, ab_channel) VALUES (?, ?) ON CONFLICT DO NOTHING;
        """, (guild_id, ab_channel_id))

        await self.connection.commit()

    async def depositNewFFUser(self, user_id : int, guild_id : int) -> None:
        await self.depositUser(user_id, guild_id)

        await self.connection.execute("""
            INSERT INTO ff_user_stats (user_id, guild_id) VALUES (?, ?) ON CONFLICT DO NOTHING;
        """, (user_id, guild_id))

        await self.connection.commit()

    async def depositNewHMUser(self, user_id : int, guild_id : int) -> None:
        await self.connection.execute("""
            INSERT INTO u_hangman (user_id, guild_id) VALUES (?, ?) ON CONFLICT DO NOTHING;
        """, (user_id, guild_id))

        await self.connection.commit()

    async def removeUser(self, user_id : int, guild_id : int) -> None:
        await self.connection.execute("""
            DELETE from USERS where user_id = ? and guild_id = ?;
        """, (user_id, guild_id))

        await self.connection.commit()

    async def depositUser(self, user_id : int, guild_id : int) -> None:
        await self.connection.execute("""
            INSERT INTO users (user_id, guild_id) VALUES (?, ?) ON CONFLICT DO NOTHING;
        """, (user_id, guild_id))

        await self.connection.commit()

#https://discord.com/oauth2/authorize?client_id=969290253657575455&permissions=8925867088&integration_type=0&scope=bot