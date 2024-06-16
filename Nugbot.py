import re
import dice
import json
import time
import random
import asyncio
import discord
import requests
import cloudscraper

from discord import Member
from random import randint
from bs4 import BeautifulSoup
from datetime import datetime
from operator import itemgetter
from discord.ext import commands
from discord.ext.commands import has_permissions

TOKEN = "Removed"
osuApiID = "Removed"
osuApiSecret = "Removed"
ApexAPI = "Removed"


class HasteBinApi:

    def __init__(self, content):
        self.content = content

    def get_key(self):
        req = requests.post('https://hastebin.com/documents',
                            # headers={},
                            data=self.content)

        key = json.loads(req.content)
        return key['key']


nicknames = ['Armstrong', 'Bandit', 'Beast', 'Boomer', 'Buzz', 'C-Block', 'Casper', 'Caveman', 'Centice', 'Chipper',
             'Cougar', 'Dude', 'Foamer', 'Fury', 'Gerwin', 'Goose', 'Heater', 'Hollywood', 'Hound', 'Iceman', 'Imp',
             'Jester', 'Junker', 'Khan', 'Marley', 'Maverick', 'Merlin', 'Middy', 'Mountain', 'Myrtle', 'Outlaw',
             'Poncho', 'Rainmaker', 'Raja', 'Rex', 'Roundhouse', 'Sabretooth', 'Saltie', 'Samara', 'Scout', 'Shepard',
             'Slider', 'Squall', 'Sticks', 'Stinger', 'Storm', 'Sultan', 'Sundown', 'Swabbie', 'Tex', 'Tusk', 'Viper',
             'Wolfman', 'Yuri']

wordblacklist2 = ["caca", "n1gg3r", "creamp13", "ni663r", "f4got", "fagot", "f4g0t", "nigg3r", "nigger",
                  "fag0t", "fagg0t", "cr34mp1e", "cr3amp1e", "fucc", "f4ggot",
                  "creampie", "n1663r", "cum", "cr3amp13", "creampi3", "f4gg0t", "f4get", "cr3ampie",
                  "n199er", "fuck", "cr34mp13", "n1gger", "creamp1e", "ni66er", "faggot", "faget"]

intents = discord.Intents.default()
intents.members = True
intents.messages = True

client = commands.Bot(command_prefix='.', intents=intents)
client.remove_command('help')  # Remove !help to add own version

giveawayUsers = []
gameList = []
gamesDict = {}
giveawayStatus = 0
latestPlug = ['a']
latestMessageUser = ['bean']
failedAttempts = {}
tempmsg = ""
tempauthor = ""
tempguild = ""
daevymsg = ""
wordblacklist = {}
wordwhitelist = {}
muteDict = {}

with open('E:\\Scripts\\Python\\Nugbot\\servers_info.json', 'r') as fp:  # Open Json containing info for Gatekeeper
    servers_info = (json.load(fp))

with open('E:\\Scripts\\Python\\Nugbot\\newUsers.json', 'r') as fp:
    newUsers = (json.load(fp))
    print("Successfully loaded newUsers.json")

with open("blacklist.json", 'r') as blacklistfile:
    wordblacklist = set(json.load(blacklistfile))
    print("Successfully loaded blacklist")

with open("whitelist.json", 'r') as whitelistfile:
    wordwhitelist = set(json.load(whitelistfile))
    print("Successfully loaded whitelist")

# Set up msgCount variable for automagic giveaways
msgCount = 0
with open("msgcount.txt", "r") as file:
    msgCount = int(file.read())


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    i = 0
    serverList = []
    print('')
    for guild in client.guilds:
        i += 1
        serverList.append(guild.name)
    print(f"Currently in {i} servers!\n --------------------------------------- \n")
    print(f"{serverList} \n")
    await client.change_presence(activity=discord.Game(name='.h'))


@client.command(pass_context=True, aliases=['h'])
async def help(ctx, mode=""):
    if mode.lower() == "":
        embed = discord.Embed(colour=discord.Colour.blue(), title="Categories")
        embed.add_field(name="Fun", value="Commands just for nonsense and fun.", inline=False)
        embed.add_field(name="Games", value="Commands for games, such as Rocket League.", inline=False)
        embed.add_field(name="Mod", value="Commands for mods/admins.", inline=False)
        await ctx.send(embed=embed)
        return

    elif mode.lower() == "fun":
        embed = discord.Embed(colour=discord.Colour.green(), title="Fun")
        embed.add_field(name="gamble *amount* [.g]", value="Roll for Nuggets!", inline=False)
        embed.add_field(name="bal/baltop", value="Nugget leaderboards. `.baltop all` for a global leaderboard.",
                        inline=False)
        embed.add_field(name="give", value="Give another user nuggets. (`.give @user 10`)", inline=False)
        embed.add_field(name="enlarge",
                        value="Enlarge an emote. Only works on custom emotes from servers the bot is in.", inline=False)
        embed.add_field(name="roll",
                        value="Roll a die (D20 by default). Choose what to roll by doing f.ex `.roll 2d6`.",
                        inline=False)
        embed.add_field(name="coinflip [flip]", value="Flip a coin.", inline=False)
        embed.add_field(name="fact", value="Posts a random fact.", inline=False)
        embed.add_field(name="hug", value="Hug someone!", inline=False)
        embed.add_field(name="slap", value="Slap someone!", inline=False)
        await ctx.send(embed=embed)
        return

    elif mode.lower() == "games":
        embed = discord.Embed(colour=discord.Colour.dark_teal(), title="Games")
        embed.add_field(name="rank", value="Check your rank in certain games.", inline=False)
        embed.add_field(name="worth", value="Check the value of Rocket League items.", inline=False)
        await ctx.send(embed=embed)
        return

    elif mode.lower() == "mod":
        embed = discord.Embed(colour=discord.Colour.dark_red(), title="Mod Tools")
        embed.add_field(name="logging", value="Activate logging for the server", inline=False)
        embed.add_field(name="mute",
                        value="Mute a user for x seconds. (This requires you to set up a role named *Muted* first.)",
                        inline=False)
        embed.add_field(name="kick", value="Kick a user", inline=False)
        embed.add_field(name="ban", value="Ban a user", inline=False)
        embed.add_field(name="unban", value="Unban a user. (Only accepts user's ID).", inline=False)
        embed.add_field(name="del / clear", value="Deletes x messages. Defaults to 99. Example use: `.del 10`.",
                        inline=False)
        await ctx.send(embed=embed)
        return


''' --- Scrapped
###Plug info
@client.command(pass_context=True)
async def plug(ctx):
    embed = discord.Embed(colour=discord.Colour.dark_magenta())
    embed.set_author(name='Plug your twitch channel!')
    embed.add_field(name="__How it works__ \nInstead of you having to hop between discord servers to plug your channel, Nugbot will now do this for you! \nIn every server Nugbot is in, it will repost your link in predetermined channels so you don't have to.", value = "------------------------------", inline=False)
    embed.add_field(name="__But won't that cause a lot of spam?__ \nNo more than usual. Every plug is logged, and misuse *will* get you blacklisted.", value= '------------------------------', inline=False)
    embed.add_field(name="__Accepted channel names:__ \nself-promo, self-promotion, twitch-promos, promote-yourself, going-live, who-be-live-meow, shame-free-plugs, twitch-live.", value="------------------------------", inline=False)
    embed.add_field(name="__More on names:__ \nIf you want to name your Twitch advertising channel differently, send a message to SimplyFluke, and it'll be added.", value="------------------------------", inline=False)
    embed.add_field(name="__Add me!__ \nShould you want to add NugBot to your server, head to https://tinyurl.com/NuggyBot", value="------------------------------", inline=False)
    print(f"Dropping plug info in {ctx.message.guild}")
    await ctx.send(embed=embed)
'''


###Roll
@client.command(pass_context=True, aliases=['dice', 'DICE'])
async def roll(ctx, die='20'):
    stamp = time.time()
    timeStamp = datetime.fromtimestamp(stamp).strftime('%d-%m-%y %H:%M:%S')
    if die != '20':
        rollan = dice.roll(die)
        total = 0
        print(
            f'{timeStamp}: {str(ctx.message.author.name)} threw some dice! The results were {str(rollan)}. || {ctx.message.guild}')
        for num in rollan:
            total = total + num
        await ctx.send(f"> You rolled {str(rollan)} for a total of **{str(total)}**")
    else:
        rollan = randint(1, int(die))
        print(f" {str(ctx.message.author.name)} threw a die! It landed on a {str(rollan)}. || {ctx.message.guild}")
        rList = ['https://i.imgur.com/uXv54ot.png', 'https://i.imgur.com/8dmBenI.png',
                 'https://i.imgur.com/ZxTsyRR.png', 'https://i.imgur.com/EBbTKoU.png',
                 'https://i.imgur.com/Jlmc9MH.png', 'https://i.imgur.com/56QHQS8.png',
                 'https://i.imgur.com/azxX9N5.png',
                 'https://i.imgur.com/SRPZGNx.png', 'https://i.imgur.com/WiBRLkj.png',
                 'https://i.imgur.com/kJRz3H5.png', 'https://i.imgur.com/tD1JrZw.png',
                 'https://i.imgur.com/S8KfCe9.png', 'https://i.imgur.com/AD0r21e.png',
                 'https://i.imgur.com/aJ9jsAC.png',
                 'https://i.imgur.com/7kcFpWA.png', 'https://i.imgur.com/1rRwfZE.png',
                 'https://i.imgur.com/KtlZ17V.png', 'https://i.imgur.com/K2RiR95.png',
                 'https://i.imgur.com/BvUPcko.png', 'https://i.imgur.com/XCsIlfm.png']
        r = rollan - 1
        e = discord.Embed(colour=discord.Colour.green())
        e.set_image(url=rList[r])
        await ctx.send(embed=e)


@client.command()  # Bucko the legend <3
async def enlarge(ctx, emoji: discord.Emoji):
    await ctx.send(emoji.url)


@client.command(pass_context=True)
async def dictupdate(ctx):
    with open("user_info.json", 'r') as uf:
        userdict = (json.load(uf))
    i = 0
    for guild in client.guilds:
        print(guild)
        if not str(guild.id) in userdict.keys():
            for member in guild.members:
                try:
                    userdict[member.guild.id].update({
                        member.id: {
                            "Name": member.name,
                            "Money": 0,
                            "rlconsole": "",
                            "rlid": '',
                            "epicID": "",
                            "steamID": "",
                            "console": "",
                            "riotID": ""
                        }
                    })
                except KeyError:
                    userdict.update({
                        member.guild.id: {
                            member.id: {
                                "Name": member.name,
                                "Money": 0,
                                "rlconsole": "",
                                "rlid": '',
                                "epicID": "",
                                "steamID": "",
                                "console": "",
                                "riotID": ""
                            }}
                    })

                i += 1
                with open("user_info.json", "w") as uf:
                    json.dump(userdict, uf, indent=4)
        print(f"Updated {i} users.")


@client.command(pass_context=True)
async def baltop(ctx, mode="here"):
    topbalance = {}
    sortedBal = {}
    balList = []
    with open("user_info.json", "r") as userfile:
        userinfo = (json.load(userfile))

    if mode.lower() == "all" or mode.lower() == "global":
        for key in userinfo.keys():
            for user in userinfo[str(key)].keys():
                tempBal = userinfo[str(key)][str(user)]['Money']
                if tempBal != 0:
                    name = userinfo[str(key)][str(user)]["Name"]
                    try:
                        if name in topbalance and topbalance[name] > tempBal:
                            pass
                        else:
                            topbalance[name] = tempBal
                            sortedBal = dict(sorted(topbalance.items(), key=itemgetter(1), reverse=True))
                            embed = discord.Embed(colour=discord.Colour.teal(), type="rich",
                                                  title="__Global Nugget Leaderboard__")

                    except KeyError:
                        topbalance[name] = tempBal
                        sortedBal = dict(sorted(topbalance.items(), key=itemgetter(1), reverse=True))

    else:
        for member in ctx.guild.members:
            try:
                tempBal = userinfo[str(ctx.message.guild.id)][str(member.id)]['Money']
                topbalance[member.name] = tempBal
            except KeyError:
                pass

            embed = discord.Embed(colour=discord.Colour.teal(), type="rich",
                                  title="__Nugget Leaderboard__")
            embed.set_footer(text=ctx.message.guild)

    sortedBal = dict(sorted(topbalance.items(), key=itemgetter(1), reverse=True))
    for key in sortedBal:
        balList.append(f"{key} - {sortedBal[key]}")

    embed.set_thumbnail(
        url="https://31.media.tumblr.com/363b2f61cb697eece543b040225a80e3/tumblr_mndnmoTHkQ1qe5puyo1_500.png")
    embed.add_field(name="\u200b", value=f":trophy:**1st place:**:trophy: {balList[0]}\n"
                                         f":second_place: **2nd place:** {balList[1]}\n"
                                         f":third_place: **3rd place:** {balList[2]}\n\n"
                                         f" **4th:** {balList[3]}\n"
                                         f" **5th:** {balList[4]}\n"
                                         f" **6th:** {balList[5]}\n"
                                         f" **7th:** {balList[6]}\n"
                                         f" **8th:** {balList[7]}\n"
                                         f" **9th:** {balList[8]}\n"
                                         f" **10th:** {balList[9]}\n")

    await ctx.send(embed=embed)


