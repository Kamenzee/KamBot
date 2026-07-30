
class Users:
    def __init__(self, user_id=0, guild_id=0, points=75):
        self.user_id = user_id
        self.guild_id = guild_id
        self.points = points

    def __str__(self):
        return f"User ID: {self.user_id}\n" \
               f"Guild ID: {self.guild_id}\n" \
               f"Points: {self.points}\n"


    def getUserId(self):
        return self.user_id

    def getUserGuildId(self):
        return self.guild_id

    def getUserPoints(self):
        return self.points

    def increasePoints(self, points):
        self.points += points

    def decreasePoints(self, points):
        self.points -= points

    def getKey(self) -> int:
        return int(f"{self.user_id}{self.guild_id}")

