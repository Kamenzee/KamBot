# FoodFight.py
import asyncio
from typing import Optional, Union, List, Tuple


import asyncpg
import discord
from discord import app_commands
import re
import yaml
from PIL import ImageDraw, Image, ImageFont
from discord.ext import commands, tasks
from Classes.FoodFightHelpers import *
import ast

"""
This Cog/Class is a game designed to allow Discord users to buy, sell, and throw food at one another as well as 
using food
to heal healthpoints.

Author = Mackenzie Carter
Latest version = KamBotV1
Latest Update = 08/31/2023


****** To Do List ******************************************************************************************************
update special food functions to work with new system. - Done
create script to update database every so often. - Done
update users to have levels and exp. - Tentatively Done
 - determine level balance WIP
add methods to complete multiple needed tasks after actions for better readability. - Done, I guess
add bot variable to access and manage points - Done
add error/log handling where needed, log necessary information. - WIP
add hit timer so no one gets spam hit.  Does not need to be stored in DB
************************************************************************************************************************
***************************************
User/Target info contains
[0] - user_id
[1] - guild_id
[2] - current health
[3] - last timeout timestamp
[4] - hits
[5] - misses
[6] - critical hits
[7] - critical misses
[8] - inventory
[9] - points spent in FF
[10] - points earned in FF
[11] - hit percent
[12] - exp
[13] - level
[14] - hit timer (WIP)
[15] - points
*******************************************************
Each food record contains
[0] - ID
[1] - foodtype (apple, pear, fruit juice, etc...)
[2] - cost
[3] - min_damage
[4] - max_damage
[5] - art_adj (an, a rotten), (a box of, a bowl of)
[6] - outcome ("They threw an Appalachia., it stinks")
[7] - category
"""