@client.command(pass_context=True, aliases=['stats'])
async def rank(ctx, game="", console="", userID="", userID2="", userID3="", userID4="",
               userID5=""):  # Valorant, Osu, CS:GO, League of Legends, Rainbow 6 Siege

    if ctx.guild.id == 776892745981231154:
        if not ctx.message.channel.id == 814702813434216488:
            await ctx.send("Wrong channel, mate.")
            return

    if userID5 != "":  # Deal with spaces in usernames
        userID = f"{userID}%20{userID2}%20{userID3}%20{userID4}%20{userID5}"
    elif userID4 != "":
        userID = f"{userID}%20{userID2}%20{userID3}%20{userID4}"
    elif userID3 != "":
        userID = f"{userID}%20{userID2}%20{userID3}"
    elif userID2 != "":
        userID = f"{userID}%20{userID2}"
    # userID = f"%20".join([userID,userID2,userID3,userID4,userID5])

    rankDict = {
        "un-ranked": "<:unranked:816919331950034944>",
        "bronze i": "<:bronze1:816919331841638420>",
        "bronze ii": "<:bronze2:816919331878731786>",
        "bronze iii": "<:bronze3:816919331988176926>",
        "silver i": "<:silver1:816919332026187796>",
        "silver ii": "<:silver2:816919331714760726>",
        "silver iii": "<:silver3:816919331954491402>",
        "gold i": "<:gold1:816919332189372436>",
        "gold ii": "<:gold2:816919331954884620>",
        "gold iii": "<:gold3:816919331966550047>",
        "platinum i": "<:platinum1:816919331740188703>",
        "platinum ii": "<:platinum2:816919332021993503>",
        "platinum iii": "<:platinum3:816919332093296650>",
        "diamond i": "<:diamond1:816919332012949524>",
        "diamond ii": "<:diamond2:816919332121870366>",
        "diamond iii": "<:diamond3:816919332318871592>",
        "champion i": "<:champion1:816919332147429407>",
        "champion ii": "<:champion2:816919331980050492>",
        "champion iii": "<:champion3:816919331992502282>",
        "grand champion ii": "<:grandchamp2:816919332167745607>",
        "grand champion i": "<:grandchamp1:816919332118200320>",
        "grand champion iii": "<:grandchamp3:816919331664691201>",
        "supersonic legend": "<:supersonic_legend:816919331585261579>"
    }

    consoleList = ['ps', 'ps3', 'ps4', 'ps5', 'xbox', 'pc', 'steam', 'epic', 'mobile']
    cocKey = "Removed"
    if game.lower() == "fn" or game.lower() == "fortnite":
        game = "Fortnite"
        r = requests.get("https://fortnite-api.com/v1/stats/br/v2",
                         params={"name": userID,
                                 "image": "all"})
        if "200" in str(r):
            print(f"Looking up {userID}'s {game} ranks")
            statDict = json.loads(r.text)
            embed = discord.Embed(colour=discord.Colour.blue())
            embed.set_author(name="\u200b")
            embed.set_image(url=statDict['data']['image'])
            await ctx.send(embed=embed)

        else:
            await ctx.send("Could not find profile :slight_frown:")

    if game.lower() == "rl" or game.lower() == "rocketleague":
        try:
            if console != "" and userID != "" or console == "me":
                if console == 'me':
                    with open("user_info.json", "r") as userfile:
                        user_info = (json.load(userfile))
                    console = user_info[str(ctx.author.id)]['rlconsole']
                    userID = user_info[str(ctx.author.id)]['rlid']

                    if console == "":
                        await ctx.send("> Please link your account with **.rllink** first.")
                        return

                if console.lower() in consoleList:
                    if console.lower() == 'pc':
                        console = "steam"

                    if console.lower() == 'ps4' or console.lower() == "ps3" or console.lower() == "ps5":
                        console = "ps"

                    print(f"Looking up {userID}'s ranks...\n")
                    temp_msg = await ctx.send(
                        "> I'm not a fast boi like the other bots.. Please be patient \n> :pleading_face::point_right::point_left:")
                    await temp_msg.add_reaction("🕙")

                    userID = userID.replace("https://steamcommunity.com/id/",
                                            "")  # Cut off full steam link just in case
                    userID = userID.replace("https://steamcommunity.com/profiles/", "")

                    rankURL = f"http://api.yannismate.de/rank/{console}/{userID}?returnName=true"
                    scraper = cloudscraper.create_scraper()
                    r = scraper.get(rankURL)

                    if not "Player not found" in r.text or "Internal Server Error" in r.text:
                        txt = r.text.split("'s ranks: ")

                        if txt[1] == "":
                            await temp_msg.delete()
                            await ctx.send(
                                "> User seems to have some black voodoo curse going on. Can not find any ranks. "
                                ":slight_frown:")
                            return
                        name = txt[0]

                        cleaning = "{'" + txt[1] + "'}"
                        cleaning = cleaning.replace(": ", "': '")
                        cleaning = cleaning.replace(" | ", "', '")
                        cleaning = cleaning.replace("'", '"')
                        playerInfoDict = json.loads(cleaning)

                        try:
                            casual = playerInfoDict['Un-Ranked']
                        except KeyError:
                            print("Could not find casual MMR.")
                            casual = "Unknown"

                        try:
                            splitones = playerInfoDict['Ranked Duel 1v1'].split(' Div')
                            onesrank = playerInfoDict['Ranked Duel 1v1']
                            onesicon = rankDict[splitones[0].lower()]
                        except KeyError:
                            onesrank = "Unranked"
                            onesicon = "<:unranked:816919331950034944>"
                            print("Could not find 1s MMR.")

                        try:
                            splitduos = playerInfoDict['Ranked Doubles 2v2'].split(' Div')
                            duosrank = playerInfoDict['Ranked Doubles 2v2']
                            duosicon = rankDict[splitduos[0].lower()]
                        except KeyError:
                            duosrank = "Unranked"
                            duosicon = "<:unranked:816919331950034944>"
                            print("Could not find 2s MMR.")

                        try:
                            splitthrees = playerInfoDict['Ranked Standard 3v3'].split(' Div')
                            threesrank = playerInfoDict['Ranked Standard 3v3']
                            threesicon = rankDict[splitthrees[0].lower()]
                        except KeyError:
                            threesrank = "Unranked"
                            threesicon = "<:unranked:816919331950034944>"
                            print("Could not find 3s MMR.")

                        try:
                            splittourney = playerInfoDict['Tournament Matches'].split(' Div')
                            tourneyrank = playerInfoDict['Tournament Matches']
                            tourneyicon = rankDict[splittourney[0].lower()]
                        except KeyError:
                            tourneyrank = "Unranked"
                            tourneyicon = "<:unranked:816919331950034944>"
                            print("Could not find tournament rank.")

                        try:
                            splithoops = playerInfoDict['Hoops'].split(' Div')
                            hoopsrank = playerInfoDict['Hoops']
                            hoopsicon = rankDict[splithoops[0].lower()]
                        except KeyError:
                            hoopsrank = "Unranked"
                            hoopsicon = "<:unranked:816919331950034944>"
                            print("Could not find Hoops MMR.")

                        try:
                            splitrumble = playerInfoDict['Rumble'].split(' Div')
                            rumblerank = playerInfoDict['Rumble']
                            rumbleicon = rankDict[splitrumble[0].lower()]
                        except KeyError:
                            rumblerank = "Unranked"
                            rumbleicon = "<:unranked:816919331950034944>"
                            print("Could not find Rumble MMR.")

                        try:
                            splitdropshot = playerInfoDict['Dropshot'].split(' Div')
                            dropshotrank = playerInfoDict['Dropshot']
                            dropshoticon = rankDict[splitdropshot[0].lower()]
                        except KeyError:
                            dropshotrank = "Unranked"
                            dropshoticon = "<:unranked:816919331950034944>"
                            print("Could not find Dropshot MMR.")

                        try:
                            splitsnowday = playerInfoDict['Snowday'].split(' Div')
                            snowdayrank = playerInfoDict['Snowday']
                            snowdayicon = rankDict[splitsnowday[0].lower()]
                        except KeyError:
                            snowdayrank = "Unranked"
                            snowdayicon = "<:unranked:816919331950034944>"
                            print("Could not find Snowday MMR.")

                        embed = discord.Embed(colour=discord.Colour.blue(), type="rich",
                                              title=f"{name}'s Ranks")
                        embed.add_field(name="\u200b", value=f"**Casual MMR:** {casual}", inline=False)
                        embed.add_field(name="Standard Modes", value=f"**Solo:** {onesicon} {onesrank}\n"
                                                                     f"**Doubles:** {duosicon} {duosrank}\n"
                                                                     f"**Standard:** {threesicon} {threesrank}\n"
                                                                     f"**Tournament:** {tourneyicon} {tourneyrank}",
                                        inline=False)
                        embed.add_field(name="Extra Modes", value=f"**Hoops:** {hoopsicon} {hoopsrank}\n"
                                                                  f"**Rumble:** {rumbleicon} {rumblerank}\n"
                                                                  f"**Dropshot:** {dropshoticon} {dropshotrank}\n"
                                                                  f"**Snowday:** {snowdayicon} {snowdayrank}",
                                        inline=False)
                        await temp_msg.delete()
                        await ctx.send(embed=embed)

                    if "Player not found" in r.text:
                        await temp_msg.delete()
                        if console == "steam":
                            await ctx.send(
                                "> User not found. :slight_frown:\n> (Keep in mind that *pc* is for Steam ID)")
                        else:
                            await ctx.send("> User not found. :slight_frown:")

                    if "Internal Server Error" in r.text:
                        await temp_msg.delete()
                        await ctx.send("> Yikes. Something went wrong... Please try again later.")

                if console != "" and console not in consoleList:
                    await ctx.send("I don't recognize that console..")

        except IndexError:
            await temp_msg.delete()
            await ctx.send("> The site I'm scraping from is currently having some issues. Pray for fix :pray:")
            print('Index Error hit...')

    if game.lower() == "apex":
        if console.lower() == "ps" or console == "playstation":
            console = "PS4"

        if console.lower() == "xbox":
            console = "X1"

        console = console.upper()

        r = requests.get(
            f"https://api.mozambiquehe.re/bridge?version=4&platform={console}&player={userID}&auth=Removed")
        if 'Player not found' in r.text:
            if "never played" in r.text:
                await ctx.send("User has apparently never played Apex Legends. :thinking:")
                return
            else:
                await ctx.send("User not found. :slight_frown:")
                return
        apexDict = (json.loads(r.text))
        rankImg = apexDict['global']['rank']['rankImg']
        embed = discord.Embed(colour=discord.Colour.orange())

        if not apexDict['global']['avatar'] == "Not available":
            embed.set_thumbnail(url=apexDict['global']['avatar'])

        embed.set_author(name=f"{apexDict['global']['name']}'s Stats:")
        embed.add_field(name="Level:", value=apexDict['global']['level'], inline=False)
        embed.add_field(name="Rank:",
                        value=f"{apexDict['global']['rank']['rankName']} {apexDict['global']['rank']['rankDiv']}",
                        inline=False)
        embed.add_field(name="Rank Score:", value=f"{apexDict['global']['rank']['rankScore']}", inline=False)
        await ctx.send(embed=embed)

    if game == "" and console == "" and userID == "":
        embed = discord.Embed(colour=discord.Colour.green())
        embed.set_author(name="Rank Lookup!")
        embed.add_field(name="Currently supported games and how to look up your stats:", value="\u200b", inline=False)
        embed.add_field(name="Apex", value=".rank apex {console} {user}")
        embed.add_field(name="Fortnite", value=".rank fn {user}", inline=False)
        embed.add_field(name="Rocket League",
                        value=".rank rl {console} {user}\n---\n pc = Steam. If you wish to lookup your Epic account, please use \n*.rank rl epic {user}*",
                        inline=False)
        embed.add_field(name="\u200b",
                        value="Keep in mind that you have to use your account's ID, such as Steam ID, Epic ID etc. **Steam usernames are not valid.**",
                        inline=False)
        await ctx.send(embed=embed)


