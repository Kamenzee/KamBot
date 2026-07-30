# A class specifically created for KamBot's game, AlphaBot.  It stores each guild's game state and stats.
import asyncpg
from typing import Dict


class AlphaBotGuild:
    def __init__(self, guild_id: int = 0,
                 channel_id: int = 0,
                 letter_val: int = -1,
                 game_status: int = 0,
                 last_member: int = 0,
                 last_let_seq: str = '',
                 savepoint: str = '',
                 savepoint_val: int = -1,
                 record_seq: str = '',
                 record_holder: int = 0,
                 record_value: int = 0):
        self.guild_id = guild_id
        self.alphabot_channel_id = channel_id
        self.current_letter_value = letter_val
        self.game_status = game_status
        self.last_accepted_member = last_member
        self.last_letter_sequence = last_let_seq
        self.savepoint_seq = savepoint
        self.savepoint_value = savepoint_val
        self.record_seq = record_seq
        self.record_holder = record_holder
        self.record_value = record_value


    def __str__(self):
        return (f"Guild ID: {self.guild_id}\nChannel ID: {self.alphabot_channel_id}\n"
                f"Letter Value: {self.current_letter_value}\nGame Status: {self.game_status}\n"
                f"Last Accepted Member ID: {self.last_accepted_member}\nLast Letter Sequence: {self.last_letter_sequence}\n"
                f"Savepoint: {self.savepoint_seq}\nSavepoint Value: {self.savepoint_value}\nRecord Seq: {self.record_seq}\nRecord holder: {self.record_holder}\nRecord Value: {self.record_value}\n\n")


    def updateGuildAll(self, guild_id, channel_id, letter_val, game_status, last_member, last_let_seq, savepoint, savepoint_val):
        self.guild_id = guild_id
        self.alphabot_channel_id = channel_id
        self.current_letter_value = letter_val
        self.game_status = game_status
        self.last_accepted_member = last_member
        self.last_letter_sequence = last_let_seq
        self.savepoint_seq = savepoint
        self.savepoint_value = savepoint_val


    def setupABGuild(self, guild_id):
        self.guild_id = guild_id
        self.alphabot_channel_id = 0
        self.current_letter_value = 0
        self.game_status = False
        self.last_accepted_member = 0
        self.last_letter_sequence = ""
        self.savepoint_seq = ""
        self.savepoint_value = -1


    def getRecordValue(self):
        return self.record_value

    def getRecordSeq(self):
        return self.record_seq

    def getRecordHolder(self):
        return self.record_holder

    def getGuildId(self):
        return self.guild_id

    def getChannelId(self):
        return self.alphabot_channel_id

    def getLetterValue(self):
        return self.current_letter_value

    def getGameStatus(self) -> bool:
        return self.game_status

    def getLastAcceptedMember(self):
        return self.last_accepted_member

    def getLastLetterSeq(self):
        return self.last_letter_sequence

    def getSavepointSeq(self):
        return self.savepoint_seq

    def getSavepointVal(self):
        return self.savepoint_value

    # Requires use of the Discord bot to use a pooled connection
    async def setGuildABChannel(self, channel_id):
        self.alphabot_channel_id = channel_id

    def resetGame(self):
        self.game_status = True
        self.last_accepted_member = 0

    def resetFromSave(self):
        self.current_letter_value = self.savepoint_value
        self.game_status = True
        self.last_accepted_member = 0
        self.last_letter_sequence = self.savepoint_seq
        self.savepoint_seq = ""
        self.savepoint_value = -1


    def startNewGame(self):
        self.current_letter_value = 0
        self.game_status = True
        self.last_accepted_member = 0


    def endGame(self):
        self.current_letter_value = 0
        self.game_status = False
        self.last_accepted_member = 0
        self.last_letter_sequence = ""

    def increaseTurn(self, last_member_id, last_letter_seq):
        self.last_accepted_member = last_member_id
        self.last_letter_sequence = last_letter_seq
        self.current_letter_value += 1
        self.updateRecords()

    def updateRecords(self):
        if self.current_letter_value > self.record_value:
            self.record_seq = self.last_letter_sequence
            self.record_value = self.current_letter_value
            self.record_holder = self.last_accepted_member


    def updateSavepoint(self, savepoint_seq, savepoint_val):
        self.savepoint_seq = savepoint_seq
        self.savepoint_value = savepoint_val


    def copyABGuildFrom(self, ab_guild):
        self.guild_id = ab_guild.getGuildId()
        self.alphabot_channel_id = ab_guild.getChannelId()
        self.current_letter_value = ab_guild.getLetterVal()
        self.game_status = ab_guild.getGameStatus()
        self.last_accepted_member = ab_guild.getLastAcceptedMember()
        self.last_letter_sequence = ab_guild.getLastLetterSeq()
        self.savepoint_seq = ab_guild.getSavepointSeq()
        self.savepoint_value = ab_guild.getSavepointVal()

    def gameOn(self) -> bool:
        return self.game_status

    def setGameOff(self) -> None:
        self.game_status = False

    def abChannelSet(self) -> bool:
        if self.alphabot_channel_id != 0:
            return True
        else:
            return False

    def abChannelMatch(self, compare_channel: int) -> bool:
        if self.alphabot_channel_id == compare_channel:
            return True
        else:
            return False


class ABGameManager:
    def __init__(self, ab_guilds_records: tuple, pool: asyncpg.Pool) -> None:
        self.ab_guilds = self.storeGuilds(ab_guilds_records)
        self.pool = pool

    def storeGuilds(self, ab_guilds_records) -> Dict[int, AlphaBotGuild]:
        ab_guilds = {}
        for ab_guild in ab_guilds_records:
            ab_guilds[ab_guilds_records[0]] = AlphaBotGuild(ab_guild[0], ab_guild[1], ab_guild[2], ab_guild[3],
                                                            ab_guild[4], ab_guild[5], ab_guild[6], ab_guild[7])
        return ab_guilds

    def getGuildByID(self, guild_id):
        return self.ab_guilds.get(guild_id)

    def updateGuild(self, ab_guild: AlphaBotGuild):
        self.ab_guilds[ab_guild.getGuildId()] = ab_guild

    def removeGuildFromAB(self, guild_id) -> None:
        del self.ab_guilds[guild_id]