# Initiates the Cog when the bot loads
class FoodFight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.foods_dict = {}
        self.ff_users = {}
        self.menu_cats = []

    # Defines a function that runs when the Cog is loaded into the bot
    async def cog_load(self) -> None:
        # Creates the contents of the foods_dict dictionary
        await self.getMenu()
        # Separates the foods_dict dictionary into separate food categories for the menu
        self.menu_cats = self.getMenuCategories()
        # Creates the menu page images
        self.getMenuPages()
        self.depositFFUsersAutoSave.start()
        await self.getFFUsers()

    @tasks.loop(minutes=10)
    async def depositFFUsersAutoSave(self):
        ff_users_values_tuple = self.createFFTuple()
        await self.depositFFUsers(ff_users_values_tuple)



    def createFFTuple(self) -> list:
        ff_users = self.ff_users
        ff_list = []
        for user in ff_users:
            ff_list.append(ff_users.get(user).getAttributesAsList())
        return ff_list


    async def depositFFUsers(self, ff_user_list: list) -> bool:
        try:
            await self.bot.db.depositBulkFFUserStats(ff_user_list)
            self.bot.logInfo(0, 0,
                                f'Food Fight stats were successfully updated.')
            return True
        except Exception as e:
            self.bot.logWarning(0, 0,
                                f'Food Fight stats were unable to be updated due to the following error: ', str(e))
            return False

    async def getMenu(self) -> None:
        food_records = self.getFoodStuffsFromFoodFile()
        for food in food_records:
            self.addFoodToFoodDict(food_records.get(food))

    def addFoodToFoodDict(self, food: tuple) -> None:
        self.foods_dict[food[0]] = FoodStuffs(food[0], food[1], food[2], food[3], food[4], food[5], food[6], food[7])

    async def getFFUsers(self) -> None:
        users = await self.bot.db.fetchFFUserData()
        for user in users:
            self.addUserToUserDict(user)

    def addUserToUserDict(self, user_info: asyncpg.Record) -> None:
        user_key = int(f"{user_info[0]}{user_info[1]}")
        timeout = datetime.strptime(user_info[3], "%Y-%m-%d %H:%M:%S%z")
        inv_list = ast.literal_eval(user_info[8])
        new_user = FFUser(user_info[0], user_info[1],
                          user_info[2], timeout, user_info[4], user_info[5], user_info[6], user_info[7],
                          inv_list,
                          user_info[9], user_info[10], user_info[11], user_info[12], user_info[13])
        self.ff_users[user_key] = new_user


    def getFoodStuffsFromFoodFile(self) -> dict:
        try:
            with open(r'KamBotFiles/DataFiles/foodstuff.yaml') as file:
                food_records = yaml.load(file, Loader=yaml.FullLoader)
                file.close()
                return food_records
        except Exception as e:
            print(f"The following error has occurred in getFoodStuffsFromFoodFile(): {e}")

    def getMenuCategories(self) -> tuple:
        foods_dict = self.foods_dict
        botanical = []
        breakfast = []
        dinner = []
        drink = []
        snack = []
        special = []
        free = []
        # This loops through each key in the foods_dict dictionary and sorts them into the proper category list
        # based on the 7th index of the key's value.  See the blockquote at the top of the page for index information.
        for food in foods_dict:
            if foods_dict.get(food).getCategory() == "botanical":
                botanical.append(foods_dict.get(food))
            if foods_dict.get(food).getCategory() == "breakfast":
                breakfast.append(foods_dict.get(food))
            if foods_dict.get(food).getCategory() == "dinner":
                dinner.append(foods_dict.get(food))
            if foods_dict.get(food).getCategory() == "drink":
                drink.append(foods_dict.get(food))
            if foods_dict.get(food).getCategory() == "snack":
                snack.append(foods_dict.get(food))
            if foods_dict.get(food).getCategory() == "special":
                special.append(foods_dict.get(food))
            if foods_dict.get(food).getCategory() == "free":
                free.append(foods_dict.get(food))
        return botanical, breakfast, dinner, drink, snack

    # Defines the function to create the menu pages (images)
    def getMenuPages(self) -> None:
        for cat in self.menu_cats:
            menu_page = Image.open('KamBotFiles/MenuImage/BlankMenu.jpg')
            menu_draw = ImageDraw.Draw(menu_page)
            vertpix = 265
            for food in cat:
                menu_draw.text((25, vertpix), f"""{food.getFoodId()}) {food.getFoodType().capitalize()}
--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- {food.getCost()}""", fill=(225, 225, 225),
                               font=ImageFont.truetype("KamBotFiles/DataFiles/Menuetto.ttf", 55))
                vertpix += 99
            menu_page.save(f"KamBotFiles/MenuImage/{cat[0].getCategory()}Menu.jpg")
        return

    # Defines the help message that describes the detailed instructions for the FoodFight game
    @app_commands.command(name='ffhelp', description='GET SOME HELP!')
    async def ffhelp(self, intr: discord.Interaction) -> None:
        await intr.response.send_message(
"""KamBot's catering will be there for ALL of your food needs.  Run out of food in the school cafeteria?  At KamBot's 
catering most of our employees are still in high school, they're already familiar!  

Contaminated food in your restaurant's kitchen?  KamBot's catering knows ALL about contamination, we'll be there.  

Throwing a party but are too lazy to cook?  KamBot's cooks are always prepared to cut corners to be there and serve 
your guests on time!

Food Fight is a game developed to allow users to do exactly that!  Fight with food!  Everyone starts with 50 health,
however, the maximum health is 100.

To check the menu type "/ffshop".  This allows you to shop for what you want!  To buy the food, type "/ffbuy <food> <amount>". 
You can carry up to 10 items.

Once you have the food in your inventory you can eat it to gain health (up to 100) using "/ffeat <food>".  
The amount of health gained is based on cost

If you're feeling frisky instead of hungry, you can choose to throw the food at another member of the server with 
"/ffthrow"

In the menu, each food has an item number that can also be used to buy, throw, or eat the food.  These numbers have 
no significance other than their relation to the food itself.

When hit with a food, the damage done is *typically* based on the cost.  The amount of damage is how many KamKoins 
you get back from the attack, so throw often!

If your health hits 0, you are unable to throw or be hit for 60 minutes and lose your levels and have your health reset to 50.  
You can still purchase food, so stock up and get payback when you return.  >;)

Some "off menu" items do exist, have fun trying to find them!  These items range from special attacks to **free** 
items that do little or no damage, but hey, they're free!

You can check your stats by typing "/ffstats" and you can see some basic information about how often you hit, miss, 
etc... To check your inventory you can use "/ffinv".

HAVE FUN!  Be prepared for the next games and updates from KamBot!

***EAT ELITE***""")

    # Defines the generic instructions for the ff commands.
    async def ff(self, ctx) -> None:
        response = "Please type 'k.help ff' for detailed instructions or 'k.ffs' to see the menu."
        await ctx.send(response)

    # A command is initiated when the prefix and command name are combined and sent as a message in Discord.
    # Defines the command to "throw" food at another member of the current server
    @app_commands.command(name="ffthrow", description="THROW SOME FOOD!")
    # async def ffThrow(self, interaction: discord.Interaction, *args: tuple) -> None:
    async def ffThrow(self, interaction: discord.Interaction) -> None:
        try:
            throw_menu = FFThrowModal(title='Targeting...')
            await interaction.response.send_modal(throw_menu)
            await throw_menu.wait()
            thrower_id = interaction.user.id
            await self.addNewFFUser(thrower_id, interaction.guild)
            channel = interaction.channel
            food = self.findFoodFromString(throw_menu.food)
            disc_target = await self.getMemberFromChannel(channel, throw_menu.target)
            if disc_target is not None:
                await self.addNewFFUser(disc_target.id, interaction.guild)
            if not await self.passThrowChecks(channel, thrower_id, food, disc_target):
                return
            # if not await self.foodInInventory(food, thrower_id, channel):
            #     return
            else:
                if food.getCategory() == "special":
                    await self.getSpecial(interaction, food, disc_target)
                else:
                    await self.throwActions(interaction.channel, food, disc_target, interaction.user)
        except Exception as error:
            self.bot.logWarning(thrower_id, interaction.guild.id, f"Threw {food.getFoodId()} at user {disc_target.id} and received "
                                                       f"the following error: ", str(error))


    async def passThrowChecks(self, channel: discord.TextChannel,
                              thrower_id: int, food: FoodStuffs, disc_target: discord.Member):
        if not await self.targetFound(disc_target, channel):
            return False
        target_id = disc_target.id
        if await self.targetingSelf(target_id, thrower_id, channel):
            return False
        if not await self.throwReady(thrower_id, target_id, channel):
            return False
        if not await self.foodFound(food, channel, "throw"):
            return False
        if not await self.foodInInventory(food, thrower_id, channel):
            return False
        if await self.targetRecentlyHit(target_id, channel):
            return False
        return True

    async def targetRecentlyHit(self, target_id: int, channel: discord.TextChannel) -> bool:
        target = self.ff_users.get(int(f'{target_id}{channel.guild.id}'))
        if target.recentlyHit():
            await channel.send(f'<@!{target_id}> was JUST hit, don\'t be a troll, you bully.')
            return True
        return False

    async def foodFound(self, food: FoodStuffs, channel: discord.TextChannel, verb: str) -> bool:
        if food is None or not isinstance(food, FoodStuffs):
            await channel.send(f"You might want to see if that's even on the menu before trying to *{verb}* it")
            return False
        return True

    def getUserFromFFUsers(self, user_id: int, guild_id: int) -> FFUser:
        thrower = self.ff_users.get(int(f"{user_id}{guild_id}"))
        if thrower is None:
            thrower = FFUser(user_id, guild_id, 75)
        return thrower

    async def targetingSelf(self, target_id: int, user_id: int, channel: discord.TextChannel) -> bool:
        if target_id == user_id:
            await channel.send(f"You're looking at a mirror, you can't throw food at yourself!  Try eating it "
                               f"with \"/ffeat <food>\" instead.")
            return True
        else:
            return False

    async def targetFound(self, target: discord.Member, channel: discord.TextChannel) -> bool:
        if target is None:
            await channel.send(
                f"You search and search but can't find that target.  Maybe they're hiding in the shadows...  Maybe "
                f"they don't exist...  Maybe you should try again! ")
            return False
        else:
            return True

    async def foodInInventory(self, food: FoodStuffs, user_id: int, channel: discord.TextChannel) -> bool:
        guild_id = channel.guild.id
        thrower = self.getUserFromFFUsers(user_id, guild_id)
        if food.getFoodId() in thrower.getInventory():
            return True
        else:
            await channel.send(f"You do not have that in your inventory. You can buy it using "
                               f"\"/ffbuy <food_string_or_id> <amount>\" or \"/ffshop\" to see what else is on the menu! ")
            return False

    def findFoodFromString(self, food_string: str) -> Optional[FoodStuffs]:
        foods = self.foods_dict
        if self.foodStringIsAlpha(food_string):
            for item in foods:
                if self.foundFood(food_string, foods.get(item).getFoodType()):
                    return foods.get(item)
            return None
        elif food_string.isdigit():
            for item in foods:
                if int(food_string) == item:
                    return foods.get(item)
            return None
        else:
            return None

    def foundFood(self, food_string: str, food_type: str) -> bool:
        return food_string == food_type or bool(re.search(food_string, food_type, re.I))

    def foodStringIsAlpha(self, food_string: str) -> bool:
        return all(x.isalpha() or x.isspace() for x in food_string)

    async def allArgsPresent(self, args: tuple, channel: discord.TextChannel) -> bool:
        if len(args) < 3:
            await channel.send(
                f"You fumble through your inventory when something hits you - and it's not food this time.  You can't "
                f"shake the feeling that you forgot something.")
            return False
        else:
            return True


    def separateFoodAndTarget(self, args: tuple) -> tuple:
        pass


    def getFoodFromMessage(self, food_str: str) -> FoodStuffs:
        return self.findFoodFromString(food_str)

    def getFoodStringFromMessage(self, food_tuple: tuple):
        food_name = ''
        for food in food_tuple:
            food_name += ''.join(food) + ' '
        return food_name.strip()

    async def getDiscTargetFromMessage(self, target_str: str, channel: discord.TextChannel) -> discord.Member:
        member = await self.getMemberFromChannel(channel, target_str)
        return member

    def getTargetString(self, name_tuple: tuple) -> str:
        target_name = ''
        for name in name_tuple:
            target_name += ''.join(name) + ' '
        return target_name.strip()


    # Defines the function to "do damage" to the target player
    async def throwActions(self, channel: discord.TextChannel, food: FoodStuffs, disc_target: discord.Member,
                           disc_thrower: discord.Member) -> None:
        guild_id = channel.guild.id
        target_id = disc_target.id
        thrower_id = disc_thrower.id
        food_type = food.getFoodType()
        attack_damage = food.getHealthFactor()
        thrower_name = self.getDiscUserName(disc_thrower)
        target = self.getUserFromFFUsers(target_id, guild_id)
        thrower = self.getUserFromFFUsers(thrower_id, guild_id)
        article, outcome = food.getArtOutcome()
        thrower.removeFromInventory(food.getFoodId())
        if self.targetIsHit(thrower.getHitChance()):
            if not self.isCrit():
                self.hitTarget(target, thrower, attack_damage)
                await channel.send(
                    f"<@!{thrower_id}>threw {article} {food_type} at <@!{target_id}>!"
                    f" {outcome.capitalize()} {attack_damage} damage was dealt. ")
                self.bot.logInfo(thrower_id, guild_id, f'Hit {target_id} for {attack_damage} damage.')
            else:
                attack_damage *= 2
                self.critHitTarget(target, thrower, attack_damage)
                await channel.send(
                    f"{thrower_name}, with perfect poise and posture absolutely launched {article}"
                    f" {outcome} at {disc_target.mention} for a critical hit!  {attack_damage} damage was "
                    f"dealt. ")
                self.bot.logInfo(thrower_id, guild_id, f'Critically hit {target_id} for {attack_damage} damage.')
            await self.targetHealthChecks(target, disc_target, channel)
            await self.updateUserExp(channel, thrower.getUserId(), thrower.getUserGuildId(), attack_damage)

        else:
            if not self.isCrit():
                self.missTarget(thrower)
                await channel.send(f"{thrower_name} threw {article} {food_type} at "
                                   f"{disc_target.mention} and missed!")
                self.bot.logInfo(thrower_id, guild_id, f'Missed {target_id}.')
            else:
                self.critMiss(thrower, attack_damage)
                await channel.send(
                    f"While throwing {article} {food_type} at {disc_target.mention}, "
                    f"{thrower_name} slipped on a banana peel and took {attack_damage} damage.  Adding insult to "
                    f"injury, the attack also missed.")
                self.bot.logInfo(thrower_id, guild_id, f'Critically missed {target_id} and took {attack_damage} damage.')
            await self.throwerHealthChecks(thrower, thrower_name, channel)


    async def updateUserExp(self, channel: discord.TextChannel, user_id: int, guild_id: int, exp: int) -> None:
        user = self.getUserFromFFUsers(user_id, guild_id)
        if user.checkForLevel(exp):
            await channel.send(f'Whoa!  <@!{user.getUserId()}> leveled up!  You are now level {user.getLevel()} and '
                               f'have a {user.getHitChance()}% chance of hitting your targets!')
            self.bot.logInfo(user_id, guild_id, f'Leveled to level {user.getLevel()}')
        self.updateUserInFFDict(user)



    def getArtOutcome(self, food: FoodStuffs) -> Tuple[str, str]:
        food_desc = self.getFoodDescriptors()
        return food.getArtAdj(food_desc), food.getOutcomes(food_desc)

    def getAttackDamage(self, food: FoodStuffs) -> int:
        min_damage, max_damage = food.getMinMaxDamage()
        return random.randint(min_damage, max_damage)

    async def throwerHealthChecks(self, thrower: FFUser, thrower_name: str, channel: discord.TextChannel) -> None:
        if thrower.getCurrentHealth() <= 0:
            thrower.resetUser()
            self.updateUserInFFDict(thrower)
            await channel.send(
                f"Oh no!  {thrower_name} hurt itself in its confusion and needs to take a break!")
            self.bot.logInfo(thrower.getUserId(), thrower.getUserGuildId(), f'Timed out.')

    async def targetHealthChecks(self, target: FFUser, disc_target: discord.Member, channel: discord.TextChannel) -> None:
        if target.getCurrentHealth() <= 0:
            target.resetUser()
            self.updateUserInFFDict(target)
            await channel.send(
                f"Oh no! {disc_target.mention}'s health hit zero!  They had a breakdown and ran to the shower to clean "
                f"up.")
            self.bot.logInfo(target.getUserId(), target.getUserGuildId(), f'Timed out.')

    def updateUserInFFDict(self, ff_user: FFUser) -> None:
        user_key = self.getFFUserKey(ff_user)
        self.ff_users[user_key] = ff_user

    def getDiscUserName(self, disc_user: discord.Member) -> str:
        if disc_user.nick is None:
            return disc_user.name
        else:
            return disc_user.nick

    def targetIsHit(self, hit_chance: int = 50) -> bool:
        return random.choices([1,0], cum_weights=[hit_chance, 100])[0]

    def isCrit(self) -> int:
        return random.choices([1, 0], cum_weights=[10, 90])[0]

    def getFoodDescriptors(self) -> int:
        return random.choices([1, 2], weights=[3, 1])[0]

    def hitTarget(self, target: FFUser, thrower: FFUser, damage: int) -> None:
        thrower.updateThrowerHitStats(damage)
        target.doDamage(damage)
        target.setHitTimer(datetime.now(timezone.utc))
        self.increasePointsForUser(thrower, damage)
        self.updateFoodDictThrowerAndTarget(thrower, target)

    def increasePointsForUser(self, ff_user, points):
        key = ff_user.getKey()
        self.bot.kambot_users.get(key).increasePoints(points)

    def critHitTarget(self, target: FFUser, thrower: FFUser, damage: int) -> None:
        thrower.incrementCritHits()
        self.increasePointsForUser(thrower, damage)
        target.doDamage(damage)
        target.setHitTimer(datetime.now(timezone.utc))
        self.updateFoodDictThrowerAndTarget(thrower, target)

    def updateFoodDictThrowerAndTarget(self, thrower: FFUser, target: FFUser) -> None:
        thrower_key, target_key = self.getThrowerTargetKeys(thrower, target)
        self.ff_users[thrower_key] = thrower
        self.ff_users[target_key] = target

    def getThrowerTargetKeys(self, thrower: FFUser, target: FFUser) -> Tuple[int, int]:
        return self.getFFUserKey(thrower), self.getFFUserKey(target)

    def getFFUserKey(self, ff_user: FFUser) -> int:
        return int(f"{ff_user.getUserId()}{ff_user.getUserGuildId()}")

    def missTarget(self, thrower: FFUser) -> None:
        thrower.incrementMisses()
        self.updateUserInFFDict(thrower)

    def critMiss(self, thrower: FFUser, damage: int) -> None:
        thrower.incrementCritMisses()
        thrower.doDamage(damage)
        self.updateUserInFFDict(thrower)

    #  *************************** Special Foots Defined **************************************************************
    # Special Foods perform actions that are not compatible with a standard damage model.  Their attacks are more
    # sophisticated and unique.
    # *****************************************************************************************************************
    async def getSpecial(self, interaction: discord.Interaction, food: FoodStuffs, target: discord.Member) -> None:
        funct_dict = {}
        if food.getFoodType().isalpha():
            funct_dict[f"{food.getFoodType()}"] = eval(f"self.{food.getFoodType()}")
            await funct_dict[f'{food.getFoodType()}'](interaction, target)
        else:
            food_funct = ""
            for character in food.getFoodType():
                if character.isalpha():
                    food_funct += character
                elif character.isspace():
                    food_funct += "_"
            funct_dict[f"{food_funct}"] = eval(f"self.{food_funct}")
            await funct_dict[f"{food_funct}"](interaction, target)

    async def surstromming(self, intr: discord.Interaction, target: discord.Member) -> None:
        thrower_name = self.getDiscUserName(intr.user)
        self.surstrommingActions(intr.user.id, intr.guild.id)
        await intr.channel.send(
            f"{thrower_name} stands menacingly donned in a hazmat suit and respirator weilding something resembling "
            f"a bulging can of sardines.  Shakily, fingers clasp around the pulltab.  No one can look away at the "
            f"spectacle unfolding. The scene of pure, unmitigated oddness turns into fear, confusion, and "
            f"hopelessness as the tab pops.  Everyone's nostrils are assaulted with the pungent stench of "
            f"surstr\xF6mming.  Death is preferable to the inhalation of such a loathsome fetor.  Everyone in the "
            f"server food fight rushes to clean the wretched stench from their being. The "
            f"target of the attack was {target.mention}, this was a bit excessive.")

    def surstrommingActions(self, thrower_id: int, guild_id: int) -> None:
        thrower = self.getUserFromFFUsers(thrower_id, guild_id)
        thrower.incrementCritHits()
        thrower.removeFromInventory(99)
        self.timeoutCurrentGuild(thrower_id, guild_id)

    def timeoutCurrentGuild(self, thrower_id: int, guild_id: int) -> None:
        for user in self.ff_users:
            if user == int(f"{thrower_id}{guild_id}"):
                pass
            elif self.ffUserMemberOfGuild(user, guild_id):
                user = self.ff_users.get(user)
                user.resetUser()
                self.updateUserInFFDict(user)
            else:
                pass

    def ffUserMemberOfGuild(self, user_key: int, guild_id: int) -> bool:
        return bool(re.search(f'{guild_id}$', str(user_key)))

    async def escargot(self, intr: discord.Interaction, disc_target: discord.Member) -> None:
        target_id = disc_target.id
        guild_id = intr.guild.id
        user_name = self.getDiscUserName(intr.user)
        self.escargotActions(intr.user.id, target_id, guild_id)
        await intr.channel.send(
            f"{user_name}, with a small styrofoam box in hand, grins from ear to ear.  This is no ordinary "
            f"grin, this is one that says \"Hey, I''m about to mess your day up.\"   This is the "
            f"kind of grin that could make a snail recoil in disgust of the thoughts making "
            f"their way through the grinner''s mind.  Coincidentally, when the box is opened "
            f"that's exactly what slimes out - uncooked escargot.  They menacingly make their "
            f"way towards the target who is unable to move from the fear being invoked my the "
            f"gaze of the stemmed eyes directed at them.  These snails are trained, these snails "
            f"are deadly, these snails are... hungry.  {disc_target.mention}, all of the items in your inventory "
            f"have been eaten. The snails depart with full bellies leaving you with an empty inventory.")

    def escargotActions(self, thrower_id: int, target_id: int, guild_id: int) -> None:
        thrower = self.getUserFromFFUsers(thrower_id, guild_id)
        target = self.getUserFromFFUsers(target_id, guild_id)
        target.escargot()
        thrower.removeFromInventory(75)
        thrower.incrementCritHits()
        self.updateFoodDictThrowerAndTarget(thrower, target)

    async def french_toast(self, intr: discord.Interaction, target: discord.Member) -> None:
        thrower_name = self.getDiscUserName(intr.user)
        self.frenchToastActions(intr.user.id, target.id, intr.guild.id)
        ft_message = await intr.channel.send(
            f"{thrower_name} looks at {target.mention} with love.  {thrower_name}'s passion for you keeps them up at night, thinking "
            f"of the wonderful things that can be done for you, how to make you smile, how to ensure your safety, what "
            f"the future holds for you and your dreams.  Dreams are blessed with your appearance often and your very "
            f"existence is appreciated.  To show you love, {thrower_name} sits in front of you with a plate of BEAUTIFULLY "
            f"cooked slices of French toast, one of God's gifts to mankind.  Gingerly, they feed you the first bite "
            f"and....  It was like your very soul left your body to walk through the gates of Heaven.  The texture, "
            f"the flavor, the feeling.  This act of love and kindness has put you at 100/100 health.  Be sure to say "
            f"thanks!  ")
        reactions = ["\U00002764"]
        for reaction in reactions:
            await ft_message.add_reaction(reaction)

    def frenchToastActions(self, thrower_id: int, target_id: int, guild_id: int) -> None:
        thrower = self.getUserFromFFUsers(thrower_id, guild_id)
        target = self.getUserFromFFUsers(target_id, guild_id)
        target.frenchToast()
        thrower.incrementCritHits()
        thrower.removeFromInventory(77)
        self.updateFoodDictThrowerAndTarget(thrower, target)

    async def spanish_fly(self, intr: discord.Interaction, target: discord.Member) -> None:
        self.spanishFlyActions(target.id, intr.guild.id, intr.user.id)
        sp_message = await intr.channel.send(
            f"{intr.user.mention}, with a smirk and gloved hand winks.  After a deep inhale, they blow a powdery "
            f"substance that creates a cloud around someone like a dense fog. It's hard to make out what's going on, "
            f"it enveloped you, {target.mention}, blurring your vision and stirring something up inside you.  Your "
            f"blood pressure rises, you begin to sweat, you moan as the feeling bursts through your body.  You don't "
            f"know what just happened but you need to leave, immediately!  A cloud of powdered Spanish fly entered your "
            f"lungs and penetrated your bloodstream leaving you feeling *empty* inside.  You rush out of the room to "
            f"take a cold shower, come back in 30 minutes.")
        reactions = ["\U0001F975", "\U0001F346", "\U0001F4A6"]
        for reaction in reactions:
            await sp_message.add_reaction(reaction)

    def spanishFlyActions(self, target_id: int, guild_id: int, thrower_id: int) -> None:
        target = self.getUserFromFFUsers(target_id, guild_id)
        thrower = self.getUserFromFFUsers(thrower_id, guild_id)
        thrower.incrementCritHits()
        thrower.removeFromInventory(69)
        target.spanishFly()
        self.updateFoodDictThrowerAndTarget(thrower, target)

    # Defines the function for the special food teabag
    async def teabag(self, intr: discord.Interaction, target: discord.Member) -> None:
        thrower_name = self.getDiscUserName(intr.user)
        self.teabagActions(intr.user.id, intr.guild.id)
        await intr.channel.send(
            f"{thrower_name} teabagged {target.mention}.  It doesn't do anything at all, but it showed them who's boss.")

    def teabagActions(self, thrower_id: int, guild_id: int) -> None:
        thrower = self.getUserFromFFUsers(thrower_id, guild_id)
        thrower.removeFromInventory(88)
        thrower.incrementCritHits()
        self.updateUserInFFDict(thrower)

    # ********************************** End Special Foods *************************************************************

    async def throwReady(self, thrower_id: int, target_id: int, channel: discord.TextChannel) -> bool:
        if await self.timedOutThrower(thrower_id, channel):
            return False
        if await self.timedOutTarget(target_id, channel):
            return False
        else:
            return True

    async def timedOutThrower(self, thrower_id: int, channel: discord.TextChannel) -> bool:
        thrower = self.getUserFromFFUsers(thrower_id, channel.guild.id)
        mins_left, secs_left = self.getFFUserTimeoutVal(thrower.getLastTimeout())
        if mins_left > 0 or secs_left > 0:
            await channel.send(
                f"Uh oh! You're still scrubbing the mashed potatoes out of your eyes, you can throw again in "
                f"{round(mins_left)} minutes and {round(secs_left)} seconds.")
            return True
        else:
            return False

    async def timedOutTarget(self, target_id: int, channel: discord.TextChannel) -> bool:
        target = self.getUserFromFFUsers(target_id, channel.guild.id)
        mins_left, secs_left = self.getFFUserTimeoutVal(target.getLastTimeout())
        if mins_left > 0 or secs_left > 0:
            await channel.send(
                f"Pfffft!  <@!{target.getUserId()}> is cowering in a corner somewhere, let's give them a break "
                f"lasting precisely another {round(mins_left)} minutes and "
                f"{round(secs_left)} seconds..")
            return True
        else:
            return False

    def timeLeftInTO(self, mins: int, secs: int) -> Tuple[int, int]:
        if mins < 60:
            mins_left = 59 - mins
            secs_left = 60 - secs
        else:
            mins_left = 00
            secs_left = 00
        return int(mins_left), int(secs_left)

    def getFFUserTimeoutVal(self, timeout: datetime) -> Tuple[int, int]:
        user_TO_secs = (datetime.now(timezone.utc) - timeout).total_seconds()
        user_mins, user_secs = divmod(user_TO_secs, 60)
        mins_left, secs_left = self.timeLeftInTO(round(user_mins), round(user_secs))
        return mins_left, secs_left

    async def getMemberFromChannel(self, ff_channel: discord.TextChannel, member_str: str) -> discord.Member:
        member = None
        for member_data in ff_channel.members:
            if self.memberFound(member_data, member_str):
                member = member_data
                break
        return member

    def memberFound(self, member_data: discord.Member, member_str: str) -> bool:
        return bool(re.search(member_str,
                              str(member_data.nick), re.I) or re.search(member_str, str(member_data.name), re.I))

    async def addNewFFUser(self, user_id: int, guild: discord.Guild) -> None:
        user_key = int(f'{user_id}{guild.id}')
        if user_key not in self.ff_users:
            await self.bot.addNewGuild(guild)
            await self.bot.db.depositNewFFUser(user_id, guild.id)
            await self.bot.addNewKamBotUser(user_id, guild.id)
            self.ff_users[user_key] = FFUser(user_id, guild.id)



    @app_commands.command(name="ffeat",
                          description="EAT SOME FOOD!")
    async def eat(self, intr: discord.Interaction, food: str) -> None:
        await intr.response.send_message('EATING SOME FOOD...')
        user_id = intr.user.id
        await self.addNewFFUser(user_id, intr.guild)
        channel = intr.channel
        food_obj = self.findFoodFromString(food)
        if not await self.passEatChecks(food_obj, user_id, channel):
            return
        else:
            await self.gainHealth(channel, food_obj, user_id)

    def getFoodOnlyFromMessage(self, arg: tuple) -> FoodStuffs:
        food_string = " ".join(arg).lower()
        return self.findFoodFromString(food_string)

    async def passEatChecks(self, food: FoodStuffs, user_id: int, channel: discord.TextChannel) -> bool:
        if not await self.foodFound(food, channel, "eat"):
            return False
        if not await self.foodInInventory(food, user_id, channel):
            return False
        if await self.foodIsSpecial(food, channel):
            return False
        if await self.userAtMaxHealth(channel, user_id):
            return False
        return True

    async def userAtMaxHealth(self, channel: discord.TextChannel, user_id: int) -> bool:
        guild_id = channel.guild.id
        eater = self.getUserFromFFUsers(user_id, guild_id)
        if eater.getCurrentHealth() == 100:
            await channel.send(f"You are already at max health, if you eat another bite you might burst!")
            return True
        return False

    async def foodIsSpecial(self, food: FoodStuffs, channel: discord.TextChannel) -> bool:
        if food.getCategory() == "special":
            await channel.send(f"This is a very special item, don't waste it by eating it.")
            return True
        else:
            return False

    # Defines the function to add reactions to the confirmation message for the gain_health() function.
    async def confirmEat(self, channel: discord.TextChannel, food: FoodStuffs, eat_yn: discord.Message, author_id: int) -> bool:
        foodtype = food.getFoodType()
        art_adj = food.getArtAdj(0)
        con_deny = ["\U00002705", "\U0000274E"]
        for react in con_deny:
            await eat_yn.add_reaction(react)
        def check(reaction, user):
            return user.id == author_id and str(reaction.emoji) in con_deny and reaction.message == eat_yn
        try:
            confirmation = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            for r in con_deny:
                await eat_yn.clear_reaction(r)
            await channel.send(f"{art_adj.capitalize()} {foodtype} was not eaten.")
            confirmation = None
        try:
            emoji = confirmation[0]
        except UnboundLocalError:
            emoji = None
        if str(emoji) == "\U0000274E":
            return False
        elif str(emoji) == "\U00002705":
            return True

    # Defines the function to allow a user to gain health.
    async def gainHealth(self, channel: discord.TextChannel, food: FoodStuffs, eater_id: int):
        guild_id = channel.guild.id
        eater = self.getUserFromFFUsers(eater_id, guild_id)
        healing_factor = food.getHealthFactor()  # Uses the same values as attack damage to determine healing factor
        cur_health = eater.getCurrentHealth()
        if self.getNewHealth(cur_health, healing_factor) <= 100:
            await self.healUser(eater, healing_factor, channel, food)
        elif self.getNewHealth(cur_health, healing_factor) > 100:
            if await self.confirmHeal(channel, eater, food, healing_factor):
                eater.maxHealth()
                eater.removeFromInventory(food.getFoodId())
                self.updateUserInFFDict(eater)
                await channel.send(f"You are now at 100/100 health!  You have an appetite worthy of the Gods.")

    async def confirmHeal(self, channel: discord.TextChannel, eater: FFUser, food: FoodStuffs, healing_factor: int) -> bool:
        waste_food = self.getWasteFood(healing_factor, eater.getCurrentHealth())
        eat_yn = await channel.send(
            f"You are so full you can hardly eat another bite! {waste_food} food will be wasted, is that okay?")
        eat_yn_TF = await self.confirmEat(channel, food, eat_yn, eater.getUserId())
        if not eat_yn_TF:
            await channel.send(f"{food.getFoodType().capitalize()} was not consumed.  Maybe try a smaller meal?")
            return False
        else:
            return True

    def getWasteFood(self, red_pot: int, current_health: int) -> int:
        return (red_pot + current_health) - 100

    async def healUser(self, eater: FFUser, health: int, channel: discord.TextChannel, food: FoodStuffs) -> None:
        eater.healUser(health)
        eater.removeFromInventory(food.getFoodId())
        self.updateUserInFFDict(eater)
        await channel.send(
            f"You ingested {food.getArtAdj(0)} {food.getFoodType()} and gained {health} health!  Your current health "
            f"is {eater.getCurrentHealth()}/100.")

    def getNewHealth(self, cur_health: int, healing_factor: int) -> int:
        return cur_health + healing_factor

    @app_commands.command(name="ffbuy",
                          description="BUY SOME FOOD!")
    async def ffBuy(self, intr: discord.Interaction, food: str, amount: int) -> None:
        await intr.response.send_message('BUYING SOME FOOD!')
        user_id = intr.user.id
        guild_id = intr.guild.id
        await self.addNewFFUser(user_id, intr.guild)
        channel = intr.channel
        food_obj = self.findFoodFromString(food)
        buyer = self.getUserFromFFUsers(user_id, guild_id)
        if not await self.passBuyChecks(channel, buyer, food_obj, amount):
            return
        else:
            await self.buyActions(channel, buyer, food_obj, amount)

    async def buyActions(self, channel: discord.TextChannel, buyer: FFUser, food: FoodStuffs, amount: int) -> None:
        food_type = food.getFoodType()
        if await self.buyConfirmed(channel, buyer, food, amount):
            if buyer.addToInventory(food.getFoodId(), amount):
                self.updateBuyer(buyer, food, amount)
                await channel.send(f"{amount} serving(s) of {food_type.capitalize()} added to your inventory!")
                return
            else:
                await channel.send(f"Something went wrong adding {food_type} to inventory.")
        else:
            await channel.send(f"{food_type.capitalize()} was not added.")

    def updateBuyer(self, buyer: FFUser, food: FoodStuffs, amount: int = 1) -> None:
        cost = food.getCost() * amount
        buyer.addPointsSpent(cost)
        self.decreasePointsForUser(buyer, cost)
        self.updateUserInFFDict(buyer)

    def decreasePointsForUser(self, ff_user, points):
        key = ff_user.getKey()
        self.bot.kambot_users.get(key).decreasePoints(points)

    async def buyConfirmed(self, channel, buyer: FFUser, food: FoodStuffs, amount: int) -> bool:
        con_message = await channel.send(
            f"Are you sure you want to buy {amount} serving(s) of {food.getFoodType()} for {food.getCost() * amount} KamKoins?")
        if not await self.confirmBuy(con_message, buyer.getUserId()):
            return False
        return True

    async def passBuyChecks(self, channel: discord.TextChannel, buyer: FFUser, food: FoodStuffs, amount: int):
        if not await self.foodFound(food, channel, "buy"):
            return False
        if await self.inventoryIsFull(channel, buyer.getInventory()):
            return False
        if await self.notEnoughInventorySpace(channel, buyer, amount):
            return False
        if not await self.buyerHasEnoughPoints(channel, buyer, food, amount):
            return False
        return True

    async def notEnoughInventorySpace(self, channel: discord.TextChannel, buyer: FFUser, amount: int):
        if buyer.getOpenInvSlots() < amount:
            await channel.send(f'You only have {buyer.getOpenInvSlots()} open inventory spaces!  Slow it down,'
                               f' Rockefeller.')
            return True
        return False

    async def inventoryIsFull(self, channel: discord.TextChannel, buyer_inv: UserInventory) -> bool:
        if buyer_inv.isFull():
            await channel.send(f"Your inventory is already full!  Save some food for everyone else, hoarder!")
            return True
        return False

    async def buyerHasEnoughPoints(self, channel: discord.TextChannel, buyer: FFUser, food: FoodStuffs, amount: int = 1) -> bool:
        buyer_points = self.getUserPoints(buyer)
        food_cost = food.getCost() * amount
        if buyer_points < food_cost:
            await channel.send(f"You don't have enough KamKoins to purchase {amount} serving(s) of {food.getFoodType()}.  You only have "
                               f"{buyer_points} and the food costs {food_cost} KamKoins.")
            return False
        return True

    def getUserPoints(self, ff_user: FFUser):
        key = ff_user.getKey()
        return self.bot.kambot_users.get(key).getUserPoints()

    # Defines the function to allow the user to confirm the choice to buy a food
    async def confirmBuy(self, con_message: discord.Message, buyer_id: int) -> bool:
        con_deny = ["\U00002705", "\U0000274E"]
        for react in con_deny:
            await con_message.add_reaction(react)
        def check(reaction, user):
            return user.id == buyer_id and str(reaction.emoji) in con_deny and reaction.message == con_message
        try:
            confirmation = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            for r in con_deny:
                await con_message.clear_reaction(r)
            return False
        try:
            emoji = confirmation[0]
        except UnboundLocalError:
            emoji = None
        if str(emoji) == "\U0000274E":
            return False
        elif str(emoji) == "\U00002705":
            return True




    # A command is initiated when the prefix and command name are combined and sent as a message in Discord.
    @app_commands.command(name="ffinv",
                          description="CHECK YOUR FOOD!")
    # Defines the function to show a user the items in their inventor
    async def ShowInventory(self, intr: discord.Interaction) -> None:
        user_name = self.getDiscUserName(intr.user)
        user_id = intr.user.id
        guild_id = intr.guild.id
        await self.addNewFFUser(user_id, intr.guild)
        ff_user = self.getUserFromFFUsers(user_id, guild_id)
        await self.sendInventory(intr, ff_user, user_name)

    async def sendInventory(self, intr: discord.Interaction, ff_user: FFUser, user_name: str) -> None:
        inv_embed = discord.Embed(title=f"{user_name}'s Inventory")
        inv_embed.add_field(name="KamKoins", value=f"{self.getUserPoints(ff_user)}", inline=False)
        inv_embed = self.addEmbedInventorySlots(inv_embed, ff_user.getInventory())
        await intr.response.send_message(embed=inv_embed)

    def getUserPoints(self, ff_user: FFUser) -> int:
        return self.bot.kambot_users.get(self.getFFUserKey(ff_user)).getUserPoints()

    def addEmbedInventorySlots(self, inv_embed: discord.Embed, user_inv: UserInventory) -> discord.Embed:
        for food in user_inv:
            slot = food[0]
            food = self.getFoodFromFoodsDict(food[1])
            if food is None:
                food_type = "empty"
            else:
                food_type = food.getFoodType()
            inv_embed.add_field(name=slot, value=food_type.capitalize())
        return inv_embed

    def getFoodFromFoodsDict(self, food_id: int) -> Union[str, FoodStuffs]:
        return self.foods_dict.get(food_id)

    # A command is initiated when the prefix and command name are combined and sent as a message in Discord.
    @app_commands.command(name="ffstats",
                          description="GET YOUR RECEIPT!")
    # Defines the function to allow a user to see their stats for the FF game
    async def showStats(self, intr: discord.Interaction) -> None:
        user_id = intr.user.id
        guild_id = intr.guild.id
        await self.addNewFFUser(user_id, intr.guild)
        ff_user = self.getUserFromFFUsers(user_id, guild_id)
        name = self.getDiscUserName(intr.user)
        stats_embed = discord.Embed(title=f"{name}'s Food Fight Stats")
        stats_embed = self.addEmbedStatSlots(stats_embed, ff_user)
        await intr.response.send_message(embed=stats_embed)

    def addEmbedStatSlots(self, stats_embed: discord.Embed, ff_user: FFUser) -> discord.Embed:
        mins_left, secs_left = self.getFFUserTimeoutVal(ff_user.getLastTimeout())
        points = self.getUserPoints(ff_user)
        stats_embed.add_field(name=f"Points", value=f"{points}")
        stats_embed.add_field(name=f"Health", value=f"{ff_user.getCurrentHealth()}")
        stats_embed.add_field(name=f"Timeout remaining", value=f"{mins_left}:{'0' if secs_left < 10 else ''}{secs_left}")
        stats_embed.add_field(name=f"Total hits", value=f"{ff_user.getTotalHits()}")
        stats_embed.add_field(name=f"Total Misses", value=f"{ff_user.getTotalMisses()}")
        stats_embed.add_field(name=f"Total Critical Hits", value=f"{ff_user.getTotalCritHits()}")
        stats_embed.add_field(name=f"Total Critical Misses", value=f"{ff_user.getTotalCritMisses()}")
        stats_embed.add_field(name=f"Total Points Spent in FF", value=f"{ff_user.getPointsSpent()}")
        stats_embed.add_field(name=f"Total Points Earned in FF", value=f"{ff_user.getPointsEarned()}")
        return stats_embed

    @app_commands.command(name="ffshop",
                          description="SEE SOME FOOD!")
    async def showMenu(self, intr: discord.Interaction, text_version: bool=False) -> None:
        await self.addNewFFUser(intr.user.id, intr.guild)
        menu_embed = discord.Embed(title=f"KamBot's Menu")
        menu_image = discord.File(f"KamBotFiles/KambotMenu.jpg", filename=f"imageKambotMenu.jpg")
        menu_embed.set_image(url="attachment://imageKambotMenu.jpg")
        view = Buttons(self.bot, self.menu_cats, text_version)
        view.message = await intr.response.send_message(file=menu_image, embed=menu_embed, view=view)

    async def textChecks(self, args: tuple, channel: discord.TextChannel) -> bool:
        accept_list = ("txt", "text", "Txt", "Text")
        if len(args) == 1 and args[0] in accept_list:
            return True
        elif len(args) == 1 and args not in accept_list:
            await channel.send(f"If you want to see the text version of the menu, please specify 'txt' or 'text' after "
                               f"the k.ffs command. This might help loading time for slow connections")
            return False
        else:
            return False

    def removeFFGuild(self, guild_id: int) -> None:
        for user in self.ff_users:
            if user.getGuildId() == guild_id:
                del self.ff_users[user.getKey]

    def removeFFUser(self, user_id : int, guild_id : int) -> None:
        if int(f'{user_id}{guild_id}') in self.ff_users:
            del self.ff_users[int(f'{user_id}{guild_id}')]

    # def addUser(self, user_id : int, guild_id : int) -> None:
    #     if int(f'{user_id}{guild_id}') not in self.ff_users:
    #         self.ff_users[int(f'{user_id}{guild_id}')] = FFUser(user_id, guild_id)
    #         self.bot.db.depositNewFFUser(user_id, guild_id)