###Find price of Rocket League items
@client.command(pass_context=True, aliases=['worth'])
async def value(ctx, item='', paint='', console='pc'):
    stamp = time.time()
    timeStamp = datetime.fromtimestamp(stamp).strftime('%d-%m-%y %H:%M:%S')
    strItem = str(item)
    lowerItem = strItem.lower()

    if strItem == '' or strItem == '?' or lowerItem == 'help':
        emb = discord.Embed(colour=discord.Colour.green())
        emb.set_author(name='Rocket League item value checker:')
        emb.add_field(name='**Usage:**', value='.worth [item] [color] [console]', inline=False)
        emb.add_field(
            name="**Searching for items:** \n If the item you're looking for has spaces (such as 'Fire God', Hex Tide' etc... \n Please replace the space with an underscore. (ex: Fire_God)",
            value="------------------------------", inline=False)
        emb.add_field(
            name="**Colors:** \n Most are as usual. The exceptions are: \n **Titanium White - ** TW or White \n **Forest Green - ** Green or Fgreen \n **Sky Blue - ** sblue \n **Burnt Sienna - ** Sienna or Burnt \n Example use: .worth draco sblue",
            value='------------------------------', inline=False)
        emb.add_field(
            name="**More about colors!** \n Prices vary between consoles! If you're on xbox or ps4 let me know. \n Example use: **.worth zomba tw xbox** ",
            value="------------------------------", inline=False)
        # emb.add_field(name="**Quick tip:** \n The command defaults to unpainted items on PC, so unless you're on console, you don't need to worry about writing color if the item is unpainted. (Sorry console people.)", value="------------------------------", inline=False)
        emb.add_field(name="**Problems?** \n For questions or feedback, toss a message at SimplyFluke.",
                      value="------------------------------", inline=False)
        await ctx.send(embed=emb)
    else:
        # Rename bad items (Jesus fuck) (Yes, this could've been done soooo much easier with a dict, but I was a dummy when I wrote it, and now I'm lazy.)
        if lowerItem == 'firegod':
            lowerItem = 'fire_god'

        elif lowerItem == 'gold_rush' or lowerItem == 'goldrush':
            lowerItem = 'alpha_reward_gold_rush'

        elif lowerItem == 'zombas':
            lowerItem = 'zomba'

        elif lowerItem == 'hypnotic':
            lowerItem = 'hypnotik'

        elif lowerItem == 'splash':
            lowerItem = 'big_splash'

        elif lowerItem == 'shattered':
            lowerItem = 'shattered_goal_explosion'

        elif lowerItem == 'ekg':
            lowerItem = 'ekg_omg'

        elif lowerItem == 'dustcloud':
            lowerItem = 'dust_cloud'

        elif lowerItem == 'slashbeam' or lowerItem == 'slash_beam':
            lowerItem = 'slash_beam_iii'

        elif lowerItem == 'fennek':
            lowerItem = 'fennec'

        elif lowerItem == 'goldcap' or lowerItem == 'gold_cap':
            lowerItem = 'alpha_reward_gold_cap'

        elif lowerItem == 'goldstone' or lowerItem == 'gold_stone':
            lowerItem = 'alplha_reward_goldstone'

        elif lowerItem == 'nugget' or lowerItem == 'gold_nugget' or lowerItem == 'goldnugget':
            lowerItem = 'beta_reward_gold_nugget'

        elif lowerItem == 'fireworks':
            lowerItem = 'fireworks_goal_explosion'

        elif lowerItem == 'goldstone':
            lowerItem = 'alpha_reward_goldstone'

        # Give painted items browser-friendly strings
        if paint.lower() == 'skyblue':
            paint = 'sblue'

        elif paint.lower() == 'burnt':
            paint = 'sienna'

        elif paint.lower() == 'green':
            paint = 'fgreen'

        elif paint.lower() == 'tw':
            paint = 'white'

        elif paint.lower() == 'titaniumwhite':
            paint = 'white'

        elif paint.lower() == 'xbox':
            paint = ''
            console = 'xbox'

        elif paint.lower() == 'ps4':
            paint = ''
            console = 'ps4'

        # Fix item string to make browser friendly
        fixedItem = re.sub(r'\W', '_', lowerItem)
        rScores = re.sub("_", " ", fixedItem)
        fixed = rScores.title()

        # Set up some lists to cross-check if it looks good
        paintList = ['', 'white', 'grey', 'crimson', 'pink', 'cobalt', 'sblue', 'sienna', 'saffron', 'lime', 'fgreen',
                     'orange', 'purple', 'black']

        consoleList = ['pc', 'xbox', 'ps4']

        # Let's scrape some info!
        if paint.lower() in paintList and console.lower() in consoleList:
            try:
                url = f"https://rl.insider.gg/{console.lower()}/{fixedItem}/{paint.lower()}"
                r = requests.get(url)
                src = r.content
                soup = BeautifulSoup(src, 'html.parser')
                print(f"Scraping {url}...")

                # Find image of requested item
                cont = soup.find('div', {"id": "itemSummaryContainer"})
                img = cont.find('img')
                print("Found image...")

                # Time to grab the text
                soup = BeautifulSoup(r.text, "html.parser")
                text = str(soup)
                price = re.findall(r'[\w\:][0-9.:]* - [0-9.]*[\w\:]+ k', text)  # LOOK MOM! I'M DOING REGEX!

                try:
                    if price[2]:
                        priced = price[1]
                        bpPrice = price[0]
                except IndexError:
                    price = re.findall(r'[\w\:][0-9.:]* - [0-9.]*[\w\:]+', text)
                    priced = price[3]
                    bpPrice = price[2]

                if priced == bpPrice:
                    bpPrice = "Unavailable"

                ###Find the rarity of the item and match embed color
                rarityList = ['Common', 'Very Rare', 'Rare', 'Import', 'Exotic', 'Black Market', 'Limited']
                i = 0
                rarity = ''
                print('Finding rarity...')
                while rarity == '':
                    if rarityList[i] in text:
                        rarity = rarityList[i]
                        print(f"Rarity of {fixed} is {rarity}!")
                        break
                    else:
                        i += 1

                # priced = price[3]
                # bpPrice = price[2]
                print("Found text...")

                if rarity == "Common":
                    emb = discord.Embed(colour=discord.Colour.blue())

                elif rarity == "Rare":
                    emb = discord.Embed(colour=discord.Colour.dark_blue())

                elif rarity == "Very Rare":
                    emb = discord.Embed(colour=discord.Colour.dark_purple())

                elif rarity == "Import":
                    emb = discord.Embed(colour=discord.Colour.red())

                elif rarity == "Exotic":
                    emb = discord.Embed(colour=discord.Colour.gold())

                elif rarity == "Black Market":
                    emb = discord.Embed(colour=discord.Colour.dark_magenta())

                elif rarity == "Limited":
                    emb = discord.Embed(colour=discord.Colour.dark_gold())

                emb.set_author(name=fixed)
                emb.add_field(name='Current Value: ', value=priced, inline=True)
                emb.add_field(name='BP Value: ', value=bpPrice, inline=True)
                emb.set_image(url=img["src"])
                await ctx.send(embed=emb)
                print(f"{timeStamp}: All done! || {ctx.message.guild}\n")

            # Handle errors
            except AttributeError:
                penCol = ['> That little thing? 1 key at best.', "> It's a bit on the short side. 1.5 keys.",
                          "> I don't think they're supposed to look like that... Production error?",
                          "> Error! Couldn't fit that monster in a variable."]

                meCol = ['> Error! Value too high to calculate.',
                         '> The U.S. Office of Management and Budget puts your value between $7.000.000 - $9.000.000',
                         "> Hard to say... At least 200 credits and 14 goats!"]

                if fixed == 'Penis' or fixed == 'My Penis' or fixed == 'Mypenis':
                    await ctx.send(random.choice(penCol))

                elif fixed == 'Myself' or fixed == 'Me' or fixed == 'My Self' or fixed == 'Self':
                    await ctx.send(random.choice(meCol))

                else:
                    await ctx.send(
                        "> Whoops! Either that item is not available for trade, or just straight up worthless.")
                    print(f'{timeStamp}: Attribute Error. Item: {fixed} might not be available for trade.\n')

            except IndexError:
                await ctx.send("> Whoops! That item is not available in that color!")
                print(f'{timeStamp}: Index Error. Item {fixed} not available in {paint}\n')

        # In case they mispelt
        else:
            if paint not in paintList:
                await ctx.send(
                    "> Please make sure the color is written the same way as in-game. (Or refer to the colors listed "
                    "in **.worth**)")
            elif console not in consoleList:
                await ctx.send(
                    "> Please make sure the console type is written the correct way. (Only supporting PC, "
                    "PS4 and Xbox at the moment")


###Flip a coin
@client.command(pass_context=True, aliases=['coinflip', 'cflip'])
async def flip(ctx):
    x = randint(1, 2)

    if x == 1:
        e = discord.Embed(colour=discord.Colour.green())
        e.set_image(url='https://i.imgur.com/0D97Lkp.png')
        await ctx.send(embed=e)
        print(f"{ctx.message.author.name} flipped a coin. It landed on heads. || {ctx.message.guild}\n")

    else:
        e = discord.Embed(colour=discord.Colour.green())
        e.set_image(url='https://i.imgur.com/3gNQsOo.png')
        await ctx.send(embed=e)
        print(f"{ctx.message.author.name} flipped a coin. It landed on tails. || {ctx.message.guild}\n")


###Random fact
@client.command(pass_context=True, aliases=['facts'])
async def fact(ctx):
    stamp = time.time()
    timeStamp = datetime.fromtimestamp(stamp).strftime('%d-%m-%y %H:%M:%S')
    url = "https://uselessfacts.jsph.pl/random.txt?language=en"
    r = requests.get(url).text
    fin = r.replace("Source: [djtech.net](http://www.djtech.net/humor/useless_facts.htm)", "").strip()
    await ctx.send(fin)
    print(f"{timeStamp}: Spitting out random facts -- ({fin}) || {ctx.message.guild}\n")


###Purge chat
@client.command(pass_context=True, aliases=['purge', 'clears', 'wipe', 'del', 'delete'])
@has_permissions(manage_messages=True)
async def clear(ctx, number=99):
    stamp = time.time()
    timeStamp = datetime.fromtimestamp(stamp).strftime('%d-%m-%y %H:%M:%S')
    await ctx.channel.purge(limit=number + 1)
    print(f"{timeStamp}: Deleted {str(number)} messages in {ctx.message.guild}\n")


###Activate Gatekeeper for server
@client.command(pass_context=True, aliases=['gk'])
@has_permissions(administrator=True)
async def gatekeeper(ctx, mode='on', role=''):
    if mode.lower() == 'on':
        if not role == '':
            role = role.replace('<@&', '')
            role = role.replace('>', '')
            with open("E:\\Scripts\\Python\\Nugbot\\servers_info.json", 'r') as current:
                current_servers = (json.load(current))
            print(current_servers)
            print("-----")
            try:
                if ctx.guild.name in current_servers.keys():
                    this_server = current_servers[ctx.guild.name]

                    if not this_server['channel'] == ctx.message.channel.id and this_server['role'] == role:
                        this_server['channel'] = ctx.message.channel.id
                        this_server['role'] = role

                        with open('E:\\Scripts\\Python\\Nugbot\\servers_info.json', 'w') as add_server:
                            json.dump(current_servers, add_server)
                        print(f'Updated Gatekeeper settings for {ctx.guild.name}')
                        await ctx.send("Updated server settings for Gatekeeper mode :thumbsup:")
                    else:
                        await ctx.send("This channel and role is already selected for Gatekeeper mode :thumbsup:")

                else:
                    current_servers[ctx.guild.name]['channel'] = ctx.message.channel.id
                    current_servers[ctx.guild.name]['role'] = role
                    current_servers[ctx.guild.name]['gatekeeper'] = "True"

                    with open('E:\\Scripts\\Python\\Nugbot\\servers_info.json', 'w') as add_server:
                        json.dump(current_servers, add_server, indent=4)
                    print(f'Activated Gatekeeper in {ctx.guild.name}')
                    await ctx.send("Gatekeeper activated :thumbsup:")

            except KeyError:
                current_servers.update({
                    ctx.guild.name: {
                        "guild_id": ctx.guild.id,
                        "channel": ctx.message.channel.id,
                        "role": role,
                        "gatekeeper": "True"
                    }
                })
                with open('E:\\Scripts\\Python\\Nugbot\\servers_info.json', 'w') as add_server:
                    json.dump(current_servers, add_server, indent=4)
                print(f'Activated Gatekeeper in {ctx.guild.name}')
                await ctx.send("Gatekeeper activated :thumbsup:")

        else:
            await ctx.send('Make sure to include the role you want to set to the newcomers :point_up:')

    if mode.lower() == 'off':
        with open('E:\\Scripts\\Python\\Nugbot\\servers_info.json', 'r') as fp:
            server_info = (json.load(fp))
        server_info.update({ctx.guild.name: {
            "guild_id": ctx.guild.id,
            "channel": "",
            "role": "",
            "gatekeeper": "False"
        }})
        with open('E:\\Scripts\\Python\\Nugbot\\servers_info.json', 'w') as add_server:
            json.dump(server_info, add_server)
        await ctx.send("Gatekeeper deactivated.")
        print(f'Deactivated Gatekeeper for {ctx.guild.name}')

    if mode.lower() != 'on' and mode.lower() != 'off':
        await ctx.send("Unknown mode... Example use: *gatekeeper on @thatnewbierole*")


