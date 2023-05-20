# This script requires the 'members' privileged intents to get the list of users on a guild 

import discord
from discord.ext import commands
import discord
import os
import pymongo
from pymongo import MongoClient
from pymongo import message

description = '''Custom score based bot for CampusBinge'''

intents = discord.Intents.default()
intents.members = True

token = open("token.txt", "r").read()
bot = commands.Bot(command_prefix='$', description=description, intents=intents)
uri = os.environ['MONGODB_URI']
cluster = MongoClient(uri)
db = cluster["discord_test"]
collection = db["test"]

roles = ['Boss', 'Team Leaders and coordinators', 'Deaprtment Heads']

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(pass_context=True)
@commands.has_any_role(*roles)
async def add(ctx, candidate: discord.Member, key: str , tokens: int):
    if key.lower() != "tokens" :
        await ctx.channel.send("Use the correct format. Use $add_help for more info")
        return
    if ctx.message.mentions != []:
        myquery = { "_id": (ctx.message.mentions)[0].id }
        candidate = (ctx.message.mentions)[0]
    else : 
        await ctx.channel.send("Use the correct format. Use $add_help for more info")
        return
    role = ''
    if (collection.count_documents(myquery) == 0):
        rolelist = [i.name for i in candidate.roles]
        for i in rolelist:
            if i == '@everyone' or i =='Binge Tribe' or i == 'Department Heads' or i == 'Custodian' or i == 'Boss':
                pass
            else: 
                role = i
                break
        if role =='':
            await ctx.channel.send('Assign a role first to this member')
            return
        tier = ''
        if tokens <= 8000:
            tier = 'Rookie'
        elif tokens <= 30000:
            tier = 'Challenger'
        elif tokens <= 80000:
            tier = 'Champion'
        elif tokens <= 200000:
            tier = 'Master'
        elif tokens <= 500000:
            tier = 'Ace'
        else: tier = 'Conquerer'

        post = {"_id": candidate.id, "score": tokens , "role": role, "tier": tier}
        collection.insert_one(post)
        await ctx.channel.send(f"Succesfully added {tokens} tokens to {candidate}'s account")
    
    else:
        query = {"_id": candidate.id}
        user = collection.find(query)
        for result in user:
            score = result["score"]
        score = score + tokens 
        tier = ''
        if score <= 8000:
            tier = 'Rookie'
        elif score <= 30000:
            tier = 'Challenger'
        elif score <= 80000:
            tier = 'Champion'
        elif score <= 200000:
            tier = 'Master'
        elif score <= 500000:
            tier = 'Ace'
        else: tier = 'Conquerer'
        collection.update_one({"_id": candidate.id}, {"$set":{"score":score}})
        collection.update_one({"_id": candidate.id}, {"$set":{"tier":tier}})
        await ctx.channel.send(f"Succesfully added {tokens} tokens to {candidate}'s account")
    
@bot.command()
async def add_help(ctx):
    em = discord.Embed(title = "Help", description = "Use: $add @<user> tokens <points>", color=ctx.author.color)
    await ctx.reply(embed=em)

@bot.command()
async def balance_help(ctx):
    em = discord.Embed(title = "Help", description = "Use: $balance @<user> or just $balance to get your own balance", color=ctx.author.color)
    await ctx.reply(embed=em)

@bot.command()
async def balance(ctx, candidate: discord.Member = None): 
    if ctx.message.mentions != []:
        myquery = { "_id": (ctx.message.mentions)[0].id }
        candidate = (ctx.message.mentions)[0]
    else : 
        myquery = { "_id": ctx.author.id }
        candidate = ctx.message.author
        
    if (collection.count_documents(myquery) == 0):
        await ctx.reply(f"Yet to open account kid 🙂")
    else:
        query = {"_id": candidate.id}
        user = collection.find(query)
        for result in user:
            score = result["score"]
            tier = result["tier"]
        await ctx.reply(f"{candidate} has {score} points. You are at {tier} tier currently")

@bot.command()
async def rich(ctx):
    embed = discord.Embed(title= "Top scorers according to your role are:", description = "")
    candidate = ctx.message.author
    rolelist = [i.name for i in candidate.roles]
    for i in rolelist:
        if i == '@everyone' or i =='Binge Tribe' or i == 'Department Heads' or i == 'Custodian' or i == 'Boss':
            pass
        else: 
            role = i
            break
    # collection.inventory.find({"role": role})
    for dic in collection.find({"role": role}).sort("score", pymongo.DESCENDING).limit(20):
        embed.add_field(name= f"{ctx.guild.get_member(dic['_id'])}  -->  {dic['score']}", value='\u200b', inline=False)
    await ctx.channel.send(embed = embed)

@bot.command()
async def rich_all(ctx):
    embed = discord.Embed(title= "Top scorers on server are:", description = "")
    for dic in collection.find().sort("score", pymongo.DESCENDING).limit(20):
        embed.add_field(name= f"{message.guild.get_member(dic['_id'])}  -->  {dic['score']}", value='\u200b', inline=False)
    await message.channel.send(embed = embed)
bot.run(token)
