# imports
import discord, os, json, sys
import random
from discord.ext.commands import Bot
# custom database handler
import database
from time import sleep

from keep import alive
alive()

# init discord stuff and json handling
BOT_PREFIX = ("gg")
BOT_PREFIX_LIST = ["gg"]
token = os.environ["token"]
# emojis
emoji_worked = "✅"
emoji_error = "❌"
discord_error_rgb_code = discord.Color.from_rgb(239, 83, 80)
intents = discord.Intents.all()
client = Bot(command_prefix=BOT_PREFIX, intents=intents)  # init bot
db_handler = database.pythonboat_database_handler(client)  # ("database.json")
with open("owner.json") as f:
    adminlist = json.load(f)

"""

// GLOBAL FUNCTIONS

"""


async def get_user_input(message):
    print("Awaiting User Entry")
    # we want an answer from the guy who wants to give an answer
    answer = await client.wait_for("message", check=lambda
        response: response.author == message.author and response.channel == message.channel)
    answer = answer.content
    # clean input
    answer = answer.lower().strip()

    return answer


async def send_embed(title, description, channel, color="default"):
    # some default colors
    colors = [0xe03ca5, 0xdd7b28, 0x60c842, 0x8ae1c2, 0x008c5a, 0xc5bcc5]
    if color == "default": color = 0xe03ca5
    # create the embed
    embed = discord.Embed(title=title, description=description, color=color)
    await channel.send(embed=embed)
    return


async def send_error(channel):
    embed = discord.Embed(title="Error.", description="Internal Error, call admin.", color=0xff0000)
    await channel.send(embed=embed)
    return


# ~~~ set custom status ~~~
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle)
    # log_channel = 807057317396217947 # in your server, select a channel you want log info to be sent to
    # rightclick and copy id. put the id here. it should look like this : 807057317396217947
    """
    NEED LOG CHANNEL ID
    """
    # channel = client.get_channel(log_channel)
    # await channel.send("running")

    # check json, putting it here because has to be in a async function
    check_status = await db_handler.check_json()

    if check_status == "error":
        # channel = client.get_channel(log_channel)
        color = discord_error_rgb_code
        embed = discord.Embed(description=f"Critical error. JSON file is corrupted or has missing variables.\n\n"
        # f"`Error` code : {error_info}`\n" # -- Possibly to add
                                          f" Please contact an admin or delete the JSON database, but do a backup before -\n"
                                          f"this will result in re-creating the default config but will also **delete all user data**\n\n",
                              color=color)
        embed.set_author(name="UnbelievaBoat-Python Bot",
                         icon_url="https://blog.learningtree.com/wp-content/uploads/2017/01/error-handling.jpg")
        embed.set_footer(text="tip: default config at https://github.com/NoNameSpecified/UnbelievaBoat-Python-Bot")
        # await channel.send(embed=embed)
        quit()

    db_handler.get_currency_symbol()


"""

USER-BOT INTERACTION

"""