@client.command(pass_context=True)
async def userinfo(ctx, member: Member):
    embed = discord.Embed(colour=discord.Colour.dark_gold())
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="User:", value=member, inline=False)
    embed.add_field(name="Created at:", value=member.created_at, inline=False)
    embed.add_field(name="Joined server at:", value=member.joined_at, inline=False)
    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def readlog(ctx):
    for entry in ctx.guild.audit_logs(limit=2):
        print(entry)


###Hugs!
@client.command(pass_context=True)
async def hug(ctx, member: Member):
    stamp = time.time()
    timeStamp = datetime.fromtimestamp(stamp).strftime('%d-%m-%y %H:%M:%S')
    embed = discord.Embed(colour=discord.Colour.green())
    embed.set_author(name=f"{ctx.message.author.name} hugs {member.name}")
    hug_col = ['https://i.imgur.com/b1Rcb.gif', 'https://i.imgur.com/NsbWDnW.gif', 'https://i.imgur.com/bUAuTXs.gif',
               'https://i.imgur.com/QUYEX4M.gif', 'https://i.imgur.com/9L5FwI8.gif', 'https://i.imgur.com/z1b0tse.gif',
               'https://i.imgur.com/T9A4DfG.gif', 'https://i.imgur.com/UN29yMD.gif', 'https://i.imgur.com/YtWCHd0.gif',
               'https://i.imgur.com/c1HAZqs.gif', 'https://i.imgur.com/oapaLEO.gif', 'https://i.imgur.com/i3lYZye.gif',
               'https://i.imgur.com/KgvQa15.gif', 'https://i.imgur.com/qIfv8fZ.gif', 'https://i.imgur.com/DNKdHMg.gif',
               'https://i.imgur.com/zgQS1g3.gif', 'https://i.imgur.com/LrvydKB.gif', 'https://i.imgur.com/Pc8zjUT.gif',
               'https://i.imgur.com/DSBVwwU.gif', 'https://i.imgur.com/QnHpXIQ.gif', 'https://i.imgur.com/PGq3Vpn.gif',
               'https://i.imgur.com/NGefdBg.gif', 'https://i.imgur.com/5OP70V7.gif', 'https://i.imgur.com/L1S0ynZ.gif',
               'https://i.imgur.com/yon5Wqd.gif', 'https://i.imgur.com/wdt8qCD.gif', 'https://i.imgur.com/KTKHP4b.gif',
               'https://i.imgur.com/pzUkiLl.gif', 'https://i.imgur.com/A35uJxO.gif', 'https://i.imgur.com/KeyP8hS.gif',
               'https://i.imgur.com/HGxuibe.gif', 'https://i.imgur.com/DY5mqQI.gif', 'https://i.imgur.com/yKjGH8x.gif',
               'https://i.imgur.com/vY7dGRd.gif', 'https://i.imgur.com/Ed2vXU5.gif', 'https://i.imgur.com/QdLD4OO.gif',
               'https://i.imgur.com/GJnoHy6.gif', 'https://i.imgur.com/yZDp8to.gif', 'https://i.imgur.com/FcDc4.gif',
               'https://i.imgur.com/4Eo2HWB.gif', 'https://i.imgur.com/9PwxrCH.gif', 'https://i.imgur.com/DaGG4HR.gif',
               'https://i.imgur.com/Rv41Vs5.gif', 'https://i.imgur.com/iUUamo2.gif', 'https://i.imgur.com/gWo14GX.gif',
               'https://i.imgur.com/iuN3cSj.gif', 'https://i.imgur.com/7VsEllT.gif', 'https://i.imgur.com/OAXMT8b.gif',
               'https://i.imgur.com/aFPRJGV.gif', 'https://i.imgur.com/FCXa6Gx.gif', 'https://i.imgur.com/VgP2ONn.gif',
               'https://i.imgur.com/ytpwtDJ.gif', 'https://i.imgur.com/34Ldmbz.gif', 'https://i.imgur.com/LwF6XOc.gif',
               'https://i.imgur.com/daowaXJ.gif', 'https://i.imgur.com/kSWpxnG.gif']
    rand = random.choice(hug_col)
    embed.set_image(url=random.choice(hug_col))
    await ctx.send(embed=embed)
    print(f"{timeStamp}: Sending hugs in {ctx.message.guild}")


###Slap
@client.command(pass_context=True)
async def slap(ctx, member: Member):
    stamp = time.time()
    timeStamp = datetime.fromtimestamp(stamp).strftime('%d-%m-%y %H:%M:%S')
    embed = discord.Embed(colour=discord.Colour.green())
    embed.set_author(name=f"{ctx.message.author.name} slapped {member.name}")
    slap_col = ['https://i.imgur.com/9GxTsgl.gif', 'https://i.imgur.com/uwHDm3r.gif', 'https://i.imgur.com/mT4VjD6.gif',
                'https://i.imgur.com/w66ZqGR.gif', 'https://i.imgur.com/lQZ3Tr5.gif', 'https://i.imgur.com/1FyrbwB.gif',
                'https://i.imgur.com/nuDmQu5.gif', 'https://i.imgur.com/wlLCjRo.gif', 'https://i.imgur.com/sVeYncu.gif',
                'https://i.imgur.com/1Uvfak1.gif', 'https://i.imgur.com/xylnYFw.gif', 'https://i.imgur.com/dBUtmsq.gif',
                'https://i.imgur.com/n6sJHYY.gif', 'https://i.imgur.com/p3Hjy3q.gif',
                'https://i.imgur.com/3Wy0d6R.gif', 'https://i.imgur.com/NEwiIsK.gif', 'https://i.imgur.com/qwunEAS.gif',
                'https://i.imgur.com/Si5W4VF.gif', 'https://i.imgur.com/JEO2XAt.gif', 'https://i.imgur.com/FWIdKzK.gif',
                'https://i.imgur.com/ik594Wg.gif', 'https://i.imgur.com/8gpUKMc.gif', 'https://i.imgur.com/3JlVi6P.gif',
                'https://i.imgur.com/vp4BYmx.gif', 'https://i.imgur.com/MmhPxip.gif', 'https://i.imgur.com/W8ZL9zn.gif',
                'https://i.imgur.com/Jd3wuwj.gif', 'https://i.imgur.com/Sasm6eY.gif', 'https://i.imgur.com/nvuCVg7.gif',
                'https://i.imgur.com/JbXa8oJ.gif',
                'https://i.imgur.com/dBdHrCI.gif', 'https://i.imgur.com/w4iZeSW.gif', 'https://i.imgur.com/DgCnHoD.gif',
                'https://i.imgur.com/hpc7zcj.gif', 'https://i.imgur.com/U7iSGZW.gif', 'https://i.imgur.com/luv7WOg.gif',
                'https://i.imgur.com/S8ndobN.gif', 'https://i.imgur.com/jIq6RcZ.gif', 'https://i.imgur.com/hvU4fCG.gif',
                'https://i.imgur.com/TqnOU0M.gif', 'https://i.imgur.com/8hsSb0i.gif', 'https://i.imgur.com/5AamjO0.gif',
                'https://i.imgur.com/rrhjU3T.gif', 'https://i.imgur.com/Xrp1ZGx.gif', 'https://i.imgur.com/LZf7I9R.gif']
    rand = random.choice(slap_col)
    embed.set_image(url=random.choice(slap_col))
    await ctx.send(embed=embed)
    print(f"{timeStamp}: Handing out slaps in {ctx.message.guild}")


###Kill the bot
@client.command()
async def die(ctx):
    f = str(ctx.author.id)

    if f == "189974308355964928":
        await ctx.send('> rip me')
        print("Closing client...")
        await client.close()

    else:
        await ctx.send("> lol. You're way too weak to kill me. :joy:")


@client.command(pass_context=True, aliases=['g'])
async def gamble(ctx, bet="", mode="", choice=""):
    with open("user_info.json", 'r') as userfile:
        userinfo = (json.load(userfile))

    money = userinfo[str(ctx.message.guild.id)][str(ctx.message.author.id)]['Money']

    if bet == "0":
        await ctx.send(f"{ctx.message.author.name} rolled 100!! They won 1000000 nugs! <:5headNug:706089147080638504>")
        return

    if str(bet).lower() == "all":  # Ez bet all
        bet = userinfo[str(ctx.message.guild.id)][str(ctx.message.author.id)]['Money']

    if str(bet).lower() == "half":  # Ez bet half
        bet = (userinfo[str(ctx.message.guild.id)][str(ctx.message.author.id)]['Money'] / 2)

    if "%" in str(bet):
        bet = bet.replace("%", "")
        if int(bet) != 0 and int(bet) <= 100:
            money = userinfo[str(ctx.message.guild.id)][str(ctx.message.author.id)]['Money']
            bet = round((money / 100) * int(bet))
        else:
            await ctx.send("Yeah nah.")
            return

    try:
        bet = int(bet)
    except Exception as e:
        print(e)
        return

    if bet <= 0 or type(bet) != int:
        await ctx.send("> Please enter a valid bet.")
        return

    if userinfo[str(ctx.message.guild.id)][str(ctx.message.author.id)]['Money'] < bet:  # Check if they have enough
        await ctx.send("> Gurl you too broke.")
        return

    if mode.lower() in ["flip", "coin"]:  # Coinflip
        if choice == "" or not choice.lower() in ["heads", "tails"]:
            await ctx.send("> Please choose heads or tails.")
            return

        cflip = randint(1, 2)

        if cflip == 1:
            if choice.lower() == "heads":
                await ctx.send(f"> It landed on heads! You won {bet} nuggets!")
                # print(f"{ctx.message.author.name} bet on heads and won {bet} nugs.")
                money = (money + bet)

            else:
                await ctx.send(f"> It landed on tails. You lost {bet} nuggets :slight_frown:")
                # print(f"{ctx.message.author.name} bet on tails and lost {bet} nugs.")
                money = (money - bet)

        elif cflip == 2:
            if choice.lower() == "tails":
                await ctx.send(f"> It landed on tails! You won {bet} nuggets!")
                # print(f"{ctx.message.author.name} bet on tails and won {bet} nugs.")
                money = (money + bet)

            else:
                await ctx.send(f"> It landed on tails. You lost {bet} nuggets. :slight_frown:")
                # print(f"{ctx.message.author.name} bet on heads and lost {bet} nugs.")
                money = (money - bet)

        userinfo[str(ctx.message.guild.id)][str(ctx.message.author.id)]['Money'] = money

        with open("user_info.json", 'w') as userfile:
            json.dump(userinfo, userfile, indent=4)

    if mode.lower() == "roll" or mode == "" and bet != 0:  # Roll 1-100
        roll = randint(1, 100)
        if roll == 100:
            money = money + (bet * 3)
            await ctx.send(f"> {ctx.message.author.name} rolled **{roll}**!! They win {bet} nuggets!")

        elif roll >= 50:
            money = money + bet
            await ctx.send(f"> {ctx.message.author.name} rolled **{roll}**! They win {bet} nuggets!")

        elif roll < 50:
            money = money - bet
            await ctx.send(f"> {ctx.message.author.name} rolled **{roll}**. {bet} nuggies gone. :pensive:")

    with open("user_info.json", 'w') as userfile:
        userinfo[str(ctx.message.guild.id)][str(ctx.message.author.id)]['Money'] = money
        json.dump(userinfo, userfile, indent=4)


@client.command(pass_context=True, aliases=['bal'])
async def balance(ctx):
    with open("user_info.json", 'r') as userfile:
        userinfo = (json.load(userfile))
    await ctx.send(
        f"You currently have {userinfo[str(ctx.message.guild.id)][str(ctx.message.author.id)]['Money']} nuggets. "
        f"<:5headNug:706089147080638504>")


