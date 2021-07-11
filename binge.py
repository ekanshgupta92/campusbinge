import discord
from discord import role
# from discord.ext import commands
from discord.ext.commands.core import has_any_role, has_role
import pymongo
from pymongo import MongoClient

intents = discord.Intents(messages=True, guilds=True)
intents.members = True  # Subscribe to the privileged members intent.

cluster = MongoClient("mongodb+srv://test:eg123456@cluster0.5ajlh.mongodb.net/test")
db = cluster["discord_test"]
collection = db["test"]

token = open("token.txt", "r").read()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message): 
    
    if message.mentions != []:
        myquery = { "_id": (message.mentions)[0].id }
        candidate = (message.mentions)[0]
    else : 
        myquery = { "_id": message.author.id }
        candidate = message.author
    
    # Debugging cmds 
    # print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
    # print(f"{message.raw_role_mentions}")
    # print(f"{(message.mentions)[0].id}")
    # print(f"{(((message.mentions)[0].roles)[0]).id}")
    # print(f"{message.author.id}")
    # print(f"{candidate}")
    # print(f"{candidate.id}")

    if message.content.startswith('$add help') or message.content == "$add" :
        em = discord.Embed(title = "Help", description = "Use: $add @<user> tokens <points>", color=message.author.color)
        await message.reply(embed=em)

    if message.content.startswith('$balance help'):
        em = discord.Embed(title = "Help", description = "Use: $balance @<user> or just $balance to get your own balance", color=message.author.color)
        await message.reply(embed=em)

    if message.content.startswith('$rich'):
        embed = discord.Embed(title= "Top scorers on server", description = "")
        for dic in collection.find().sort("score", pymongo.DESCENDING).limit(5):
            embed.add_field(name= f"{message.guild.get_member(dic['_id'])}  -->  {dic['score']}", value='\u200b', inline=False)
        await message.channel.send(embed = embed)
    
    if (collection.count_documents(myquery) == 0):
        if message.author == client.user:
            return

        if message.content.startswith('$add') & ('tokens' in message.content) & (message.mentions!= []):
            tokens = int(message.content.split()[3])
            post = {"_id": candidate.id, "score": tokens}
            collection.insert_one(post)
            await message.channel.send(f"Succesfully added {tokens} tokens to {candidate}'s account")

        if message.content.startswith('$balance'):
            # post = {"_id": candidate.id, "score": 0}
            await message.reply(f"Yet to open account 🙂")

    else:
        if message.author == client.user:
            return

        if message.content.startswith('$add') & ('tokens' in message.content) & (message.mentions!= []):
            tokens = int(message.content.split()[3])
            query = {"_id": candidate.id}
            user = collection.find(query)
            for result in user:
                score = result["score"]
            score = score + tokens
            collection.update_one({"_id": candidate.id}, {"$set":{"score":score}})
            await message.channel.send(f"Succesfully added {tokens} tokens to {candidate}'s account")

        if message.content.startswith('$balance'):
            query = {"_id": candidate.id}
            user = collection.find(query)
            for result in user:
                score = result["score"]
            await message.reply(f"{candidate} has {score} points. ")

client.run(token)