@client.event
async def on_message(message):
    """
    start general variable definition
    """

    # check if message is for our bot
    if not message.clean_content.lower().startswith(BOT_PREFIX):
        return 0

    # prefix checked, we can continue
    #
    indx = 0


    for i in BOT_PREFIX_LIST:
        if indx == 0:
            new_message = message.content.lower().replace(i, "")
            indx += 1

    command = new_message.lower().split(" ")

    # stop if not meant for bot. (like just a "?")
    if command[0] in ["", " "]: return 0;

    """
    basically, if the command is : 
        +give money blabla
        we take what is after the prefix and before everything else, to just get the command
        in this case : "give"
        edit : for now we just splitted it, pure command will be taken with command = command[0]
    this is to redirect the command to further handling
    """
    print(command)  # for testing purposes

    param_index = 1
    param = ["none", "none", "none", "none"]
    for param_index in range(len(command)):
        param[param_index] = command[param_index]
    print(f"Command called with parameters : {param}")
    # for use of parameters later on, will have to start at 0, not 1

    # ~~~~ GET DISCORD VARIABLES for use later on
    # to directly answer in the channel the user called in
    channel = message.channel
    server = message.guild
    user = message.author.id
    user_mention = message.author.mention
    user_pfp = message.author.avatar_url
    username = str(message.author)
    nickname = str(message.author.display_name)
    user_roles = [randomvar.name.lower() for randomvar in message.author.roles]

    # some stuff will be only for staff, which will be recognizable by the botmaster role
    staff_request = 1 if (user in adminlist) else 0
    print("staff status : ", staff_request)
    command = command[0]

    #

    """
    START PROCESSING COMMANDS
    """

    """

    possible improvements : everything in int, not float
                            all displayed numbers with "," as thousands operator
                            people can enter amounts with thousands operator
    """

    """
        REGULAR COMMANDS (not staff only)
    """
    # list of commands # their aliases, to make the help section easier
    all_reg_commands_aliases = {
        "blackjack": "bj",
        "roulette": "r",
        "slut": "s",
        "crime": "c",
        "work": "w",
        "rob": "steal",
        "balance": "bal",
        "deposit": "dep",
        "withdraw": "with",
        "give": "pay",
        "leaderboard": "lb",
        "helpeconomy": "economy-info",
        "module": "moduleinfo",
        "daily": "d",
        "cockfight": "cf",
        "upgrade": "improve",
        "stats": "analytics"
    }
    all_reg_commands = list(all_reg_commands_aliases.keys())

    # --------------
    # BLACKJACK GAME
    # --------------

    if command in ["blackjack", all_reg_commands_aliases["blackjack"]]:
        if "none" in param[1] or param[2] != "none":  # only bj <bet> ; nothing more than that 1 parameter
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`blackjack <bet, half or all>`",
                                  color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        try:
            if param[1].lower() == "half":
                bet, check = "half", False
            elif param[1].lower() == "all":
                bet, check = "all", False
            else:
                bet, check = int(float(param[1])), True
        except Exception as e:
                print(e)
                color = discord_error_rgb_code
                embed = discord.Embed(
                description=f"{emoji_error}  Invalid `<bet>` argument given.\n\nUsage:\n`blackjack <bet, half or all>`", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        if check:
            if bet < 100:
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{emoji_error}  You must choose at least `100` for your bet.",
                                      color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        try:
            # gotta check if enough money, if bet enough, etc etc then do the actual game
            status, bj_return = await db_handler.blackjack(user, bet, client, channel, username, user_pfp, message)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{bj_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)
        # "success" case where code doesnt fail is answering client directly in handler
        # same for all other games
        return

    if command in ["cockfight", all_reg_commands_aliases["cockfight"]]:
        if "none" in param[1] or param[2] != "none":  # only bj <bet> ; nothing more than that 1 parameter
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`cockfight <bet, half or all>`",
                                  color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return
        try:
            if param[1].lower() == "half":
                bet, check = "half", False
            elif param[1].lower() == "all":
                bet, check = "all", False
            else:
                bet, check = int(float(param[1])), True
        except Exception as e:
            print(e)
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Invalid `<bet>` argument given.\n\nUsage:\n`cockfight <bet, half or all>`", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return
        if check:
            if bet < 100:
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{emoji_error}  You must choose at least `100` for your bet.",
                                      color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        try:
            # gotta check if enough money, if bet enough, etc etc then do the actual game
            status, cf_return = await db_handler.cockfight(user, bet, channel, username, user_pfp)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{cf_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            await send_error(channel)
        # "success" case where code doesnt fail is answering client directly in handler
        # same for all other games
        return

    # --------------
    # ROULETTE GAME
    # --------------

    # ATTENTION : for now roulette is only playable by ONE person, multiple can't play at once

    elif command in ["roulette", all_reg_commands_aliases["roulette"]]:  # no alias
        if "none" in param[1] or "none" in param[2]:  # we need 2 parameters
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`roulette <bet, half or all> <space>`", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # bet must be in 1st place
        try:
            if param[1].lower() == "half":
                bet, check = "half", False
            elif param[1].lower() == "all":
                bet, check = "all", False
            else:
                bet, check = int(float(param[1])), True
        except:
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Invalid `<bet>` argument given.\n\nUsage:\n`roulette <bet, half or all> <space>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # space must be in second, and a valid space
        space = str(param[2])
        if space.lower() not in ["odd", "even", "black", "red", "1st", "2nd", "3rd", "first", "second", "third", "1-12",
                                 "13-24", "25-36", "1-18", "19-36"]:
            fail = 0
            try:
                space = int(space)
                if not (space > 0 and space < 36):
                    fail = 1
            except Exception as e:
                print(e)
                fail = 1
            if fail == 1:
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  Invalid `<space>` argument given.\n\nUsage:\n`roulette <bet> <space>`",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        # convert to str, even if number. will be checked in the game itself later
        space = str(space)

        if check:
            if bet < 100:
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{emoji_error}  You must choose at least `100` for your bet.",
                                      color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        try:
            # gotta check if enough money, if bet enough, etc etc then do the actual game
            status, roulette_return = await db_handler.roulette(user, bet, space, client, channel, username, user_pfp,
                                                                user_mention)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{roulette_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

        return

    # --------------
    # 	  SLUT
    # --------------

    elif command in ["slut", all_reg_commands_aliases["slut"]]:  # no alias
        try:
            status, slut_return = await db_handler.slut(user, channel, username, user_pfp)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{slut_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

    # --------------
    # 	  CRIME
    # --------------

    elif command in ["crime", all_reg_commands_aliases["crime"]]:  # no alias
        try:
            status, crime_return = await db_handler.crime(user, channel, username, user_pfp)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{crime_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

    # --------------
    # 	  WORK
    # --------------

    elif command in ["work", all_reg_commands_aliases["work"]]:  # no alias
        try:
            status, work_return = await db_handler.work(user, channel, username, user_pfp)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{work_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        except Exception as e:
            print(e)
            await send_error(channel)
    elif command in ["daily", all_reg_commands_aliases["daily"]]:  # no alias
        try:
            status, work_return = await db_handler.daily(user, channel, username, user_pfp)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{work_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        except Exception as e:
            print(e)
            await send_error(channel)


    # --------------
    # 	  ROB
    # --------------

    elif command in ["rob", all_reg_commands_aliases["rob"]]:  # no alias
        # you gotta rob someone
        if "none" in param[1] or param[2] != "none":  # we only one param
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`rob <user>`",
                                  color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        user_to_rob = str(param[1])  # the mention in channel gives us <@!USERID> OR <@USERIRD>
        if len(user_to_rob) == 22:
            flex_start = 3
        else:  # if len(userbal_to_check) == 21:
            flex_start = 2
        user_to_rob = "".join(list(user_to_rob)[flex_start:-1])  # gives us only ID

        try:
            status, rob_return = await db_handler.rob(user, channel, username, user_pfp, user_to_rob)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{rob_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

    # --------------
    #    BALANCE
    # --------------

    elif command in ["balance", all_reg_commands_aliases["balance"]]:
        # you can either check your own balance or someone else's bal
        if "none" in param[1]:
            # tell handler to check bal of this user
            userbal_to_check = user
            username_to_check = username
            userpfp_to_check = user_pfp
        # only one user to check, so only 1 param, if 2 -> error
        elif param[1] != "none" and param[2] != "none":
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Invalid `[user]` argument given.\n\nUsage:\n`balance <user>`", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return
        # else we want the balance of someone else
        else:
            userbal_to_check = str(param[1])  # the mention in channel gives us <@!USERID> OR <@USERIRD>
            if len(userbal_to_check) == 22:
                flex_start = 3
            else:  # if len(userbal_to_check) == 21:
                flex_start = 2
            userbal_to_check = "".join(list(userbal_to_check)[flex_start:-1])  # gives us only ID
            try:
                user_fetch = client.get_user(int(userbal_to_check))
                print("hello ?")
                username_to_check = user_fetch
                userpfp_to_check = user_fetch.avatar_url
            except:
                # we didnt find him
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  Invalid `[user]` argument given.\n\nUsage:\n`balance <user>`",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        # go through the handler
        try:
            await db_handler.balance(user, channel, userbal_to_check, username_to_check, userpfp_to_check)
        except Exception as e:
            print(e)
            await send_error(channel)

    elif command in ["stats", all_reg_commands_aliases["stats"]]:
        # you can either check your own balance or someone else's bal
        if "none" in param[1]:
            # tell handler to check bal of this user
            userbal_to_check = user
            username_to_check = username
            userpfp_to_check = user_pfp
        # only one user to check, so only 1 param, if 2 -> error
        elif param[1] != "none" and param[2] != "none":
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Invalid `[user]` argument given.\n\nUsage:\n`stats <user>`", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return
        # else we want the balance of someone else
        else:
            userbal_to_check = str(param[1])  # the mention in channel gives us <@!USERID> OR <@USERIRD>
            if len(userbal_to_check) == 22:
                flex_start = 3
            else:  # if len(userbal_to_check) == 21:
                flex_start = 2
            userbal_to_check = "".join(list(userbal_to_check)[flex_start:-1])  # gives us only ID
            try:
                user_fetch = client.get_user(int(userbal_to_check))
                print("hello ?")
                username_to_check = user_fetch
                userpfp_to_check = user_fetch.avatar_url
            except:
                # we didnt find him
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  Invalid `[user]` argument given.\n\nUsage:\n`stats <user>`",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        # go through the handler
        try:
            await db_handler.stats(user, channel, userbal_to_check, username_to_check, userpfp_to_check)
        except Exception as e:
            print(e)
            await send_error(channel)

    # --------------
    # 	  DEP
    # --------------

    elif command in ["deposit", all_reg_commands_aliases["deposit"]]:
        if "none" in param[1] or param[2] != "none":  # we need 1 and only 1 parameter
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`deposit <amount, half or all>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        amount = param[1].lower()
        amount_list = ["all", "half"]
        # either all or an amount, not some random string
        if amount not in amount_list:
            try:
                # they can use the thousands separator comma
                newAmount = []
                for char in amount:
                    if char != ",":
                        newAmount.append(char)
                amount = "".join(newAmount)
                amount = int(float(amount))
                if amount < 1:
                    color = discord_error_rgb_code
                    embed = discord.Embed(
                        description=f"{emoji_error}  Invalid `<amount, half or all>` argument given.\n\nUsage:\n`deposit <amount, half or all>`",
                        color=color)
                    embed.set_author(name=username, icon_url=user_pfp)
                    await channel.send(embed=embed)
                    return
            except:
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  Invalid `<amount, half or all>` argument given.\n\nUsage:\n`deposit <amount, half or all>`",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        try:
            amount = str(amount)
            status, dep_return = await db_handler.deposit(user, channel, username, user_pfp, amount)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{dep_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

    # --------------
    # 	  WITH
    # --------------

    elif command in ["withdraw", all_reg_commands_aliases["withdraw"]]:
        if "none" in param[1] or param[2] != "none":  # we need 1 and only 1 parameter
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`withdraw <amount, half or all>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        amount = param[1].lower()
        amount_list = ["all", "half"]
        # either all or an amount, not some random string
        if amount not in amount_list:
            try:
                # they can use the thousands separator comma
                newAmount = []
                for char in amount:
                    if char != ",":
                        newAmount.append(char)
                amount = "".join(newAmount)
                amount = int(float(amount))
                if amount < 1:
                    color = discord_error_rgb_code
                    embed = discord.Embed(
                        description=f"{emoji_error}  Invalid `<amount, half or all>` argument given.\n\nUsage:\n`withdraw <amount, half or all>`",
                        color=color)
                    embed.set_author(name=username, icon_url=user_pfp)
                    await channel.send(embed=embed)
                    return
            except:
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  Invalid `<amount, half or all>` argument given.\n\nUsage:\n`withdraw <amount, half or all>`",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        try:
            amount = str(amount)
            status, with_return = await db_handler.withdraw(user, channel, username, user_pfp, amount)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{with_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)


    elif command in ["upgrade", all_reg_commands_aliases["upgrade"]]:
        if "none" in param[1]:  # we need item name
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`improve <class> `",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return
        item_name = param[1]

        if "none" in param[2]:
            pass
            # we need item amount
            #color = discord_error_rgb_code
            #embed = discord.Embed(
            #    description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`buy-item <item name> <amount>`",
            #    color=color)
            #embed.set_author(name=username, icon_url=user_pfp)
            #await channel.send(embed=embed)
            #return
        amount = param[2]

        try:
            amount = int(float(amount))
            if amount < 1:
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  Invalid `amount` given.\n\nUsage:\n`buy-item <item name> <amount>`",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except:
            amount = 1

        # handler
        #user_role_ids = [randomvar.id for randomvar in message.author.roles]

        try:
            status, buy_item_return = await db_handler.upgrade(user, channel, username, user_pfp, item_name, amount)
            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{buy_item_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)
        return

    # --------------
    # 	  GIVE
    # --------------

    elif command in ["give", all_reg_commands_aliases["give"]]:
        if "none" in param[1] or "none" in param[2]:  # we need 2 parameters
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`pay <member> <amount, half or all>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # we need to check validity of both parameters

        # CHECK 1

        reception_user = str(param[1])  # the mention in channel gives us <@!USERID> OR <@USERIRD>
        if len(reception_user) == 22:
            flex_start = 3
        else:  # if len(userbal_to_check) == 21:
            flex_start = 2
        reception_user = "".join(list(reception_user)[flex_start:-1])  # gives us only ID
        try:
            user_fetch = client.get_user(int(reception_user))
            print(user_fetch)
            reception_user_name = user_fetch

            if int(reception_user) == user:
                # cannot send money to yourself
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  You cannot trade money with yourself. That would be pointless.\n"
                                f"(You may be looking for the `add-money` command.)", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        except:
            # we didnt find him
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"{emoji_error}  Invalid `<member>` argument given.\n\nUsage:"
                                              f"\n`give <member> <amount, half or all>`", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # CHECK 2

        amount = param[2].lower()
        # either all, half or an amount, not some random string
        amount_list = ["half", "all"]
        if amount not in amount_list:
            try:
                # they can use the thousands separator comma
                newAmount = []
                for char in amount:
                    if char != ",":
                        newAmount.append(char)
                amount = "".join(newAmount)
                amount = int(float(amount))
                if amount < 1:
                    color = discord_error_rgb_code
                    embed = discord.Embed(
                        description=f"{emoji_error}  Invalid `<amount, half or all>` argument given.\n\nUsage:\n`give <member> <amount, half or all>`",
                        color=color)
                    embed.set_author(name=username, icon_url=user_pfp)
                    await channel.send(embed=embed)
                    return
            except:
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  Invalid `<amount, half or all>` argument given.\n\nUsage:\n`give <member> <amount, half or all>`",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        # handler

        try:
            amount = str(amount)
            status, give_return = await db_handler.give(user, channel, username, user_pfp, reception_user, amount,
                                                        reception_user_name)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{give_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

    # --------------
    #  LEADERBOARD
    # --------------

    elif command in ["leaderboard", all_reg_commands_aliases["leaderboard"]]:
        modes = ["-cash", "-bank", "-total"]
        page_number = 1
        mode_type = modes[2]
        server_name = server.name
        full_name = server_name  # + mode_type

        # first, vanilla
        if "none" in param[1] and "none" in param[2]:
            # using default vars
            page_number = 1
            mode_type = modes[2]
            full_name += " Leaderboard"
        # one argument
        elif param[1] != "none" and "none" in param[2]:
            if param[1] in modes:
                mode_type = param[1]
                page_number = 1
                if mode_type == "-total": full_name += " Leaderboard"
                if mode_type == "-cash": full_name += " Cash Leaderboard"
                if mode_type == "-bank": full_name += " Bank Leaderboard"
            else:
                try:
                    page_number = int(param[1])
                    mode_type = modes[2]
                    full_name += " Leaderboard"
                except:
                    color = discord_error_rgb_code
                    embed = discord.Embed(
                        description=f"{emoji_error}  Invalid `[-cash | -bank | -total]` argument given.\n\nUsage:\n"
                                    f"`leaderboard [page] [-cash | -bank | -total]`", color=color)
                    embed.set_author(name=username, icon_url=user_pfp)
                    await channel.send(embed=embed)
                    return
        # two arguments
        else:
            try:
                page_number = int(param[1])
                mode_type = param[2]
                if mode_type == "-total":
                    full_name += " Leaderboard"
                elif mode_type == "-cash":
                    full_name += " Cash Leaderboard"
                elif mode_type == "-bank":
                    full_name += " Bank Leaderboard"
                else:
                    color = discord_error_rgb_code
                    embed = discord.Embed(
                        description=f"{emoji_error}  Invalid `[-cash | -bank | -total]` argument given.\n\nUsage:\n"
                                    f"`leaderboard [page] [-cash | -bank | -total]`", color=color)
                    embed.set_author(name=username, icon_url=user_pfp)
                    await channel.send(embed=embed)
                    return
            except:
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  Invalid `[-cash | -bank | -total]` argument given.\n\nUsage:\n"
                                f"`leaderboard [page] [-cash | -bank | -total]`", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return

        print(f"Looking for {full_name}, at page {page_number}, in mode {mode_type}")

        # handler

        try:
            status, lb_return = await db_handler.leaderboard(user, channel, username, full_name, page_number, mode_type,
                                                             client)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{lb_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

    # --------------
    #     HELP
    # --------------

    elif command in ["helpeconomy", all_reg_commands_aliases["helpeconomy"]]:
        color = discord.Color.from_rgb(3, 169, 244)
        embed = discord.Embed(title=f"Help System", color=color)
        embed.add_field(name="----------------------\n\nBASIC", value=f"general economy commands", inline=False)

        embed.add_field(name=all_reg_commands[0], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[0]]}  |  "
                                                        f"Usage: `blackjack <bet, half or all>`", inline=False)
        embed.add_field(name=all_reg_commands[1], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[1]]}  |  "
                                                        f"Usage: `roulette <bet, half or all> <space>`", inline=False)
        embed.add_field(name=all_reg_commands[14], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[14]]}  |  "
                                                         f"Usage: `cf <bet, half or all>`", inline=False)
        embed.add_field(name=all_reg_commands[2], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[2]]}  |  "
                                                        f"Usage: `slut`", inline=False)
        embed.add_field(name=all_reg_commands[3], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[3]]}  |  "
                                                        f"Usage: `crime`", inline=False)
        embed.add_field(name=all_reg_commands[4], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[4]]}  |  "
                                                        f"Usage: `work`", inline=False)
        embed.add_field(name=all_reg_commands[13], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[13]]}  |  "
                                                         f"Usage: `daily`", inline=False)
        embed.add_field(name=all_reg_commands[5], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[5]]}  |  "
                                                        f"Usage: `rob`", inline=False)
        embed.add_field(name=all_reg_commands[15], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[15]]}  |  "
                                                        f"Usage: `upgrade <work, crime, slut or daily>`", inline=False)
        embed.add_field(name=all_reg_commands[6], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[6]]}  |  "
                                                        f"Usage: `balance`", inline=False)
        embed.add_field(name=all_reg_commands[16], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[16]]}  |  "
                                                         f"Usage: `stats`", inline=False)
        embed.add_field(name=all_reg_commands[7], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[7]]}  |  "
                                                        f"Usage: `deposit <amount, half or all>`", inline=False)
        embed.add_field(name=all_reg_commands[8], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[8]]}  |  "
                                                        f"Usage: `withdraw <amount, half or all>`", inline=False)
        embed.add_field(name=all_reg_commands[9], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[9]]}  |  "
                                                        f"Usage: `pay <member> <amount, half or all>`", inline=False)
        embed.add_field(name=all_reg_commands[10], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[10]]}  |  "
                                                         f"Usage: `leaderboard [page] [-cash | -bank | -total]`",
                        inline=False)
        embed.add_field(name=all_reg_commands[11], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[11]]}  |  "
                                                         f"Usage: `helpeconomy` - shows this", inline=False)
        embed.add_field(name=all_reg_commands[12], value=f"Alias: {all_reg_commands_aliases[all_reg_commands[12]]}  |  "
                                                         f"Usage: `module <module, e.g. slut>`", inline=False)
        # edit stuff
        # embed.set_footer(text="For more info, contact an admin")
        await channel.send(embed=embed)

        #### in 2 parts because one was too long

        embed = discord.Embed(title=f"Help System", color=color)
        embed.add_field(name="----------------------\n\nSTAFF ONLY", value=f"requires bot developer access",
                        inline=False)
        embed.add_field(name="add-money", value=f"Usage: `add-money <member> <amount>`", inline=False)
        embed.add_field(name="remove-money", value=f"Usage: `remove-money <member> <amount>`", inline=False)
        embed.add_field(name="change", value=f"Usage: `change <module> <variable> <new value>`", inline=False)
        embed.add_field(name="change-currency", value=f"Usage: `change-currency <new emoji name>`", inline=False)
        embed.add_field(name="----------------------\n\nITEM HANDLING",
                        value=f"create and delete requires bot developer access", inline=False)
        embed.add_field(name="create-item", value=f"Usage: `create-item`", inline=False)
        embed.add_field(name="delete-item", value=f"Usage: `delete-item <item name>`", inline=False)
        embed.add_field(name="buy-item", value=f"Usage: `buy-item <item name> <amount>`", inline=False)
        embed.add_field(name="inventory", value=f"Usage: `inventory`", inline=False)
        embed.add_field(name="catalog", value=f"Usage: `catalog <nothing or item name>`", inline=False)
        embed.add_field(name="----------------------\n\nINCOME ROLES",
                        value=f"create, delete and update requires bot developer access", inline=False)
        embed.add_field(name="add-income-role", value=f"Usage: `add-income-role <role pinged> <income>`", inline=False)
        embed.add_field(name="remove-income-role", value=f"Usage: `remove-income-role <role pinged>`", inline=False)
        embed.add_field(name="list-roles", value=f"Usage: `list-roles`", inline=False)
        embed.add_field(name="update-income", value=f"Usage: `update-income` | must be used only once a week",
                        inline=False)
        # edit stuff
        embed.set_footer(text="For more info, contact an admin")

        await channel.send(embed=embed)

    # --------------
    #  MODULE INFO
    # --------------

    elif command in ["module", all_reg_commands_aliases["module"]]:
        if "none" in param[1] or param[2] != "none":  # we need 1 and only 1 parameter
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`module <module>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        module = param[1]

        # handler

        try:
            status, module_return = await db_handler.module(user, channel, module)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{module_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

        """
            STAFF COMMANDS
        """

    # --------------
    #   ADD-MONEY
    # --------------

    elif command == "add-money":
        if not staff_request:
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"🔒 Requires bot developer access", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        if "none" in param[1] or "none" in param[2]:  # we need 2 parameters
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`add-money <member> <amount>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # we need to check validity of both parameters

        # CHECK 1

        reception_user = str(param[1])  # the mention in channel gives us <@!USERID> OR <@USERIRD>
        if len(reception_user) == 22:
            flex_start = 3
        else:  # if len(userbal_to_check) == 21:
            flex_start = 2
        reception_user = "".join(list(reception_user)[flex_start:-1])  # gives us only ID
        try:
            user_fetch = client.get_user(int(reception_user))
            print(user_fetch)
            reception_user_name = user_fetch

        except:
            # we didnt find him
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"{emoji_error}  Invalid `<member>` argument given.\n\nUsage:"
                                              f"\n`add-money <member> <amount>`", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # CHECK 2

        amount = param[2]
        try:
            # they can use the thousands separator comma
            newAmount = []
            for char in amount:
                if char != ",":
                    newAmount.append(char)
            amount = "".join(newAmount)
            amount = int(float(amount))
            if amount < 1:
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  Invalid `<amount>` argument given.\n\nUsage:\n`add-money <member> <amount>`",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except:
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Invalid `<amount>` argument given.\n\nUsage:\n`add-money <member> <amount>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # handler

        try:
            amount = str(amount)
            status, add_money_return = await db_handler.add_money(user, channel, username, user_pfp, reception_user,
                                                                  amount, reception_user_name)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{add_money_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

    # --------------
    #  REMOVE-MONEY
    # --------------

    elif command == "remove-money":
        if not staff_request:
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"🔒 Requires bot developer access", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        if "none" in param[1] or "none" in param[2]:  # we need 2 parameters
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`remove-money <member> <amount>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # we need to check validity of both parameters

        # CHECK 1

        reception_user = str(param[1])  # the mention in channel gives us <@!USERID> OR <@USERIRD>
        if len(reception_user) == 22:
            flex_start = 3
        else:  # if len(userbal_to_check) == 21:
            flex_start = 2
        reception_user = "".join(list(reception_user)[flex_start:-1])  # gives us only ID
        try:
            user_fetch = client.get_user(int(reception_user))
            print(user_fetch)
            reception_user_name = user_fetch

        except:
            # we didnt find him
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"{emoji_error}  Invalid `<member>` argument given.\n\nUsage:"
                                              f"\n`remove-money <member> <amount>`", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # CHECK 2

        amount = param[2]
        try:
            # they can use the thousands separator comma
            newAmount = []
            for char in amount:
                if char != ",":
                    newAmount.append(char)
            amount = "".join(newAmount)
            amount = int(float(amount))
            if amount < 1:
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  Invalid `<amount>` argument given.\n\nUsage:\n`remove-money <member> <amount>`",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except:
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Invalid `<amount>` argument given.\n\nUsage:\n`remove-money <member> <amount>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # handler

        try:
            amount = str(amount)
            status, rm_money_return = await db_handler.remove_money(user, channel, username, user_pfp, reception_user,
                                                                    amount, reception_user_name)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{rm_money_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

    # --------------
    #   EDIT VARS
    # --------------

    elif command in ["change", "edit"]:
        if not staff_request:
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"🔒 Requires bot developer access", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        if "none" in param[1] or "none" in param[2] or "none" in param[3]:  # we need 3 parameters
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`change <module> <variable> <new value>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # that would end up messing everything up
        if param[2] == "name":
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"{emoji_error}  You cannot change module names.", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # we need to check validity of new value parameter
        # other checks will be done in the handler

        # CHECK
        module_name = param[1]
        variable_name = param[2]
        new_value = param[3]
        try:
            new_value = int(new_value)
        except:
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Invalid `<new value>` argument given.\n\nUsage:\n`change <module> <variable> <new value>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # handler

        try:
            new_value = str(new_value)
            status, edit_return = await db_handler.edit_variables(user, channel, username, user_pfp, module_name,
                                                                  variable_name, new_value)

            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{edit_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

    # ---------------------------
    #   CHANGE CURRENCY SYMBOL
    # ---------------------------

    elif command in ["change-currency", "edit_currency"]:
        if not staff_request:
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"🔒 Requires bot developer access", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        if "none" in param[1]:  # we need 1 parameters
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`change-currency <new emoji name>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        new_emoji_name = param[1]

        # handler

        try:
            status, emoji_edit_return = await db_handler.change_currency_symbol(user, channel, username, user_pfp,
                                                                                new_emoji_name)
            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{emoji_edit_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

        """
            SPECIAL COMMANDS
        """

        """
        TODO :
            catalog
            add all these to the help menu
            use-item
        """

    # ---------------------------
    #   ITEM CREATION
    # ---------------------------

    elif command in ["create-item", "new-item", "item-create"]:
        if not staff_request:
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"🔒 Requires bot developer access", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        currently_creating_item = True
        checkpoints = 1
        last_report = ""
        color = discord.Color.from_rgb(3, 169, 244)
        # send a first input which we will then edit
        info_text = ":one: What should the new item be called?\nThis name should be unique and no more than 200 characters."
        first_embed = discord.Embed(title="Item Info", description="Name\n.", color=color)
        first_embed.set_footer(text="Type cancel to quit")
        await channel.send(info_text, embed=first_embed)

        while currently_creating_item:
            user_input = ""
            # get input first
            user_input = await get_user_input(message)
            print(user_input)
            # check if user wants cancel
            if user_input == "cancel":
                await channel.send(f"{emoji_error}  Cancelled command.")
                return

            if checkpoints == 1:
                # check 1: name
                if len(user_input) > 200:
                    await channel.send(
                        f"{emoji_error} The maximum length for an items name is 200 characters. Please try again.")
                    continue
                elif len(user_input) < 3:
                    await channel.send(
                        f"{emoji_error}  The minimum length for an items name is 3 characters. Please try again.")
                    continue
                # good input
                item_name = user_input
                first_embed = discord.Embed(title="Item Info", color=color)
                first_embed.add_field(name="Name", value=f"{item_name}")
                first_embed.set_footer(text="Type cancel to quit")
                next_info = ":two: How much should the item cost to purchase?"
                last_report = await channel.send(next_info, embed=first_embed)
                checkpoints += 1

            elif checkpoints == 2:
                # check 2: cost
                try:
                    cost = int(user_input)
                    if cost < 1:
                        await channel.send(
                            f"{emoji_error}  Invalid price given. Please try again or type cancel to exit.")
                        continue
                except:
                    await channel.send(f"{emoji_error}  Invalid price given. Please try again or type cancel to exit.")
                    continue
                first_embed.add_field(name="Price", value=f"{cost}")
                first_embed.set_footer(text="Type cancel to quit or skip to skip this option")
                next_info = ":three: Please provide a description of the item.\nThis should be no more than 200 characters."
                await last_report.edit(content=next_info, embed=first_embed)
                checkpoints += 1

            elif checkpoints == 3:
                # check 3: description
                if len(user_input) > 200:
                    await channel.send(
                        f"{emoji_error} The maximum length for an items description is 200 characters. Please try again.")
                    continue
                description = user_input
                first_embed.add_field(name="Description", value=f"{description}", inline=False)
                first_embed.set_footer(text="Type cancel to quit or skip to skip this option")
                next_info = ":four: How long should this item stay in the store for? (integer, in days)\nMinimum duration is 1 day.\nIf no limit, just reply `skip`."
                await last_report.edit(content=next_info, embed=first_embed)
                checkpoints += 1

            elif checkpoints == 4:
                # check 4: duration
                try:
                    duration = int(user_input)
                    if duration < 1:
                        await channel.send(
                            f"{emoji_error}  Invalid time duration given. Please try again or type cancel to exit.")
                        continue
                except:
                    if user_input == "skip":
                        duration = "none"
                    else:
                        await channel.send(
                            f"{emoji_error}  Invalid time duration given. Please try again or type cancel to exit.")
                        continue

                first_embed.add_field(name="Time remaining", value=f"{duration} days left")
                first_embed.set_footer(text="Type cancel to quit or skip to skip this option")
                next_info = ":five: How much stock of this item will there be?\nIf unlimited, just reply `skip` or `infinity`."
                await last_report.edit(content=next_info, embed=first_embed)
                checkpoints += 1

            elif checkpoints == 5:
                # check 5: stock
                try:
                    stock = int(user_input)
                    if stock < 1:
                        await channel.send(
                            f"{emoji_error}  Invalid stock amount given. Please try again or type cancel to exit.")
                        continue
                except:
                    if user_input == "skip" or user_input == "infinity":
                        stock = "unlimited"
                    else:
                        await channel.send(
                            f"{emoji_error}  Invalid stock amount given. Please try again or type cancel to exit.")
                        continue

                first_embed.add_field(name="Stock remaining", value=f"{stock}")
                first_embed.set_footer(text="Type cancel to quit or skip to skip this option")
                next_info = ":six: What role must the user already have in order to buy this item?\nIf none, just reply `skip`."
                await last_report.edit(content=next_info, embed=first_embed)
                checkpoints += 1

            elif checkpoints == 6:
                # check 6: required role
                try:
                    if user_input == "skip":
                        raise ValueError

                    roles = user_input
                    roles = roles.split(" ")
                    roles_clean = []
                    for i in range(len(roles)):
                        if len(roles[i]) == 22:
                            flex_start = 3
                        else:  # if len() == 21:
                            flex_start = 2
                        roles_clean.append("".join(list(roles[i])[flex_start:-1]))  # gives us only ID
                    print(roles, roles_clean)

                    required_roles = ""
                    for role_id in roles_clean:
                        try:
                            role = discord.utils.get(server.roles, id=int(role_id))
                            print(role)
                            required_roles += f"{str(role.mention)} "
                        except:
                            await channel.send(f"{emoji_error}  Invalid role given. Please try again.")
                            raise NameError

                except NameError:
                    continue

                except ValueError:
                    if user_input == "skip":
                        required_roles = "none"

                except Exception as e:
                    await channel.send(f"{emoji_error}  Invalid role given. Please try again.")
                    continue
                try:
                    roles_id_required = roles_clean
                except:
                    roles_id_required = "none"
                first_embed.add_field(name="Role required", value=f"{required_roles}")
                first_embed.set_footer(text="Type cancel to quit or skip to skip this option")
                next_info = ":seven: What role do you want to be given when this item is bought?\nIf none, just reply `skip`."
                await last_report.edit(content=next_info, embed=first_embed)
                checkpoints += 1

            elif checkpoints == 7:
                # check 7: role to be given when item bought
                try:
                    if user_input == "skip":
                        raise ValueError

                    roles = user_input
                    roles = roles.split(" ")
                    roles_clean = []
                    for i in range(len(roles)):
                        if len(roles[i]) == 22:
                            flex_start = 3
                        else:  # if len() == 21:
                            flex_start = 2
                        roles_clean.append("".join(list(roles[i])[flex_start:-1]))  # gives us only ID
                    print(roles, roles_clean)

                    roles_give = ""
                    for role_id in roles_clean:
                        try:
                            role = discord.utils.get(server.roles, id=int(role_id))
                            print(role)
                            roles_give += f"{str(role.mention)} "
                        except:
                            await channel.send(f"{emoji_error}  Invalid role given. Please try again.")
                            raise NameError

                except NameError:
                    continue

                except ValueError:
                    if user_input == "skip":
                        roles_give = "none"

                except Exception as e:
                    await channel.send(f"{emoji_error}  Invalid role given. Please try again.")
                    continue

                try:
                    roles_id_to_give = roles_clean
                except:
                    roles_id_to_give = "none"
                first_embed.add_field(name="Role given", value=f"{roles_give}")
                first_embed.set_footer(text="Type cancel to quit or skip to skip this option")
                next_info = ":eight: What role do you want to be removed from the user when this item is bought?\nIf none, just reply `skip`."
                await last_report.edit(content=next_info, embed=first_embed)
                checkpoints += 1

            elif checkpoints == 8:
                # check 8: role to be removed when item bought
                try:
                    if user_input == "skip":
                        raise ValueError

                    roles = user_input
                    roles = roles.split(" ")
                    roles_clean = []
                    for i in range(len(roles)):
                        if len(roles[i]) == 22:
                            flex_start = 3
                        else:  # if len() == 21:
                            flex_start = 2
                        roles_clean.append("".join(list(roles[i])[flex_start:-1]))  # gives us only ID
                    print(roles, roles_clean)

                    roles_remove = ""
                    for role_id in roles_clean:
                        try:
                            role = discord.utils.get(server.roles, id=int(role_id))
                            print(role)
                            roles_remove += f"{str(role.mention)} "
                        except:
                            await channel.send(f"{emoji_error}  Invalid role given. Please try again.")
                            raise NameError

                except NameError:
                    continue

                except ValueError:
                    if user_input == "skip":
                        roles_remove = "none"

                except Exception as e:
                    await channel.send(f"{emoji_error}  Invalid role given. Please try again.")
                    continue

                try:
                    roles_id_to_remove = roles_clean
                except:
                    roles_id_to_remove = "none"
                first_embed.add_field(name="Role removed", value=f"{roles_remove}")
                first_embed.set_footer(text="Type cancel to quit or skip to skip this option")
                next_info = ":nine: What is the maximum balanace a user can have in order to buy this item?\nIf none, just reply `skip`."
                await last_report.edit(content=next_info, embed=first_embed)
                checkpoints += 1

            elif checkpoints == 9:
                # check 9: max balance
                try:
                    max_bal = int(user_input)
                    if max_bal < 1:
                        await channel.send(
                            f"{emoji_error}  Invalid minimum balance given. Please try again or type cancel to exit.")
                        continue
                except:
                    if user_input == "skip":
                        max_bal = "none"
                    else:
                        await channel.send(
                            f"{emoji_error}  Invalid minimum balance given. Please try again or type cancel to exit.")
                        continue
                first_embed.add_field(name="Required balance", value=f"{max_bal}")
                first_embed.set_footer(text="Type cancel to quit or skip to skip this option")
                next_info = ":keycap_ten: What message do you want the bot to reply with, when the item is bought?\nIf none, just reply `skip`."
                await last_report.edit(content=next_info, embed=first_embed)
                checkpoints += 1

            elif checkpoints == 10:
                # check 10: reply message
                if len(user_input) > 150:
                    await channel.send(
                        f"{emoji_error} The maximum length for a reply message is 150 characters. Please try again.")
                    continue
                if user_input == "skip":
                    user_input = f"Congrats on buying the item."
                reply_message = user_input
                first_embed.add_field(name="Reply message", value=f"{reply_message}", inline=False)
                next_info = f"{emoji_worked}  Item created successfully!"
                await last_report.edit(content=next_info, embed=first_embed)
                checkpoints = -1
                # finished with the checks
                currently_creating_item = False

        # handler

        try:
            status, create_item_return = await db_handler.create_new_item(item_name, cost, description, duration, stock,
                                                                          roles_id_required, roles_id_to_give,
                                                                          roles_id_to_remove, max_bal, reply_message)
            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{create_item_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

    # ---------------------------
    #   DELETE ITEM
    # ---------------------------

    elif command in ["delete-item", "remove-item"]:
        if not staff_request:
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"🔒 Requires bot developer access", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        if "none" in param[1]:  # we need 1 parameters
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`delete-item <item name>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return
        item_name = param[1]
        # handler

        try:
            status, remove_item_return = await db_handler.remove_item(item_name)
            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{remove_item_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

        color = discord.Color.from_rgb(102, 187, 106)  # green
        embed = discord.Embed(
            description=f"{emoji_worked}  Item has been removed from the store.\nNote: also deletes from everyone's inventory.",
            color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        await channel.send(embed=embed)

        return

    # ---------------------------
    #   BUY ITEM
    # ---------------------------

    elif command in ["buy-item", "get-item"]:
        if not staff_request:
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"🔒 Requires bot developer access", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        if "none" in param[1]:  # we need item name
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`buy-item <item name> <amount>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return
        item_name = param[1]

        if "none" in param[2]:  # we need item amount
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`buy-item <item name> <amount>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return
        amount = param[2]

        try:
            amount = int(amount)
            if amount < 1:
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  Invalid `amount` given.\n\nUsage:\n`buy-item <item name> <amount>`",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except:
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Invalid `amount` given.\n\nUsage:\n`buy-item <item name> <amount>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # handler
        user_role_ids = [randomvar.id for randomvar in message.author.roles]

        try:
            status, buy_item_return = await db_handler.buy_item(user, channel, username, user_pfp, item_name, amount,
                                                                user_role_ids, server, message.author)
            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{buy_item_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)
        return

    # ---------------------------
    #   CHECK INVENTORY
    # ---------------------------

    elif command in ["inventory"]:
        # handler
        try:
            status, inventory_return = await db_handler.check_inventory(user, channel, username, user_pfp)
            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{inventory_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)
        return

    # ---------------------------
    #   ITEMS CATALOG
    # ---------------------------

    elif command in ["catalog", "items", "item-list", "list-items"]:

        if "none" in param[1]:  # we need item name
            item_check = "default_list"
        else:
            item_check = param[1]

        # handler
        try:
            status, catalog_return = await db_handler.catalog(user, channel, username, user_pfp, item_check, server)
            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{catalog_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)
        return


    # ---------------------------
    #   ADD ROLE INCOME ROLE
    # ---------------------------

    elif command in ["add-income-role", "add-role-income"]:
        if not staff_request:
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"🔒 Requires bot developer access", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        if "none" in param[1] or "none" in param[2]:  # we need 3 parameters
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`add-income-role <role pinged> <income>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # check role

        income_role_raw = param[1]
        income_role = ""
        if len(income_role_raw) == 22:
            flex_start = 3
        else:  # if len() == 21:
            flex_start = 2
        income_role = "".join(list(income_role_raw[flex_start:-1]))  # gives us only ID

        try:
            role = discord.utils.get(server.roles, id=int(income_role))
        except Exception as e:
            print(e)
            await channel.send(f"{emoji_error}  Invalid role given. Please try again.")
            return

        # check amount
        amount = param[2]
        # they can use the thousands separator comma
        try:
            newAmount = []
            for char in amount:
                if char != ",":
                    newAmount.append(char)
            amount = "".join(newAmount)
            amount = int(amount)
            if amount < 1:
                color = discord_error_rgb_code
                embed = discord.Embed(
                    description=f"{emoji_error}  Invalid `<amount>` argument given.\n\nUsage:\n`add-income-role <role pinged> <amount>`",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except:
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Invalid `<amount>` argument given.\n\nUsage:\n`add-income-role <role pinged> <amount>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # handler
        try:
            status, create_role_return = await db_handler.new_income_role(user, channel, username, user_pfp,
                                                                          income_role, amount)
            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{create_role_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)
        return

    # ---------------------------
    #   REMOVE ROLE
    # ---------------------------

    elif command in ["remove-income-role", "delete-income-role", "remove-role-income", "delete-role-income"]:
        if not staff_request:
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"🔒 Requires bot developer access", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        if "none" in param[1]:  # we need 1 parameters
            color = discord_error_rgb_code
            embed = discord.Embed(
                description=f"{emoji_error}  Too few arguments given.\n\nUsage:\n`remove-income-role <role pinged>`",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        # check role

        income_role_raw = param[1]
        income_role = ""
        if len(income_role_raw) == 22:
            flex_start = 3
        else:  # if len() == 21:
            flex_start = 2
        income_role = "".join(list(income_role_raw[flex_start:-1]))  # gives us only ID

        try:
            role = discord.utils.get(server.roles, id=int(income_role))
        except Exception as e:
            print(e)
            await channel.send(f"{emoji_error}  Invalid role given. Please try again.")
            return

        # handler
        try:
            status, remove_role_return = await db_handler.remove_income_role(user, channel, username, user_pfp,
                                                                             income_role)
            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{remove_role_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

        color = discord.Color.from_rgb(102, 187, 106)  # green
        embed = discord.Embed(description=f"{emoji_worked}  Role has been disabled as income role.", color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        await channel.send(embed=embed)

        return

    # ---------------------------
    #   LIST INCOME ROLES
    # ---------------------------

    elif command in ["list-roles", "list-income-roles", "list-role-income", "list-incomes"]:
        try:
            status, list_roles_return = await db_handler.list_income_roles(user, channel, username, user_pfp, server)
            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{list_roles_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)
        return

    # ---------------------------
    #   UPDATE INCOMES
    # ---------------------------

    elif command in ["update-income"]:
        if not staff_request:
            color = discord_error_rgb_code
            embed = discord.Embed(description=f"🔒 Requires bot developer access", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return

        try:
            status, update_incomes_return = await db_handler.update_incomes(user, channel, username, user_pfp, server)
            if status == "error":
                color = discord_error_rgb_code
                embed = discord.Embed(description=f"{update_incomes_return}", color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                await channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await send_error(channel)

        color = discord.Color.from_rgb(102, 187, 106)  # green
        embed = discord.Embed(
            description=f"{emoji_worked}  Users with registered roles have received their income (into bank account).",
            color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        await channel.send(embed=embed)

        return


"""
END OF CODE. 
    -> starting bot
"""

print("Starting bot")
client.run(token)