@client.command(pass_context=True)
async def give(ctx, member: Member, amount):
    if str(ctx.message.author.id) == str(member.id) or int(amount) <= 0:
        await ctx.send("> Magine.")
        return

    with open("user_info.json", 'r') as userfile:
        userinfo = (json.load(userfile))

    giverBalance = userinfo[str(ctx.guild.id)][str(ctx.message.author.id)]['Money']
    receiverBalance = userinfo[str(ctx.guild.id)][str(member.id)]['Money']

    if str(amount.lower()) == "all":
        amount = giverBalance

    if int(amount) > int(giverBalance):
        await ctx.send("> You don't have that kind of money, kid.")
        return

    userinfo[str(ctx.guild.id)][str(ctx.message.author.id)]['Money'] = giverBalance - int(amount)
    userinfo[str(ctx.guild.id)][str(member.id)]['Money'] = receiverBalance + int(amount)

    with open("user_info.json", 'w') as userfile:
        json.dump(userinfo, userfile, indent=4)

    print(f"{ctx.message.author} - ({giverBalance}) gave {amount} nuggets to {member.name} - ({receiverBalance})")
    await ctx.send(
        f"> :money_with_wings:{ctx.message.author.name} gave {amount} nuggets to {member.name}:money_with_wings:")


###Giveaway!
@client.command(pass_context=True, aliases=['gift'])
async def giveaway(ctx, mode='start'):
    global giveawayUsers
    global gameList
    global gamesDict
    global giveawayStatus

    with open("msgcount.txt", "r") as file:
        msgCount = int(file.read())

    n1 = "\n"
    f = str(ctx.author.id)
    mode = str(mode)
    channel = client.get_channel(715221198140866681)
    # Start the giveaway!
    if f == "189974308355964928" or msgCount == 0:
        if mode.lower() == 'start':
            giveawayUsers = ['189974308355964928']
            gameList = []
            giveawayStatus = 1
            # Load gamelist.json into a dict
            with open('gamelist.json', 'r') as fp:
                gamesDict = json.load(fp)

            # Push game names from dict to list.
            for game in gamesDict.keys():
                gameList.append(game)

            # Upload current collection to pastebin >> post link on start
            gamePaste = HasteBinApi("\n".join(gameList).encode("utf-8"))
            pasteKey = gamePaste.get_key()
            fixedPaste = f"http://hastebin.com/{pasteKey}"

            await channel.send(
                f"Giveaway time, {ctx.message.guild.default_role}! React to this post for a chance to win one out of {len(gameList)} games! {n1}The current list of games can be found at: {fixedPaste}.")
        # End the giveaway!
        if mode.lower() == "end":
            giveawayStatus = 0
            winner = random.choice(giveawayUsers)
            winner = client.get_user(int(winner))
            prize = random.choice(gameList)
            await channel.send(
                f"Congratulations to {winner.mention}! You've won **{prize}** {n1}The key(s) will be DM'd to you. If you don't get a DM, please yell at Fluke, and he'll sort it out.")
            print(f"Winner of the giveaway is {winner}")
            prizeKeys = gamesDict.get(prize)
            prizeKeysFix = str(prizeKeys).replace("{'Key': '", "")  # Jank as fuck
            prizeKeysFix = prizeKeysFix.replace("'}", "")  # But it works for now
            await winner.send(
                f"Congratulations! You've won {prize}! Here is your steam code to redeem your game: {prizeKeysFix}")
            print(f"Game: {prize} -- Key: {prizeKeysFix}")
            # Remove game from collection
            del gamesDict[prize]
            with open('gamelist.json', 'w') as fp:
                json.dump(gamesDict, fp)
    # If someone else tries to initiate a giveaway
    else:
        await ctx.send("Nice try.")


###Send msg to predetermined channel
@client.command(pass_context=True)
async def ping(ctx):
    stamp = time.time()
    timeStamp = datetime.fromtimestamp(stamp).strftime('%d-%m-%y %H:%M:%S')
    await ctx.send("Pong")
    print(f"{timeStamp}: Pong! || {ctx.message.guild}")


@client.command(pass_context=True)
async def nou(ctx):
    await ctx.message.delete()
    await ctx.send("> no u")


@client.command(pass_context=True)
@has_permissions(manage_guild=True)
async def blacklist(ctx, mode="", word=""):
    global wordblacklist
    if mode.lower() == "add":
        if not word in wordblacklist:
            wordblacklist.add(word)
            with open("blacklist.json", "w") as blfile:
                json.dump(list(wordblacklist), blfile)
            await ctx.send(f"Added {word} to the blacklist.")
            print(f"{ctx.message.author.name} added {word} to the blacklist.")
        else:
            await ctx.send(f"{word} is already blacklisted.")

    if mode.lower() == "remove":
        if word in wordblacklist:
            wordblacklist.remove(word)
            with open("blacklist.json", "w") as blfile:
                json.dump(list(wordblacklist), blfile)
            await ctx.send(f"Removed {word} from the blacklist.")
            print(f"{ctx.message.author.name} removed {word} from the blacklist.")
        else:
            await ctx.send(f"{word} is not blacklisted.")

    if mode.lower() == "list":
        blList = list(wordblacklist)
        blList.sort()
        await ctx.send(f"`{blList}`")


@client.command(pass_context=True)
@has_permissions(manage_guild=True)
async def logging(ctx, status="", *args):
    with open("servers_info.json", 'r') as sInfo:
        servers_info = (json.load(sInfo))

    if status.lower() == "info" or status.lower() == "help":
        embed = discord.Embed(colour=discord.Colour.blue(), title="Logging functions")
        embed.add_field(name="Usage:", value="`.logging on/off (function)`")
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="All", value="Activates everything below", inline=False)
        embed.add_field(name="User join", value="A user joins", inline=False)
        embed.add_field(name="User leave", value="A user leaves", inline=False)
        embed.add_field(name="User kick", value="A user is kicked", inline=False)
        embed.add_field(name="User ban", value="A user is banned", inline=False)
        embed.add_field(name="User update", value="A user changes nick or gains/loses a role", inline=False)
        embed.add_field(name="Message edit", value="A message is edited", inline=False)
        embed.add_field(name="Message delete", value="A message is deleted", inline=False)
        embed.add_field(name="Invite create", value="An invite is created", inline=False)
        embed.add_field(name="Invite delete", value="An invite is deleted", inline=False)
        embed.add_field(name="Channel create", value="A channel is created", inline=False)
        embed.add_field(name="Channel delete", value="A channel is deleted", inline=False)
        embed.add_field(name="Channel update", value="A channel is edited", inline=False)
        await ctx.send(embed=embed)
        return

    try:
        function = f"{args[0]} {args[1]}"
    except IndexError:
        function = args[0]

    serverDict = {'user join': 'User Join', 'user leave': 'User Leave', 'user update': 'User Update',
                  'user kick': 'User Kick', 'user ban': 'User Ban', 'user unban': 'User Unban',
                  'bot join': 'Bot Join', 'message edit': 'Message Edit', 'message delete': 'Message Delete',
                  'message pin': 'Message Pin', 'message unpin': 'Message Unpin', 'invite create': 'Invite Create',
                  'invite delete': 'Invite Delete', 'invite update': 'Invite Update',
                  'channel create': 'Channel Create',
                  'channel delete': 'Channel Delete', 'channel update': 'Channel Update', 'role create': 'Role Create',
                  'role delete': 'Role Delete', 'role update': 'Role Update', 'emoji create': 'Emoji Create',
                  'emoji delete': 'Emoji Delete', 'emoji update': 'Emoji Update'}

    if function.lower() == "all":
        if status.lower() == "on":
            for item in servers_info[str(ctx.guild.id)].keys():
                if item != "Gatekeeper":
                    servers_info[str(ctx.guild.id)][item]["Status"] = "True"
                    servers_info[str(ctx.guild.id)][item]["Channel"] = str(ctx.channel.id)
            await ctx.send("> Logging enabled.")

        elif status.lower() == "off":
            for item in servers_info[str(ctx.guild.id)].keys():
                if item != "Gatekeeper":
                    servers_info[str(ctx.guild.id)][item]["Status"] = "False"
                    servers_info[str(ctx.guild.id)][item]["Channel"] = ""
            await ctx.send("> Logging disabled.")

        else:
            await ctx.send("> Accepted status names are *on/off*")
            return

    elif function.lower() in serverDict.keys():
        function = serverDict[function.lower()]

        if status.lower() == "on":
            servers_info[str(ctx.guild.id)][function]['Status'] = "True"
            servers_info[str(ctx.guild.id)][function]['Channel'] = str(ctx.channel.id)
            await ctx.send(f"> Logging enabled for {function}")

        elif status.lower() == "off":
            servers_info[str(ctx.guild.id)][function]['Status'] = "False"
            servers_info[str(ctx.guild.id)][function]['Channel'] = ""
            await ctx.send(f"> Logging disabled for {function}")

        else:
            await ctx.send("> Accepted status names are *on/off*")
            return
    else:
        await ctx.send(f"> {function} is not an accepted function. Please refer to the list in `.logging info`")
        return

    with open("servers_info.json", 'w') as sInfo:
        json.dump(servers_info, sInfo, indent=4)


@client.command(pass_context=True)
async def jsontest(ctx, emoji, role: discord.Role):
    with open("servertest.json", 'r') as sTest:
        serverTest = (json.load(sTest))

    try:
        serverTest = {
            str(ctx.guild.id): {
                emoji: {
                    "Channel": ctx.channel.id,
                    "Role": role.name
                }}}
    except Exception as e:
        print(e)
    with open("servertest.json", 'w') as sTest:
        json.dump(serverTest, sTest, indent=4)


@client.command(pass_context=True)
async def serversetup(ctx):
    with open("servers_info.json", "r") as sInfo:
        servers_info = (json.load(sInfo))

    for guild in client.guilds:
        servers_info[str(guild.id)] = {}
        servers_info[str(guild.id)].update({
            "Gatekeeper": {
                "Status": "False",
                "Channel": "",
                "Role": ""
            },
            "Logging": {
                "Status": "False",
                "Channel": ""
            },
            "User Join": {
                "Status": "False",
                "Channel": ""
            },
            "User Leave": {
                "Status": "False",
                "Channel": ""
            },
            "User Update": {
                "Status": "False",
                "Channel": ""
            },
            "User Kick": {
                "Status": "False",
                "Channel": ""
            },
            "User Ban": {
                "Status": "False",
                "Channel": ""
            },
            "User Unban": {
                "Status": "False",
                "Channel": ""
            },
            "Bot Join": {
                "Status": "False",
                "Channel": ""
            },
            "Message Edit": {
                "Status": "False",
                "Channel": ""
            },
            "Message Delete": {
                "Status": "False",
                "Channel": ""
            },
            "Message Pin": {
                "Status": "False",
                "Channel": ""
            },
            "Message Unpin": {
                "Status": "False",
                "Channel": ""
            },
            "Invite Create": {
                "Status": "False",
                "Channel": ""
            },
            "Invite Delete": {
                "Status": "False",
                "Channel": ""
            },
            "Invite Update": {
                "Status": "False",
                "Channel": ""
            },
            "Channel Create": {
                "Status": "False",
                "Channel": ""
            },
            "Channel Delete": {
                "Status": "False",
                "Channel": ""
            },
            "Channel Update": {
                "Status": "False",
                "Channel": ""
            },
            "Role Create": {
                "Status": "False",
                "Channel": ""
            },
            "Role Delete": {
                "Status": "False",
                "Channel": ""
            },
            "Role Update": {
                "Status": "False",
                "Channel": ""
            },
            "Emoji Create": {
                "Status": "False",
                "Channel": ""
            },
            "Emoji Delete": {
                "Status": "False",
                "Channel": ""
            },
            "Emoji Update": {
                "Status": "False",
                "Channel": ""
            }
        })
    with open("servers_info.json", 'w') as sInfo:
        json.dump(servers_info, sInfo, indent=4)


@client.command(pass_context=True)
@has_permissions(manage_guild=True)
async def whitelist(ctx, mode="", word=""):
    global wordwhitelist
    if mode.lower() == "add":
        if not word in wordwhitelist:
            wordwhitelist.add(word)
            with open("whitelist.json", "w") as wlfile:
                json.dump(list(wordwhitelist), wlfile)
            await ctx.send(f"Added {word} to the whitelist.")
            print(f"{ctx.message.author.name} added {word} to the whitelist.")
        else:
            await ctx.send(f"{word} is already whitelisted.")

    if mode.lower() == "remove":
        if word in wordwhitelist:
            wordwhitelist.remove(word)
            with open("whitelist.json", "w") as blfile:
                json.dump(list(wordwhitelist), blfile)
            await ctx.send(f"Removed {word} from the whitelist.")
            print(f"{ctx.message.author.name} removed {word} from the whitelist.")
        else:
            await ctx.send(f"{word} is not whitelisted.")

    if mode.lower() == "list":
        wlList = list(wordwhitelist)
        wlList.sort()
        await ctx.send(f"`{wlList}`")


