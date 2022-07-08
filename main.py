import os
import random
import json
import re
import threading
import matplotlib.pyplot as plt
import discord
from discord.ext import tasks

client = discord.Client()
companyNames = ["ArkCentral", "CountingStock: Global Operations", "MineufacturingGroup", "CraftClass",
                "ValiantCorp", "TerraTeam", "RunescrapIncorporated", "BTDefence", "FortressTeam",
                "RustingCo", "Stardew Real Estate", "DBDCremations", "RimTrading"]
print(os.listdir("."))
if "companies.json" not in os.listdir("."):
    print("Creating companies...")
    with open("companies.json", "x") as f:
        companiesTemplate = {"ArkCentral": random.randint(40, 160),
                             "CountingStock: Global Operations": random.randint(40, 160),
                             "MineufacturingGroup": random.randint(40, 160),
                             "CraftClass": random.randint(40, 160),
                             "ValiantCorp": random.randint(40, 160), "TerraTeam": random.randint(40, 160),
                             "RunescrapIncorporated": random.randint(40, 160), "BTDefence": random.randint(40, 160),
                             "FortressTeam": random.randint(40, 160),
                             "RustingCo": random.randint(40, 160), "Stardew Real Estate": random.randint(40, 160),
                             "DBDCremations": random.randint(40, 160), "RimTrading": random.randint(40, 160)}
        json.dump(companiesTemplate, f, ensure_ascii=False, indent=4)

if "users.json" not in os.listdir("."):
    print("Creating users...")
    with open("users.json", "x") as f:
        usersTemplate = {}
        json.dump(usersTemplate, f, ensure_ascii=False, indent=4)
if "userStocks.json" not in os.listdir("."):
    print("Creating user stock...")
    with open("userStocks.json", "x") as f:
        userStocksTemplate = {}
        json.dump(userStocksTemplate, f, ensure_ascii=False, indent=4)
userStockInventoryTemplate = {"ArkCentral": 0,
                              "CountingStock: Global Operations": 0,
                              "MineufacturingGroup": 0,
                              "CraftClass": 0,
                              "ValiantCorp": 0, "TerraTeam": 0,
                              "RunescrapIncorporated": 0, "BTDefence": 0,
                              "FortressTeam": 0,
                              "RustingCo": 0, "Stardew Real Estate": 0,
                              "DBDCremations": 0, "RimTrading": 0}

with open('companies.json') as companiesjson:
    companies = json.load(companiesjson)
with open('users.json') as usersjson:
    users = json.load(usersjson)
with open('userStocks.json') as userstocksjson:
    userStocks = json.load(userstocksjson)

priceMod = lambda currentPrice: currentPrice * (random.randint(80, 120) / 100)
priceModLow = lambda currentPrice: currentPrice * (random.randint(10, 400) / 100)
priceModHigh = lambda currentPrice: currentPrice * (random.randint(50, 110) / 100)

changed = False
crashed_stock = ""


def ModifyPrices():
    global changed
    global crashed_stock
    changed = True
    print('Changed')
    threading.Timer(1200, ModifyPrices).start()
    for i in companyNames:
        value = companies.get(i)
        newValue = priceMod(value)
        if newValue < 10:
            newValue = 10
        if newValue < 30:
            newValue = priceModLow(newValue)
        if newValue > 200:
            newValue = priceModHigh(newValue)
        updateDict = {i: int(newValue)}
        companies.update(updateDict)


ModifyPrices()


@tasks.loop(seconds=5, count=None)
async def updateCheck():
    global changed
    for guild in client.guilds:
        for channel in guild.channels:
            print(channel.name)
            if channel.name == 'stocks':
                stocks = channel
                if changed:
                    await stocks.send('Prices Updated!')
                    changed = False


updateCheck.start()


@tasks.loop(seconds=5, count=None)
async def CrashCheck():
    global crashed
    global crashed_stock
    crashedCorps = []
    for i in companies:
        if companies[i] < 15:
            crashedCorps.append(i)
            for guild in client.guilds:
                for channel in guild.channels:
                    if channel.name == 'stocks':
                        stocks = channel
                        await stocks.send(i + ' has crashed hardcore! You will lose all of your stock holding for it. '
                                              'No refunds!')
    for i in crashedCorps:
        updateDict = {i: 50}
        companies.update(updateDict)
        with open("companies.json", "w") as companiesUpdate:
            json.dump(companies, companiesUpdate, ensure_ascii=False, indent=4)
        for j in userStocks.keys():
            print(j)
            print(i)
            userStocks[str(j)][str(i)] = 0
            with open("userStocks.json", "w") as userStocksUpdate:
                json.dump(userStocks, userStocksUpdate, ensure_ascii=False, indent=4)


