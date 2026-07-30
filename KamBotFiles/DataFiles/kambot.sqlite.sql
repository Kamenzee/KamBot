BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "ff_user_stats" (
	"user_id"	INTEGER,
	"guild_id"	INTEGER,
	"health"	INTEGER DEFAULT 50,
	"timeout"	TEXT DEFAULT '1992-11-10 05:00:00+00:00',
	"hits"	INTEGER DEFAULT 0,
	"misses"	INTEGER DEFAULT 0,
	"crit_hits"	INTEGER DEFAULT 0,
	"crit_misses"	INTEGER DEFAULT 0,
	"inventory"	TEXT DEFAULT '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
	"points_spent"	INTEGER DEFAULT 0,
	"points_earned"	INTEGER DEFAULT 0,
	"hit_percent"	INTEGER DEFAULT 50,
	"exp_points"	INTEGER DEFAULT 0,
	"level"	INTEGER DEFAULT 0,
	PRIMARY KEY("user_id","guild_id"),
	FOREIGN KEY("user_id","guild_id") REFERENCES "users"("user_id","guild_id") ON DELETE CASCADE
) STRICT;
CREATE TABLE IF NOT EXISTS "foodstuffs" (
	"food_id"	INTEGER,
	"foodtype"	TEXT,
	"cost"	INTEGER,
	"min_damage"	INTEGER,
	"max_damage"	INTEGER,
	"art_adj"	TEXT,
	"outcome"	TEXT,
	"category"	TEXT
) STRICT;
CREATE TABLE IF NOT EXISTS "g_hangman" (
	"guild_id"	INTEGER NOT NULL,
	"guild_hm_word"	TEXT DEFAULT '',
	"easy_games_started"	INTEGER DEFAULT 0,
	"easy_games_won"	INTEGER DEFAULT 0,
	"easy_games_lost"	INTEGER DEFAULT 0,
	"hard_games_started"	INTEGER DEFAULT 0,
	"hard_games_won"	INTEGER DEFAULT 0,
	"hard_games_lost"	INTEGER DEFAULT 0,
	"cor_let_guesses"	INTEGER DEFAULT 0,
	"inc_let_guesses"	INTEGER DEFAULT 0,
	"game_guessed_letters"	TEXT DEFAULT '',
	"game_turn"	INTEGER DEFAULT 0,
	"game_on"	INTEGER DEFAULT 0,
	"hm_diff"	INTEGER DEFAULT 0,
	"starter"	INTEGER DEFAULT 0,
	"cor_eword_guesses"	INTEGER DEFAULT 0,
	"cor_hword_guesses"	INTEGER DEFAULT 0,
	"inc_eword_guesses"	INTEGER DEFAULT 0,
	"inc_hword_guesses"	INTEGER DEFAULT 0,
	PRIMARY KEY("guild_id"),
	FOREIGN KEY("guild_id") REFERENCES "guilds"("guild_id") ON DELETE CASCADE
) STRICT;
CREATE TABLE IF NOT EXISTS "guild_ab_stats" (
	"guild_id"	INTEGER,
	"ab_channel"	INTEGER DEFAULT 0,
	"let_val"	INTEGER DEFAULT 0,
	"game_on"	INTEGER DEFAULT 0,
	"last_id"	INTEGER DEFAULT 0,
	"latest_lets"	TEXT DEFAULT '',
	"savepoint"	TEXT DEFAULT '',
	"savepoint_val"	INTEGER DEFAULT 0,
	"record_sequence"	TEXT DEFAULT '',
	"record_holder"	INTEGER DEFAULT 0,
	"record_seq_value"	INT DEFAULT 0,
	PRIMARY KEY("guild_id"),
	FOREIGN KEY("guild_id") REFERENCES "guilds"("guild_id") ON DELETE CASCADE
) STRICT;
CREATE TABLE IF NOT EXISTS "guilds" (
	"guild_id"	INTEGER NOT NULL UNIQUE,
	"guild_name"	TEXT,
	PRIMARY KEY("guild_id")
) STRICT;
CREATE TABLE IF NOT EXISTS "u_hangman" (
	"user_id"	INTEGER,
	"guild_id"	INTEGER,
	"easy_games_started"	INTEGER NOT NULL DEFAULT 0,
	"hard_games_started"	INTEGER NOT NULL DEFAULT 0,
	"cor_let_guesses"	INTEGER NOT NULL DEFAULT 0,
	"easy_game_wins"	INTEGER NOT NULL DEFAULT 0,
	"hard_game_wins"	INTEGER NOT NULL DEFAULT 0,
	"inc_let_guesses"	INTEGER NOT NULL DEFAULT 0,
	"easy_game_losses"	INTEGER NOT NULL DEFAULT 0,
	"hard_game_losses"	INTEGER NOT NULL DEFAULT 0,
	"points_earned"	INTEGER NOT NULL DEFAULT 0,
	"hm_turns_bought"	INTEGER NOT NULL DEFAULT 0,
	"cor_eword_guesses"	INTEGER NOT NULL DEFAULT 0,
	"cor_hword_guesses"	INTEGER NOT NULL DEFAULT 0,
	"inc_eword_guesses"	INTEGER NOT NULL DEFAULT 0,
	"inc_hword_guesses"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("user_id","guild_id"),
	FOREIGN KEY("user_id","guild_id") REFERENCES "users"("user_id","guild_id") ON DELETE CASCADE
) STRICT;
CREATE TABLE IF NOT EXISTS "users" (
	"user_id"	INTEGER NOT NULL,
	"guild_id"	INTEGER NOT NULL,
	"points"	INTEGER DEFAULT 75,
	PRIMARY KEY("user_id","guild_id"),
	FOREIGN KEY("guild_id") REFERENCES "guilds"("guild_id") ON DELETE CASCADE
) STRICT;
COMMIT;