@client.command(pass_context=True, aliases=['timeout'])
@has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, seconds):
    global muteDict
    try:
        secondInt = int(seconds)
        if secondInt > 3600:
            await ctx.send("> Sounds a bit harsh...")
            return

        if secondInt <= 0:
            await ctx.send("> Now that's just silly.")
            return

        muteDict[member.id] = secondInt

        guild = await client.fetch_guild(ctx.message.guild.id)
        role = discord.utils.get(guild.roles, name="Muted")
        await member.add_roles(role, reason="Muted")
        await ctx.send(f"> {member.mention} was muted for {seconds} seconds.")

        while True:
            muteDict[member.id] -= 1
            if muteDict[member.id] == 0:
                await member.remove_roles(role, reason="Timeout over.")
                del muteDict[member.id]
                break

            await asyncio.sleep(1)
    except Exception as e:
        print(e)


@client.command(pass_context=True, aliases=['rustl'])
async def rustlookup(ctx, player):
    # Get Steam64 ID from profile
    b64url = f"https://steamidfinder.com/lookup/{player}"
    r = requests.get(b64url)
    s64ID = re.findall("(\d{17})\D", r.text)[0]

    try:
        r = requests.get(f"https://rust-stats.com/user/{str(s64ID)}/")
        pname = re.findall('Rust stats  - profile stats: (.+)', r.text)
        pname = re.sub("</title>", "", pname[0])

        hours = re.findall('play_time"><span>(\d+\.\d)', r.text)
        hsPerc = re.findall('crack.svg" class="img-responsive title-logo">\n<span>(\d+)', r.text)
        hsTotal = re.findall('stats="headshot_player"><span>(\d+)', r.text)
        hitsTotal = re.findall('stats="hit_player"><span>(\d+)', r.text)
        hitPerc = re.findall('gunshot.svg" class="img-responsive title-logo">\n<span>(\d+)', r.text)
        playerKill = re.findall('kill_type" data-kill_type="player">(\d+)', r.text)
        playerDeath = re.findall('death_type" data-death_type="player">(\d+)', r.text)
        kdr = round((int(playerKill[0]) / int(playerDeath[0])), 2)

        embed = discord.Embed(colour=discord.Colour.red(), title=pname)
        embed.add_field(name=f"🕑 Hours played: {hours[0]}", value="\u200b", inline=False)
        embed.add_field(name=f":crossed_swords: PvP kills: {playerKill[0]}",
                        value=f":headstone: PvP deaths: {playerDeath[0]}", inline=False)
        embed.add_field(name=f":chart_with_upwards_trend: PvP KDR: {kdr}", value="\u200b", inline=False)
        embed.add_field(name=f":dart: Shots landed: {hitsTotal[0]} ({hitPerc[0]}% accuracy)",
                        value=f":skull: Headshots: {hsTotal[0]} - ({hsPerc[0]}% accuracy)", inline=False)
        await ctx.send(embed=embed)

    except IndexError:
        await ctx.send("Private profile. :slight_frown:")
        return


###Kick user
@client.command(pass_context=True)
@has_permissions(kick_members=True)
async def kick(ctx, member: Member):

    stamp = time.time()
    timeStamp = datetime.fromtimestamp(stamp).strftime('%d-%m-%y %H:%M:%S')
    await Member.kick(member)
    kickCol = ["https://tenor.com/wYlS.gif", "https://tenor.com/Fo7L.gif", "https://tenor.com/o4Yl.gif",
               "https://tenor.com/riyn.gif",
               "https://tenor.com/zRrv.gif", "https://tenor.com/FLaO.gif", "https://tenor.com/1WMI.gif"]
    await ctx.send(random.choice(kickCol))
    print(f"{timeStamp}: Kicking {str(member)} from {ctx.message.guild}")


###Swing the banhammer
@client.command(pass_context=True)
@has_permissions(ban_members=True)
async def ban(ctx, member: Member):
    try:
        stamp = time.time()
        timeStamp = datetime.fromtimestamp(stamp).strftime('%d-%m-%y %H:%M:%S')
        await Member.ban(member)
        banCol = ["https://gph.is/1eRPX9V", "https://gph.is/g/aKOQ6Xa", "https://gph.is/2d6TfsV",
                  "https://tenor.com/58uD.gif", "https://tenor.com/TA00.gif",
                  "https://tenor.com/x8rZ.gif", "https://tenor.com/FYi9.gif", "https://tenor.com/JZWB.gif",
                  "https://tenor.com/VbLN.gif"]
        await ctx.send(random.choice(banCol))
        print(f"{timeStamp}: Banning {str(member)} from {ctx.message.guild}")
    except Exception as e:
        print(e)


@client.command(pass_context=True)
async def daevyroles(ctx):
    regionList = ['🔴', '🟠', '🟡', '🟢', '🔵', '🟣']
    consoleList = ['<:windows:822941259324719164>', '<:xbox:822925124541218906>', '<:playstation:822925124306206770>',
                   '<:switch:822925124570185779>']
    if ctx.author.id == 189974308355964928:
        embed1 = discord.Embed(colour=discord.Colour.red(), title="Pick your region")
        embed1.add_field(name="AF: :red_circle:", value="**AS:** :orange_circle:",
                         inline=False)
        embed1.add_field(name="EU: :yellow_circle:", value="**NA:** :green_circle:", inline=False)
        embed1.add_field(name="SA: :blue_circle:", value="**OCE:** :purple_circle:", inline=False)
        embed2 = discord.Embed(colour=discord.Colour.red(), title="Choose your console(s)")
        embed2.add_field(name="**PC**: <:windows:822941259324719164>", value="**Xbox**: <:xbox:822925124541218906>",
                         inline=False)
        embed2.add_field(name="**Playstation**: <:playstation:822925124306206770>",
                         value="**Switch**: <:switch:822925124570185779>", inline=False)
        msg1 = await ctx.send(embed=embed1)
        msg2 = await ctx.send(embed=embed2)
        await ctx.message.delete()

        for item in regionList:
            await msg1.add_reaction(item)

        for item in consoleList:
            await msg2.add_reaction(item)


@client.command(pass_context=True)
async def buckoroles(ctx):
    msg = await ctx.send(
        'If you want notifications for announcements (including when I go live) react to this message with ":heart_eyes:"')
    await ctx.message.delete()
    await msg.add_reaction("😍")


###Unban user (using user ID)
@client.command(pass_context=True)
@has_permissions(ban_members=True)
async def unban(ctx, id: int):
    user = await client.fetch_user(id)
    await ctx.guild.unban(user)
    await ctx.send(user.mention + "has been unbanned!")
    unbanCol = ["https://gph.is/2nGQuo1", "https://gph.is/2ygS19X", "https://gph.is/2F24w9F", "https://gph.is/1UvAo9r",
                "https://gph.is/1x0Mw6v", "http://gph.is/2iRqu8n",
                "https://gph.is/1ZTM48O", "https://gph.is/2h3utwo"]
    await ctx.send(random.choice(unbanCol))
    print(f"Unbanning ID {str(user.mention)} in {ctx.message.guild}")


@client.event
async def on_message(message):
    channel = message.channel
    if message.author == client.user:
        return
    await client.process_commands(message)

    if message.content.lower() == "shut up":
        await channel.send("> No you.")

    # Giveaway based on messages
    global msgCount
    global giveawayStatus
    global latestMessageUser
    global tempmsg
    global tempauthor
    global tempguild

    if message.guild.id == 629882384879190027:
        if giveawayStatus == 0 and latestMessageUser[0] != message.author.name:
            msgCount += 1

            if msgCount % 100 == 0:
                print(f"Just reached {msgCount} messages!")
            latestMessageUser = [message.author.id]

            if msgCount < 500:
                with open("msgcount.txt", "w") as msgCountWrite:
                    msgCountWrite.write(str(msgCount))

            else:  # If 500 messages has been reached
                message.channel.send(f"{message.author} just initiated a giveaway! :partying_face:")
                msgCount = 0
                with open("msgcount.txt", "w") as msgCountWrite:
                    msgCountWrite.write(str(msgCount))
                await giveaway('start')

        else:  # If Giveaway is active
            return

    if tempmsg != message.content and not message.content.startswith(".") and not message.author.bot:
        money_reward = randint(1, 10)
        with open("user_info.json", "r") as userfile:
            userinfo = (json.load(userfile))

        old_money = userinfo[str(message.guild.id)][str(message.author.id)]['Money']
        new_money = old_money + money_reward

        userinfo[str(message.guild.id)][str(message.author.id)]['Money'] = new_money

        with open("user_info.json", "w") as userfile:
            json.dump(userinfo, userfile, indent=4)

    if tempmsg == message.content and "twitch" in message.content and tempauthor == message.author and tempguild == message.guild:
        await message.delete()
        await message.channel.send("> Once is enough")

    tempmsg = message.content
    tempauthor = message.author
    tempguild = message.guild


