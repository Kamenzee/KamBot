from __future__ import annotations
from datetime import timezone, datetime, timedelta, UTC
import random


class FoodStuffs:
    def __init__(self, food_id, food_type, cost, min_dam, max_dam, art_adj, outcome, cat):
        self.food_id = food_id
        self.food_type = food_type
        self.food_cost = cost
        self.min_damage = min_dam
        self.max_damage = max_dam
        self.art_adj = art_adj
        self.outcomes = outcome
        self.category = cat

    def __str__(self) -> str:
        return (f"Food ID: {self.food_id}\nFood type: {self.food_type}\nCost: {self.food_cost}\n"
                f"Min damage: {self.min_damage}\nMax Damage: {self.max_damage}\nArt_Adj: {self.art_adj}\n"
                f"Outcomes: {self.outcomes}\nCategory: {self.category}\n")

    def getFoodId(self) -> int:
        return self.food_id

    def getFoodType(self) -> str:
        return self.food_type

    def getCost(self) -> int:
        return self.food_cost

    def getMinDamage(self) -> int:
        return self.min_damage

    def getMaxDamage(self) -> int:
        return self.max_damage

    def getArtAdj(self, index) -> str:
        return self.art_adj[index]

    def getOutcomes(self, index) -> str:
        return self.outcomes[index - 1]

    def getCategory(self) -> str:
        return self.category

    def getMinMaxDamage(self) -> list:
        return [self.min_damage, self.max_damage]

    def getInfoInList(self) -> list:
        return [self.food_id, self.food_type, self.food_cost, self.min_damage, self.max_damage, self.art_adj,
                self.outcomes, self.category]

    def getHealthFactor(self) -> int:
        min_damage, max_damage = self.getMinMaxDamage()
        return random.randint(min_damage, max_damage)

    def getArtOutcome(self) -> tuple[str, str]:
        food_desc = random.choices([1, 2], weights=[3, 1])[0]
        return self.getArtAdj(food_desc), self.getOutcomes(food_desc)


class UserInventory:
    def __init__(self):
        self.slot1 = 0
        self.slot2 = 0
        self.slot3 = 0
        self.slot4 = 0
        self.slot5 = 0
        self.slot6 = 0
        self.slot7 = 0
        self.slot8 = 0
        self.slot9 = 0
        self.slot10 = 0

    def __str__(self) -> str:
        return f"Slot 1: {self.slot1}\nSlot 2: {self.slot2}\nSlot 3: {self.slot3}\nSlot 4: {self.slot4}\n" \
               f"Slot 5: {self.slot5}\nSlot 6: {self.slot6}\nSlot 7: {self.slot7}\nSlot 8: {self.slot8}\n" \
               f"Slot 9: {self.slot9}\nSlot 10: {self.slot10}"

    def __iter__(self) -> list:
        for slot, food in self.__dict__.items():
            yield slot, food

    def __contains__(self, food_id) -> bool:
        for food in self:
            if food_id == food[1]:
                return True
        return False

    def __repr__(self):
        string = '{'
        x = 0
        for slot in self:
            if x < 9:
                string += f'{slot[1]}, '
            else:
                string += f'{slot[1]}'
            x += 1
        string += '}'
        return string

    def fillInventory(self, slot1=0, slot2=0, slot3=0, slot4=0, slot5=0, slot6=0, slot7=0, slot8=0,
                      slot9=0, slot10=0) -> None:
        self.slot1 = slot1
        self.slot2 = slot2
        self.slot3 = slot3
        self.slot4 = slot4
        self.slot5 = slot5
        self.slot6 = slot6
        self.slot7 = slot7
        self.slot8 = slot8
        self.slot9 = slot9
        self.slot10 = slot10

    def fillInventoryFromList(self, inv_list) -> UserInventory:
        slot = []
        if inv_list == 0:
            inv_list = []
        x = 0
        while x <= 9:
            if x < len(inv_list):
                slot.append(inv_list[x])
            else:
                slot.append(0)
            x += 1
        self.fillInventory(slot[0], slot[1], slot[2], slot[3], slot[4], slot[5], slot[6], slot[7], slot[8], slot[9])
        return self

    def isInInventory(self, food_id) -> bool:
        for food in self:
            if food[1] == food_id:
                return True
        return False

    def removeFromInventory(self, food_id) -> None:
        if self.isInInventory(food_id):
            for food in self:
                if food[1] == food_id:
                    setattr(self, food[0], 0)
                    self.reformatInventory()
                    return

    def reformatInventory(self) -> None:
        new_inv = []
        for food in self:
            if food[1] != 0:
                new_inv.append(food[1])
        self.fillInventoryFromList(new_inv)

    def getInvList(self) ->str:
        inv_list = []
        for item in self:
            inv_list.append(item[1])
        return str(inv_list)

    def isFull(self):
        for item in self:
            if item[1] == 0:
                return False
        return True

    def addToInventory(self, food_id, amount: int) -> bool:
        try:
            x = 1
            for food in self:
                if food[1] == 0 and x <= amount:
                    setattr(self, food[0], food_id)
                    self.reformatInventory()
                    x += 1
            return True
        except Exception as e:
            print(e)
            return False


    def emptyInventory(self):
        self.fillInventoryFromList([])

    def getNumOfOpenSlots(self):
        open_slots = 0
        for slot in self:
            if slot[1] == 0:
                open_slots += 1
        return open_slots