CrashCheck.start()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$bal'):
        await message.channel.send("Current Balance: " + str(users.get(str(message.author.id))))

    if message.content.startswith('$register'):
        await message.channel.send('Registering')
        if str(message.author.id) in users:
            await message.channel.send("User already exists")
        else:
            users[str(message.author.id)] = 500
            with open("users.json", "w") as file:
                json.dump(users, file, ensure_ascii=False, indent=4)

        if str(message.author.id) in userStocks:
            await message.channel.send("User stocks already exists")
        else:
            userStocks[str(message.author.id)] = userStockInventoryTemplate
            with open("userStocks.json", "w") as file:
                json.dump(userStocks, file, ensure_ascii=False, indent=4)
        await message.channel.send("Complete!")

    if message.content.startswith('$buystock'):
        messageWorking = message.content
        stripped = messageWorking.strip("$buystock ")
        amount = re.sub(r'[^\d]', "", stripped)
        stock = re.sub(r'\s*\d+\s*', "", stripped)
        cost = companies.get(stock)
        if stock in companyNames:
            totalCost = int(cost) * int(amount)
            if int(users.get(str(message.author.id))) >= totalCost and int(amount) > 0:
                await message.channel.send("Purchasing stock...")
                currentAmt = userStocks[str(message.author.id)].get(stock)
                currentAmt = int(currentAmt) + int(amount)
                userStocks[str(message.author.id)][str(stock)] = currentAmt
                with open('userStocks.json', 'w') as userstocksjsonupdate:
                    json.dump(userStocks, userstocksjsonupdate, ensure_ascii=False, indent=4)
                newBal = int(users.get(str(message.author.id))) - totalCost
                users[str(message.author.id)] = newBal
                with open("users.json", "w") as usersjsonupdate:
                    json.dump(users, usersjsonupdate, ensure_ascii=False, indent=4)
                await message.channel.send("Complete!")
        else:
            await message.channel.send("What? The fuck? you dob. cunt. Don't fuck with me.")

    if message.content.startswith('$sellstock'):
        messageWorking = message.content
        stripped = messageWorking.strip("$sellstock ")
        amount = re.sub(r'[^\d]', "", stripped)
        stock = re.sub(r'\s*\d+\s*', "", stripped)
        cost = companies.get(stock)
        if stock in userStocks[str(message.author.id)]:
            if int(userStocks[str(message.author.id)][stock]) >= int(amount):
                await message.channel.send("Selling stock...")
                userBal = int(users.get(str(message.author.id)))
                userBal = userBal + int(cost) * int(amount)
                users[str(message.author.id)] = userBal
                with open("users.json", "w") as usersjsonupdate:
                    json.dump(users, usersjsonupdate, ensure_ascii=False, indent=4)
                userStocks[str(message.author.id)][stock] = userStocks[str(message.author.id)][stock] - int(amount)
                with open('userStocks.json', 'w') as userstocksjsonupdate:
                    json.dump(userStocks, userstocksjsonupdate, ensure_ascii=False, indent=4)
                await message.channel.send("Complete!")
            else:
                await message.channel.send("Invalid! Check your stats.")
        else:
            await message.channel.send("What? The fuck? you dob. cunt. Don't fuck with me.")

    if message.content.startswith('$stocklist'):
        names = list(companies.keys())
        values = list(companies.values())
        graph = plt.bar(range(len(companies)), values, tick_label=names)
        plt.bar_label(graph, values)
        plt.gcf().autofmt_xdate()
        plt.tick_params(axis='x', labelsize=6)
        plt.title('Current Stock Prices')
        plt.ylabel("CumCoin Cost", style='italic')
        plt.savefig('currentPrices.png')
        plt.clf()
        await message.channel.send(file=discord.File('currentPrices.png'))

    if message.content.startswith('$stockbal'):
        target = {39: None, 123: None, 125: None}
        msg = str(userStocks.get(str(message.author.id))).translate(target)
        print(str(userStocks.get(str(message.author.id))))
        print(msg)
        await message.channel.send(msg)


# TODO - ADD BANKRUPCY OPTION, AND CREATE A COUNTER FOR EACH RUN PER PERSON. IF STOCK HITS PRICEMOD LOW x 3 IN 10 ROTATIONS, DELETE STOCK FROM EVERYONES STORAGE AND POST A NOTIF

client.run('')