@client.event
async def on_member_join(member: discord.Member = None):
    x = ''
    global newUsers
    global wordblacklist
    global wordblacklist2
    global wordwhitelist
    global nicknames

    with open("servers_info.json", 'r') as sInfo:
        servers_info = (json.load(sInfo))

    if member.guild.id == 776892745981231154:  # Change names containing profanity - Daevy
        for word in wordblacklist:
            if word in member.name.lower():
                oldName = member.name
                nick = randint(0, len(nicknames))
                await member.edit(nick=nicknames[nick])
                channel = client.get_channel(776892745981231156)
                await channel.send(
                    f"{member.mention} - Your name has been changed to something a little cuter. "
                    f"If you disagree with this, ask a mod to return it to its former glory."
                    f" :slight_smile:")
                print(f"Changed {oldName}'s name to {nicknames[nick]}.")

    if member.guild.id == 788918979007348746:  # Change names - Bucko
        for word in wordblacklist2:
            if word in member.name.lower():
                oldName = member.name
                nick = randint(0, len(nicknames))
                await member.edit(nick=nicknames[nick])
                channel = client.get_channel(788918979501883403)
                logChannel = client.get_channel(826598714092683285)
                await channel.send(
                    f"{member.mention} - Your name has been changed to something a little cuter. "
                    f"If you disagree with this, ask a mod to return it to its former glory."
                    f" :slight_smile:")
                await logChannel.send(f"> Changed {oldName}'s name to {nicknames[nick]}.")

    if member.guild.id == 559389972797325362:  # Blacklist test server
        for bword in wordblacklist:
            if bword in member.name.lower():
                if member.name.lower() in wordwhitelist:
                    return
                else:
                    oldName = member.name
                    nick = randint(0, len(nicknames))
                    await member.edit(nick=nicknames[nick])
                    channel = client.get_channel(559389972797325364)
                    await channel.send(
                        f"{member.mention} - Your name has been changed to something a little cuter. If you disagree "
                        f"with this, ask a mod to return it to its former glory. "
                        f" :slight_smile:")
                    print(f"Changed {oldName}'s name to {nicknames[nick]}.")

    for channel in member.guild.channels:
        if str(channel) == "the-door":  # SimplyFluke
            await channel.send(
                f"""Welcome to the server, {member.mention}! Please read through the rules before hopping along. 
                :slight_smile:""")
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name='Rules:')
            embed.add_field(name='1: No racism or sexism.', value="-----------------", inline=False)
            embed.add_field(name='2: Keep it in English.', value="-----------------", inline=False)
            embed.add_field(name="3: Don't share personal information of yourself or other users.",
                            value="-----------------", inline=False)
            embed.add_field(name='4: Just behave, kids. At least a little bit.', value="-----------------",
                            inline=False)
            await channel.send(embed=embed)
            stamp = time.time()
            timeStamp = datetime.fromtimestamp(stamp).strftime('%d-%m-%y %H:%M:%S')
            print(f"{timeStamp}: {member.name} joined {member.guild}!")

        if str(channel) == "the-barn-door":  # Rebelz
            channel = client.get_channel(800066780328493077)
            await member.add_roles(member.guild.get_role(800066372549738496))  # Set role to Fresh Meat on entry

            # Captcha Time
            i1 = randint(1, 5)
            i2 = randint(1, 5)
            y = i1 + i2

            capDict = {1: '1️⃣',
                       2: '2️⃣',
                       3: '3️⃣',
                       4: '4️⃣',
                       5: '5️⃣',
                       6: '6️⃣',
                       7: '7️⃣',
                       8: '8️⃣',
                       9: '9️⃣',
                       10: '🔟'}
            if x != member.name:
                ans = capDict[y]
                embed = discord.Embed(colour=discord.Colour.red())
                embed.set_author(name=f"Welcome, {member.name}!")
                embed.add_field(name='Before you venture onwards...',
                                value=f'**what is {i1} + {i2}?**\nPlease answer by using the reactions below.',
                                inline=False)
                msg = await channel.send(embed=embed)

                x = member.name
                newUsers[str(member.id)] = ans

                with open('E:\\Scripts\\Python\\Nugbot\\newUsers.json', 'w') as fp:
                    json.dump(newUsers, fp)

                emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

                for emoji in emojis:
                    await msg.add_reaction(emoji)

                print(newUsers)

        if channel.id == 776892745981231156:  # Daevy
            channel = client.get_channel(823621712243327087)  # The-Crossbar
            await member.add_roles(member.guild.get_role(823621229185073162))  # Set role to Crossbar hero on entry

            # Captcha Time
            i1 = randint(1, 5)
            i2 = randint(1, 5)
            y = i1 + i2

            capDict = {1: '1️⃣',
                       2: '2️⃣',
                       3: '3️⃣',
                       4: '4️⃣',
                       5: '5️⃣',
                       6: '6️⃣',
                       7: '7️⃣',
                       8: '8️⃣',
                       9: '9️⃣',
                       10: '🔟'}
            if x != member.name:
                ans = capDict[y]
                embed = discord.Embed(colour=discord.Colour.red())
                embed.set_author(name=f"Welcome, {member.name}!")
                embed.add_field(name='Before you venture onwards...',
                                value=f'**what is {i1} + {i2}?**\nPlease answer by using the reactions below.',
                                inline=False)
                msg = await channel.send(embed=embed)

                x = member.name
                newUsers[str(member.id)] = ans

                with open('E:\\Scripts\\Python\\Nugbot\\newUsers.json', 'w') as fp:
                    json.dump(newUsers, fp)
                print(f"Updated New Users dictionary: {newUsers}")

                emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

                for emoji in emojis:
                    await msg.add_reaction(emoji)

                print(newUsers)
                # channel = client.get_channel(812514427509014569)
                # await channel.send(f"{member} joined the server.")

    if servers_info[str(member.guild.id)]['User Join']['Status'] == "True":
        channel = client.get_channel(int(servers_info[str(member.guild.id)]['User Join']['Channel']))
        embed = discord.Embed(colour=discord.Colour.dark_theme())
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=f"{member.display_name} joined the server.", value="\u200b")
        embed.set_footer(text=member.guild.name)
        await channel.send(embed=embed)

    print(f"{member} joined {member.guild}!")

    ### add users to user_info.json upon joining a server nugbot is in.
    with open("user_info.json", "r") as userfile:
        user_info = (json.load(userfile))

    if str(member.id) in user_info[str(member.guild.id)].keys():  # Check if they're already been added.
        return

    else:
        user_info[str(member.guild.id)].update({
            member.id: {
                "Name": member.name,
                "Money": 0,
                "rlconsole": "",
                "rlid": "",
                "epicID": "",
                "steamID": "",
                "console": "",
                "riotID": ""
            }
        })
        with open("user_info.json", "w") as userfile:
            json.dump(user_info, userfile, indent=4)


@client.event
async def on_member_remove(member):
    with open("servers_info.json", 'r') as sInfo:
        servers_info = (json.load(sInfo))

    if servers_info[str(member.guild.id)]['User Leave']['Status'] == "True":
        channel = client.get_channel(int(servers_info[str(member.guild.id)]['User Leave']['Channel']))
        stamp = time.time()
        timeStamp = datetime.fromtimestamp(stamp).strftime('%d-%m-%y %H:%M:%S')
        embed = discord.Embed(Colour=discord.Colour.dark_theme())
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="User Left", value=f"{member} left the server.")
        embed.set_footer(text=member.guild)
        await channel.send(embed=embed)


@client.event
async def on_raw_reaction_add(reaction):
    global giveawayUsers
    guild = client.get_guild(reaction.guild_id)
    member = guild.get_member(reaction.user_id)
    with open('E:\\Scripts\\Python\\NugBot\\newUsers.json', 'r') as fp:
        newUsers = (json.load(fp))
    if reaction.user_id != 559390333759258634:  # Prevent it from triggering on the bot

        if reaction.guild_id is None:
            return  # Reaction is in DM

        if reaction.channel_id == 715221198140866681:  # Giveaway \\ Nug
            if reaction.user_id not in giveawayUsers:
                giveawayUsers.append(reaction.user_id)
                stamp = time.time()
                timeStamp = datetime.fromtimestamp(stamp).strftime('%d-%m-%y %H:%M:%S')
                print(f"{timeStamp}: {reaction.user_name} has entered the giveaway!")
                print(f"Current users: {giveawayUsers}")

        if reaction.channel_id == 800066780328493077:  # Rebelz Welcome channel
            if newUsers[str(reaction.user_id)]:  # Prevent kicking mods and admins
                guild = client.get_guild(reaction.guild_id)
                member = guild.get_member(reaction.user_id)
                channel = client.get_channel(800066780328493077)  # Push channel ID to variable.

                if reaction.emoji.name == newUsers[str(reaction.user_id)]:  # Let them pass if right answer is given
                    await member.remove_roles(member.guild.get_role(800066372549738496))
                    with open("newUsers.json", "r") as userfile:
                        newUsers = (json.load(userfile))

                    del newUsers[str(reaction.user_id)]
                    with open("newUsers.json", 'w') as userfile:
                        json.dump(newUsers, userfile, indent=4)

                    if str(reaction.user_id) in failedAttempts:  # Remove them from failed attempts dict
                        del failedAttempts[str(reaction.user_id)]

                else:  # Yeet and log if not.
                    if str(reaction.user_id) in failedAttempts:
                        if failedAttempts[str(reaction.user_id)] == 2:
                            await member.ban(reaction.user)
                            await reaction.channel.send(f'Banned user {reaction.user_name}.')
                        else:
                            failedAttempts[str(reaction.user_id)] = 2
                            await member.kick(reaction.user, reason="Gatekeeper - Wrong answer")
                            await reaction.channel.send(
                                f'Kicked user {reaction.user_name}. They have 1 attempt remaining.')

                    else:
                        failedAttempts[str(reaction.user_id)] = 1
                        await member.kick()
                        await reaction.channel.send(
                            f'Kicked user {reaction.user_name}. They have 2 attempts remaining.')
                delete_arrival_msg = await channel.fetch_message(reaction.message_id)
                await delete_arrival_msg.delete()

        if reaction.channel_id == 823621712243327087:  # Daevy's Welcome channel
            if newUsers[str(reaction.user_id)]:  # Prevent kicking mods and admins
                guild = client.get_guild(reaction.guild_id)
                member = guild.get_member(reaction.user_id)
                channel = client.get_channel(823621712243327087)  # Push channel ID to variable.

                if reaction.emoji.name == newUsers[str(reaction.user_id)]:  # Let them pass if right answer is given
                    await member.remove_roles(member.guild.get_role(823621229185073162))
                    with open("newUsers.json", "r") as userfile:
                        newUsers = (json.load(userfile))

                    del newUsers[str(reaction.user_id)]
                    with open("newUsers.json", 'w') as userfile:
                        json.dump(newUsers, userfile, indent=4)

                    if str(reaction.user_id) in failedAttempts:  # Remove them from failed attempts dict
                        del failedAttempts[str(reaction.user_id)]

                else:  # Yeet and log if not.
                    if str(reaction.user_id) in failedAttempts:
                        if failedAttempts[str(reaction.user_id)] == 2:
                            await member.ban(reaction.user)
                            await channel.send(f'Banned user {reaction.user_name}.')
                        else:
                            failedAttempts[str(reaction.user_id)] = 2
                            await member.kick(reaction.user, reason="Gatekeeper - Wrong answer")
                            await channel.send(
                                f'Kicked user {reaction.user_name}. They have 1 attempt remaining.')

                    else:
                        failedAttempts[str(reaction.user_id)] = 1
                        await member.kick()
                        await channel.send(
                            f'Kicked user {reaction.user_name}. They have 2 attempts remaining.')
                delete_arrival_msg = await channel.fetch_message(reaction.message_id)
                await delete_arrival_msg.delete()

        if reaction.channel_id == 822933311231361034:  # Daevy's role channel
            reactDict = {'🟡': 'EU', '🟢': 'NA',
                         '🔴': 'AF', '🟠': 'AS',
                         '🔵': 'SA', '🟣': 'OCE',
                         'playstation': 'PS', 'switch': 'Switch',
                         'windows': 'PC', 'xbox': 'Xbox'}

            if reaction.emoji.name in reactDict.keys():
                role = discord.utils.get(guild.roles, name=reactDict[reaction.emoji.name])
                await member.add_roles(role, reason="React choice")
            else:
                channel = await client.fetch_channel(822933311231361034)
                message = await channel.fetch_message(reaction.message_id)
                await message.remove_reaction(reaction.emoji, member)

        if reaction.channel_id == 854012021094613042:  # Bucko
            reactDict = {'bronze1': "Bronze", "silver1": "Silver",
                         "gold1": "Gold", "platinum1": "Platinum", "diamond1": "Diamond", "champion1": "Champion",
                         "grandchamp1": "Grand Champion", "supersonic_legend": "Supersonic Legend", '🟡': 'EU',
                         '🟢': 'NA',
                         '🔴': 'AF', '🟠': 'AS', '🔵': 'SA', '🟣': 'OCE', 'playstation': 'PS', 'switch': 'Switch',
                         'windows': 'PC', 'xbox': 'Xbox'}
            regionList = ['🔴', '🟠', '🟡', '🟢', '🔵', '🟣']
            rankList = ['<:bronze1:816919331841638420>', '<:silver1:816919332026187796>', '<:gold1:816919332189372436>',
                        '<:platinum1:816919331740188703>', '<:diamond1:816919332012949524>',
                        '<:champion1:816919332147429407>',
                        '<:grandchamp1:816919332118200320>', '<:supersonic_legend:816919331585261579>']

            if reaction.emoji.name in reactDict.keys():
                role = discord.utils.get(guild.roles, name=reactDict[reaction.emoji.name])
                await member.add_roles(role, reason="React choice")

            elif reaction.emoji.name == "😍":
                role = discord.utils.get(guild.roles, name="ping")
                await member.add_roles(role, reason="React choice")

            else:
                channel = await client.fetch_channel(854012021094613042)
                message = await channel.fetch_message(reaction.message_id)
                await message.remove_reaction(reaction.emoji, member)

        if reaction.channel_id == 559389972797325364:
            with open("servertest.json", 'r') as sTest:
                servertest = (json.load(sTest))

            for key in servertest[str(reaction.guild_id)].keys():
                print(key)
                print(reaction.emoji)
                if key == str(reaction.emoji):
                    print(key)
                    channel = await client.fetch_channel(
                        int(servertest[str(reaction.guild_id)][str(reaction.emoji)]["Channel"]))
                    await channel.send(":slight_smile:")


@client.event
async def on_member_ban(guild, user):
    with open("servers_info.json", 'r') as sInfo:
        servers_info = (json.load(sInfo))

    if servers_info[str(guild.id)]['User Ban']['Status'] == "True":
        channel = client.get_channel(int(servers_info[str(guild.id)]['User Ban']['Channel']))
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="User banned", value=f"User: {user}")
        embed.set_footer(text=guild.name)
        await channel.send(embed=embed)
        return


@client.event
async def on_member_unban(guild, user):
    with open("servers_info.json", 'r') as sInfo:
        servers_info = (json.load(sInfo))

    if servers_info[str(guild.id)]['User Unban']['Status'] == "True":
        channel = client.get_channel(int(servers_info[str(guild.id)]['User Unban']['Channel']))
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name=f"User unbanned", value=f"User: {user}")
        embed.set_footer(text=guild.name)
        await channel.send(embed=embed)
        return