class FFUser():
    def __init__(self, user_id: int = 0, guild_id: int = 0, health: int = 50,
                 timeout: datetime =
                 datetime(1992, 11, 10, 5, 00, 00, 00, tzinfo=timezone.utc),
                 hits: int = 0, misses: int = 0, c_hits: int = 0, c_misses: int = 0, inv: tuple = (),
                 points_spent: int = 0,
                 points_earned: int = 0, hit_chance: int = 50, exp: int = 0, level: int = 0):
        self.user_id = user_id
        self.guild_id = guild_id
        self.current_health = health
        self.last_timeout_timestamp = timeout
        self.hits = hits
        self.misses = misses
        self.crit_hits = c_hits
        self.crit_misses = c_misses
        self.inventory = UserInventory().fillInventoryFromList(inv)
        self.points_spent_in_FF = points_spent
        self.points_earned_in_FF = points_earned
        self.hit_chance = hit_chance
        self.exp_points = exp
        self.level = level
        self.last_hit = 0
        self.hit_timer = self.createInitialHitTimer()

    def __iter__(self) -> list:
        for att, val in self.__dict__.items():
            yield att, val

    def setUserInfo(self, user_id: int, guild_id: int, health: int, timeout: datetime, hits: int,
                    misses: int, c_hits: int, c_misses: int, inv: list, points_spent: int,
                    points_earned: int) -> FFUser:
        self.user_id = user_id
        self.guild_id = guild_id
        self.current_health = health
        self.last_timeout_timestamp = datetime(timeout.year, timeout.month, timeout.day, timeout.hour, timeout.minute,
                                               timeout.second, tzinfo=timezone.utc)
        self.hits = hits
        self.misses = misses
        self.crit_hits = c_hits
        self.crit_misses = c_misses
        self.inventory = UserInventory().fillInventoryFromList(inv)
        self.points_spent_in_FF = points_spent
        self.points_earned_in_FF = points_earned
        return self

    def __str__(self) -> str:
        return (f"User ID: {self.user_id}\nGuild ID: {self.guild_id}\nCurrent Health: {self.current_health}\n"
                f"Timeout: {self.last_timeout_timestamp}\nHits: {self.hits}\n"
                f"Misses: {self.misses}\nCritical Hits: {self.crit_hits}\nCritical Misses: {self.crit_misses}\n"
                f"Inventory:\n{self.inventory}\nPoints Spent In FF: {self.points_spent_in_FF}\n"
                f"Points Earned In FF: {self.points_earned_in_FF}")

    def createInitialHitTimer(self):
        return datetime.now(timezone.utc) - timedelta(minutes=1)

    def recentlyHit(self) -> bool:
        time = (datetime.now(timezone.utc) - self.hit_timer)
        recently_hit = (datetime.now(timezone.utc) - self.hit_timer) < timedelta(minutes=1)
        return recently_hit

    def setHitTimer(self, new_time: datetime = datetime.now(timezone.utc)) -> None:
        self.hit_timer = new_time

    def getUserId(self) -> int:
        return self.user_id

    def getUserGuildId(self) -> int:
        return self.guild_id

    def getCurrentHealth(self) -> int:
        return self.current_health

    def getLastTimeout(self) -> datetime:
        return self.last_timeout_timestamp

    def getTotalHits(self) -> int:
        return self.hits

    def getTotalMisses(self) -> int:
        return self.misses

    def getTotalCritHits(self) -> int:
        return self.crit_hits

    def getTotalCritMisses(self) -> int:
        return self.crit_misses

    def getInventory(self) -> UserInventory:
        return self.inventory

    def getUserInvList(self) -> str:
        return self.inventory.getInvList()

    def getPointsSpent(self) -> int:
        return self.points_spent_in_FF

    def getPointsEarned(self) -> int:
        return self.points_earned_in_FF

    def getExp(self) -> int:
        return self.exp_points

    def getLevel(self) -> int:
        return self.level

    def getHitChance(self) -> int:
        return self.hit_chance

    def getOpenInvSlots(self):
        return self.inventory.getNumOfOpenSlots()


    def copyFFUserFrom(self, ff_user) -> None:
        self.current_health = ff_user.getCurrentHealth()
        self.last_timeout_timestamp = ff_user.getLastTimeout()
        self.hits = ff_user.getTotalHits()
        self.misses = ff_user.getTotalMisses()
        self.crit_hits = ff_user.getTotalCritHits()
        self.crit_misses = ff_user.getTotalCritMisses()
        self.inventory = ff_user.getInventory()
        self.points_spent_in_FF = ff_user.getPointsSpent()
        self.points_earned_in_FF = ff_user.getPointsEarned()

    def incrementHits(self):
        self.hits += 1

    def incrementCritHits(self):
        self.hits += 1
        self.crit_hits += 1

    def incrementMisses(self):
        self.misses += 1

    def incrementCritMisses(self):
        self.misses += 1
        self.crit_misses += 1

    def doDamage(self, damage) -> int:
        self.current_health -= damage
        return self.current_health

    def resetUser(self):
        self.current_health = 50
        self.exp_points = 0
        self.level = 0
        self.hit_chance = 50
        self.last_timeout_timestamp = datetime.now(timezone.utc)

    def removeFromInventory(self, food_id):
        self.inventory.removeFromInventory(food_id)

    def healUser(self, red_pot_val):
        self.current_health += red_pot_val

    def maxHealth(self):
        self.current_health = 100

    # def getPoints(self):
    #     return self.points
    #
    # def addPoints(self, points):
    #     self.points += points
    #
    # def removePoints(self, points):
    #     if self.points - points < 0:
    #         self.points = 0
    #     else:
    #         self.points -= points

    def spanishFly(self):
        self.last_timeout_timestamp = datetime.now(timezone.utc) - timedelta(minutes=30)

    def addToInventory(self, food_id, amount: int):
        return self.inventory.addToInventory(food_id, amount)

    def escargot(self):
        self.inventory.emptyInventory()

    def frenchToast(self):
        self.current_health = 100

    def addPointsSpent(self, points):
        self.points_spent_in_FF += points

    def addPointsEarned(self, points):
        self.points_earned_in_FF += points

    def updateThrowerHitStats(self, damage):
        self.points_earned_in_FF += damage
        self.incrementHits()

    def increaseExp(self, points: int = 0):
        self.exp_points += points

    def updateLevel(self, level: int = 0):
        self.level = level
        self.setHitChance()

    def setHitChance(self):
        hit_levels = {
            0: 50,
            1: 60,
            2: 70,
            3: 80,
            4: 90
        }
        for hit_level in hit_levels:
            if self.level == hit_level:
                self.hit_chance = hit_levels.get(hit_level)

    def checkForLevel(self, exp: int = 0) -> bool:
        exp_levels = (0, 10, 25, 75, 250)
        initial_xp = self.getExp()
        self.increaseExp(exp)
        new_exp = self.getExp()
        index = 0
        for exp_level in exp_levels:
            if (initial_xp < exp_level) & (new_exp >= exp_level):
                self.updateLevel(index)
                return True
            index += 1
        return False

    def getFormattedDate(self):
        return self.getLastTimeout().strftime('%Y-%m-%d %H:%M:%S%z')

    def getKey(self):
        return int(f"{self.user_id}{self.guild_id}")

    def getAttributesAsList(self) -> list:
        return [
            self.user_id,
            self.guild_id,
            self.current_health,
            self.getFormattedDate(),
            self.hits,
            self.misses,
            self.crit_hits,
            self.crit_misses,
            self.inventory.getInvList(),
            self.points_spent_in_FF,
            self.points_earned_in_FF,
            self.hit_chance,
            self.exp_points,
            self.level
        ]