class Buttons(discord.ui.View):
    def __init__(self, bot, menu_cats: List[List[FoodStuffs]], text: bool, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.botanical = menu_cats[0]
        self.breakfast = menu_cats[1]
        self.dinner = menu_cats[2]
        self.drink = menu_cats[3]
        self.snack = menu_cats[4]
        self.use_text = text

    @discord.ui.button(emoji='\U0001F351', label="The Garden", style=discord.ButtonStyle.blurple)
    async def botanicalButton(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not self.use_text:
            botan_embed = discord.Embed(title="**Fruits & Veggies**", color=0x34eb34)
            botan_page = discord.File(f"KamBotFiles/MenuImage/botanicalMenu.jpg", filename="BotanMenu.jpg")
            botan_embed.set_image(url="attachment://BotanMenu.jpg")
            await interaction.response.edit_message(embed=botan_embed, attachments=[botan_page])
        else:
            botan_embed = await self.getBotanicalTextPage()
            await interaction.response.edit_message(embed=botan_embed, attachments=[])

    async def getBotanicalTextPage(self) -> discord.Embed:
        botan_embed = discord.Embed(title="**Fruits & Veggies**", color=0x34eb34)
        for food in self.botanical:
            botan_embed.add_field(name=f"{food.getFoodId()}) {food.getFoodType().capitalize()}",
                                  value=f" --- --- --- --- --- --- --- --- --- --- --- **{food.getCost()}**",
                                  inline=False)
        return botan_embed

    # Creates a button object to be added to the message within the view
    @discord.ui.button(emoji='\U0001F95E', label="Breakfast", style=discord.ButtonStyle.blurple)
    async def breakfastButton(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        # If there are no arguments to the command the Embed is titled, the original image is changed to the category page
        if not self.use_text:
            break_embed = discord.Embed(title="**Breakfast**", color=0xf0ab4a)
            break_page = discord.File(f"KamBotFiles/MenuImage/breakfastMenu.jpg", filename="BreakMenu.jpg")
            break_embed.set_image(url="attachment://BreakMenu.jpg")
            await interaction.response.edit_message(embed=break_embed, attachments=[break_page])
        else:
            break_embed = await self.getBreakfastTextPage()
            await interaction.response.edit_message(embed=break_embed, attachments=[])

    async def getBreakfastTextPage(self) -> discord.Embed:
        break_embed = discord.Embed(title="**Breakfast**", color=0xf0ab4a)
        for food in self.breakfast:
            break_embed.add_field(name=f"{food.getFoodId()})---{food.getFoodType().capitalize()}",
                                  value=f" --- --- --- --- --- --- --- --- --- --- --- **{food.getCost()}**",
                                  inline=False)
        return break_embed

    @discord.ui.button(emoji='\U0001F354', label="Entrées", style=discord.ButtonStyle.blurple)
    async def dinnerButton(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not self.use_text:
            dinner_embed = discord.Embed(title=f"Entrées", color=0xe0eb50)
            dinner_page = discord.File(f"KamBotFiles/MenuImage/dinnerMenu.jpg", filename=f"DinnerMenu.jpg")
            dinner_embed.set_image(url="attachment://DinnerMenu.jpg")
            await interaction.response.edit_message(embed=dinner_embed, attachments=[dinner_page])
        else:
            dinner_embed = await self.getDinnerTextPage()
            await interaction.response.edit_message(embed=dinner_embed, attachments=[])

    async def getDinnerTextPage(self) -> discord.Embed:
        dinner_embed = discord.Embed(title=f"Entrées", color=0xe0eb50)
        for food in self.dinner:
            dinner_embed.add_field(name=f"{food.getFoodId()}) {food.getFoodType().capitalize()}",
                                   value=f" --- --- --- --- --- --- --- --- --- --- --- **{food.getCost()}**",
                                   inline=False)
        return dinner_embed

    @discord.ui.button(emoji='\U0001F964', label="Beverages", style=discord.ButtonStyle.blurple)
    async def drinkButton(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not self.use_text:
            drink_embed = discord.Embed(title=f"Beverages", color=0x96caf2)
            drink_page = discord.File(f"KamBotFiles/MenuImage/drinkMenu.jpg", filename=f"DrinkMenu.jpg")
            drink_embed.set_image(url="attachment://DrinkMenu.jpg")
            await interaction.response.edit_message(embed=drink_embed, attachments=[drink_page])
        else:
            drink_embed = await self.getDrinkTextPage()
            await interaction.response.edit_message(embed=drink_embed, attachments=[])

    async def getDrinkTextPage(self) -> discord.Embed:
        drink_embed = discord.Embed(title=f"Beverages", color=0x96caf2)
        for food in self.drink:
            drink_embed.add_field(name=f"{food.getFoodId()}) {food.getFoodType().capitalize()}",
                                  value=f" --- --- --- --- --- --- --- --- --- --- --- **{food.getCost()}**", inline=False)
        return drink_embed

    # Creates a button object to be added to the message within the view
    @discord.ui.button(emoji='\U0001F968', label="Sides", style=discord.ButtonStyle.blurple)
    async def snackButton(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not self.use_text:
            snack_embed = discord.Embed(title=f"Snacks & Sides", color=0x51ede8)
            snack_page = discord.File(f"KamBotFiles/MenuImage/snackMenu.jpg", filename=f"SnackMenu.jpg")
            snack_embed.set_image(url="attachment://SnackMenu.jpg")
            await interaction.response.edit_message(embed=snack_embed, attachments=[snack_page])
        else:
            snack_embed = await self.getSnackTextPage()
            await interaction.response.edit_message(embed=snack_embed, attachments=[])

    async def getSnackTextPage(self) -> discord.Embed:
        snack_embed = discord.Embed(title=f"Snacks & Sides", color=0x51ede8)
        for food in self.snack:
            snack_embed.add_field(name=f"{food.getFoodId()}) {food.getFoodType().capitalize()}",
                                  value=f" --- --- --- --- --- --- --- --- --- --- --- **{food.getCost()}**", inline=False)
        return snack_embed

    async def on_timeout(self) -> None:
        self.clear_items()
        menu_embed = discord.Embed(title=f"KamBot's Menu")
        menu_embed.set_image(url="attachment://imageKambotMenu.jpg")
        menu_embed.add_field(name="The server has taken the menu.", value="""
        To request another menu type "/ffshop" or "/ffshop <txt>", to place your order type "/ffbuy <food item>".
        We hope you enjoy your meal, however you use it!
        """)
        # updates the embed to the timeout value
        await self.message.resource.edit(embed=menu_embed, attachments=[
            discord.File(f"KamBotFiles/KambotMenu.jpg", filename=f"imageKambotMenu.jpg")], view=self, )


class FFSelectMenu(discord.ui.TextInput):
    def __init__(self, bot):
        super().__init__(label="")
        self.bot = bot

class FFThrowModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(title=f'Targeting...')
        self.food = None
        self.target = None

        self.add_item(discord.ui.TextInput(label="Food",
                                           placeholder='THE FOOD YOU WANNA THROW!',
                                           required=True,
                                           max_length=32))
        self.add_item(discord.ui.TextInput(label="Target",
                                            placeholder='WHO YOU WANNA THROW IT AT!',
                                           required=True,
                                           max_length=32))



    async def on_submit(self, interaction: discord.Interaction):
        self.food = self.children[0].value
        self.target = self.children[1].value
        await interaction.response.send_message(f'YOU THREW SOME FOOD!')
        self.stop()



async def setup(bot):
    await bot.add_cog(FoodFight(bot))