@client.event
async def on_invite_create(invite: discord.Invite):
    with open("servers_info.json", 'r') as sInfo:
        servers_info = (json.load(sInfo))

    if invite.max_age != 0:
        age = invite.max_age / 3600 / 24

    if servers_info[str(invite.guild.id)]['Invite Create']['Status'] == "True":
        channel = client.get_channel(int(servers_info[str(invite.guild.id)]['Invite Create']['Channel']))
        embed = discord.Embed(colour=discord.Colour.green(), title="Invite Created")
        embed.set_thumbnail(url="https://www.pngkey.com/png/full/29-298206_letter-png-letter.png")
        embed.add_field(name="Created by:", value=invite.inviter, inline=False)
        embed.add_field(name="Invite ID:", value=invite.id, inline=False)
        embed.add_field(name="Max uses:", value=invite.max_uses)
        embed.add_field(name="Expires in:", value=f"{round(age)} days", inline=False)
        if isinstance(invite.channel, discord.abc.GuildChannel):
            embed.add_field(name="Channel:", value=f"#{invite.channel.name}", inline=False)
        await channel.send(embed=embed)
        return


@client.event
async def on_invite_delete(invite):
    with open("servers_info.json", 'r') as sInfo:
        servers_info = (json.load(sInfo))

    if servers_info[str(invite.guild.id)]['Invite Delete']['Status'] == "True":
        channel = client.get_channel(int(servers_info[str(invite.guild.id)]['Invite Delete']['Channel']))
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Invite deleted", value=f"Invite: {invite.id}")
        embed.set_footer(text=invite.guild.name)
        await channel.send(embed=embed)
        return


@client.event
async def on_guild_channel_create(channel):
    with open("servers_info.json", 'r') as sInfo:
        servers_info = (json.load(sInfo))

    if servers_info[str(channel.guild.id)]['Channel Create']['Status'] == "True":
        sayChannel = client.get_channel(int(servers_info[str(channel.guild.id)]['Channel Create']['Channel']))
        embed = discord.Embed(colour=discord.Colour.green())
        embed.add_field(name="Channel created", value=f"Channel: {channel}")
        embed.set_footer(text=channel.guild.name)
        await sayChannel.send(embed=embed)
        return


@client.event
async def on_guild_channel_delete(channel):
    with open("servers_info.json", 'r') as sInfo:
        servers_info = (json.load(sInfo))

    if servers_info[str(channel.guild.id)]['Channel Delete']['Status'] == "True":
        sayChannel = client.get_channel(int(servers_info[str(channel.guild.id)]['Channel Delete']['Channel']))
        embed = discord.Embed(colour=discord.Colour.green())
        embed.add_field(name="Channel deleted", value=f"Channel: {channel}")
        embed.set_footer(text=channel.guild.name)
        await sayChannel.send(embed=embed)
        return


@client.event
async def on_guild_channel_update(before, after):
    if servers_info[str(before.guild.id)]['Channel Update']['Status'] == "True":
        embed = discord.Embed(colour=discord.Colour.dark_theme())
        embed.set_footer(text=before.guild.name)
        sayChannel = client.get_channel(int(servers_info[str(after.guild.id)]['Channel Update']['Channel']))

        # Check for role changes
        beforeRoles = []
        afterRoles = []
        beforeOverwrites = []
        afterOverwrites = []
        xi = 0
        if beforeRoles != afterRoles:
            for role in before.changed_roles:
                beforeRoles.append(role.name)

            for role in after.changed_roles:
                afterRoles.append(role.name)

            for role in beforeRoles:
                if not role in afterRoles:
                    embed.add_field(name=f"Role removed from {before.mention}", value=f"Role: {role.name}",
                                    inline=False)
                    xi = 1

            for role in afterRoles:
                if not role in beforeRoles:
                    embed.add_field(name=f"Role added to {after.mention}", value=f"Role: {role.name}", inline=False)
                    xi = 1

        # Check for name changes
        if before.name != after.name:
            embed.add_field(name=f"Changed name for #{before.name}", value=f"New channel name: {after.mention}",
                            inline=False)
            xi = 1

        # Check for permission overwrites
        if before.overwrites != after.overwrites:
            for key in after.overwrites.keys():
                afterOverwrites.append(key)

            for key in before.overwrites:
                beforeOverwrites.append(key)

            for oWrite in afterOverwrites:
                if not oWrite in beforeOverwrites:
                    embed.add_field(name=f"Role permissions added in {after.name}", value=f"Role: {oWrite}",
                                    inline=False)
                    xi = 1

            for oWrite in beforeOverwrites:
                if not oWrite in afterOverwrites:
                    embed.add_field(name=f"Role permissions removed in {before.name}", value=f"Role: {oWrite}",
                                    inline=False)
                    xi = 1

        if xi == 1:
            await sayChannel.send(embed=embed)

        return


@client.event
async def on_member_update(before, after):
    global wordblacklist2
    global nicknames
    with open("servers_info.json", 'r') as sInfo:
        servers_info = (json.load(sInfo))

    if before.guild.id == 788918979007348746:  # Change names - Bucko
        for word in wordblacklist2:
            if word in str(after.nick).lower():
                oldName = before.name
                nick = randint(0, len(nicknames))
                await after.edit(nick=nicknames[nick])
                channel = client.get_channel(788918979501883403)
                logChannel = client.get_channel(826598714092683285)
                await channel.send(
                    f"{after.mention} - Your name has been changed to something a little cuter. "
                    f"If you disagree with this, ask a mod to return it to its former glory."
                    f" :slight_smile:")
                await logChannel.send(f"> Changed {after.name}'s name to {nicknames[nick]}.")

    if servers_info[str(before.guild.id)]['User Update']['Status'] == "True":
        channel = client.get_channel(int(servers_info[str(before.guild.id)]['User Update']['Channel']))

        beforeRoles = []
        afterRoles = []

        for role in before.roles:
            beforeRoles.append(role)

        for role in after.roles:
            afterRoles.append(role)

        if before.nick == after.nick and len(beforeRoles) != len(afterRoles):
            if len(beforeRoles) > len(afterRoles):
                eventStr = f"Role removed from {before}"
                for role in beforeRoles:
                    if not role in afterRoles:
                        roleStr = f"❌ {role}"
                        rColor = discord.Colour.red()

            if len(beforeRoles) < len(afterRoles):
                eventStr = f"Role added to {before}"
                for role in afterRoles:
                    if not role in beforeRoles:
                        roleStr = f"✅ {role}"
                        rColor = discord.Colour.green()

            embed = discord.Embed(colour=rColor)
            embed.add_field(name=eventStr, value=roleStr, inline=False)
            embed.set_footer(text=before.guild.name)
            await channel.send(embed=embed)
            return

        if before.nick != after.nick:
            embed = discord.Embed(colour=discord.Colour.blue(), title=f"{before} changed nickname.")
            embed.add_field(name="Before:", value=f"`{before.nick}`", inline=False)
            embed.add_field(name="After:", value=f"`{after.nick}`", inline=False)
            embed.set_footer(text=before.guild.name)
            await channel.send(embed=embed)
            return


@client.event
async def on_message_delete(message: discord.Message):
    with open("servers_info.json", 'r') as sInfo:
        servers_info = (json.load(sInfo))

    if not message.author.bot:
        if servers_info[str(message.guild.id)]['Message Delete']['Status'] == "True":
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_thumbnail(url="https://image.flaticon.com/icons/png/512/807/807837.png")
            embed.add_field(name=f"{message.author.name}'s message in #{message.channel} was deleted.",
                            value=f"`{message.content}`", inline=False)
            embed.set_footer(text=message.guild.name)
            channel = client.get_channel(int(servers_info[str(message.guild.id)]['Message Delete']['Channel']))
            await channel.send(embed=embed)


@client.event
async def on_message_edit(before, after):
    with open("servers_info.json", 'r') as sInfo:
        servers_info = (json.load(sInfo))

    if not before.author.bot and abs(len(before.content) - len(after.content)) > 3:
        if servers_info[str(before.guild.id)]['Message Edit']['Status'] == "True":
            channel = await client.fetch_channel(int(servers_info[str(before.guild.id)]['Message Edit']['Channel']))
            embed = discord.Embed(colour=discord.Colour.red(),
                                  title=f"{before.author.name} edited a message in #{before.channel.name}")
            embed.set_thumbnail(
                url="https://icons.iconarchive.com/icons/custom-icon-design/flatastic-1/512/edit-icon.png")
            embed.add_field(name="Before edit:", value=f"`{before.content}`", inline=False)
            embed.add_field(name="After edit:", value=f"`{after.content}`", inline=False)
            embed.set_footer(text=f"{before.guild.name}")
            await channel.send(embed=embed)


@client.event
async def on_raw_reaction_remove(reaction):
    guild = client.get_guild(reaction.guild_id)
    member = guild.get_member(reaction.user_id)

    if reaction.channel_id == 822933311231361034:  # Daevy's role channel
        reactDict = {'🟡': 'EU', '🟢': 'NA',
                     '🔴': 'AF', '🟠': 'AS',
                     '🔵': 'SA', '🟣': 'OCE',
                     'playstation': 'PS', 'switch': 'Switch',
                     'windows': 'PC', 'xbox': 'Xbox'}

        if reaction.emoji.name in reactDict.keys():
            role = discord.utils.get(guild.roles, name=reactDict[reaction.emoji.name])
            await member.remove_roles(role, reason="React choice")

    if reaction.channel_id == 854012021094613042:
        reactDict = {'bronze1': "Bronze", "silver1": "Silver",
                     "gold1": "Gold", "platinum1": "Platinum", "diamond1": "Diamond", "champion1": "Champion",
                     "grandchamp1": "Grand Champion", "supersonic_legend": "Supersonic Legend", '🟡': 'EU', '🟢': 'NA',
                     '🔴': 'AF', '🟠': 'AS', '🔵': 'SA', '🟣': 'OCE', 'playstation': 'PS', 'switch': 'Switch',
                     'windows': 'PC', 'xbox': 'Xbox'}

        if reaction.emoji.name in reactDict.keys():
            role = discord.utils.get(guild.roles, name=reactDict[reaction.emoji.name])
            await member.remove_roles(role, reason="Reach choice")

    if reaction.channel_id == 837858737057300531:
        if reaction.emoji.name == "😍":
            role = discord.utils.get(guild.roles, name="ping")
            await member.remove_roles(role, reason="React choice")

    if reaction.channel_id == 854012021094613042:  # Bucko
        reactDict = {'bronze1': "Bronze", "silver1": "Silver",
                     "gold1": "Gold", "platinum1": "Platinum", "diamond1": "Diamond", "champion1": "Champion",
                     "grandchamp1": "Grand Champion", "supersonic_legend": "Supersonic Legend", '🟡': 'EU',
                     '🟢': 'NA',
                     '🔴': 'AF', '🟠': 'AS', '🔵': 'SA', '🟣': 'OCE', 'playstation': 'PS', 'switch': 'Switch',
                     'windows': 'PC', 'xbox': 'Xbox'}
        regionList = ['🔴', '🟠', '🟡', '🟢', '🔵', '🟣']
        rankList = ['<:bronze1:816919331841638420>', '<:silver1:816919332026187796>', '<:gold1:816919332189372436>',
                    '<:platinum1:816919331740188703>', '<:diamond1:816919332012949524>',
                    '<:champion1:816919332147429407>',
                    '<:grandchamp1:816919332118200320>', '<:supersonic_legend:816919331585261579>']

        if reaction.emoji.name in reactDict.keys():
            role = discord.utils.get(guild.roles, name=reactDict[reaction.emoji.name])
            await member.remove_roles(role, reason="React choice")

        elif reaction.emoji.name == "😍":
            role = discord.utils.get(guild.roles, name="ping")
            await member.remove_roles(role, reason="React choice")

        else:
            channel = await client.fetch_channel(854012021094613042)
            message = await channel.fetch_message(reaction.message_id)
            await message.remove_reaction(reaction.emoji, member)


@client.event
async def on_guild_join(guild):
    i = 0
    for guilds in client.guilds:
        i += 1
    print(f"NugBot joined {guilds}! Now in {i} guilds.\n")

    with open("user_info.json", 'r') as uf:
        userdict = (json.load(uf))
    i = 0
    if not str(guild.id) in userdict.keys():
        userdict[str(guild.id)] = {}
        for member in guild.members:
            userdict[str(guild.id)].update({
                member.id: {
                    "Name": member.name,
                    "Money": 0,
                    "rlconsole": "",
                    "rlid": "",
                    "epicID": "",
                    "steamID": "",
                    "console": "",
                    "riotID": ""
                }})
            i += 1
        with open("user_info.json", "w") as uf:
            json.dump(userdict, uf, indent=4)
        print(f"Added {i} users.")


@client.event
async def on_guild_remove(guild):
    i = 0
    for guilds in client.guilds:
        i += 1
    print(f"NugBot was removed from {guild}! Now in {i} guilds.\n")


client.run(TOKEN, bot=True, reconnect=True)
