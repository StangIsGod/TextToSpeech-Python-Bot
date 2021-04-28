import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
from submodules.VoiceText import vt_func
import time
import asyncio
import re
import os
import json
import sys

###############DIRECTORY################
SettingDir = "./Setting"
DicDir = "./dictionary"

###############SETTINGS#################
description = "Bot"
prefix = '#'
voiceapikey = ""
dicordtoken = ""

ys = {}
################DISCORD#################
intents = discord.Intents().default()
intents.members = True
client = discord.Client()
voiceClient = None


voice = {} 
channel = {} 
##############VOICETEXTAPI##############
speker = ['show', 'haruka', 'hikari', 'takeru', 'santa', 'bear']
emotion = 'happiness'
emotionlevel = 4
pitch = 100
speed = 120
volume = 100
########################################

ldedPrefix = {}

def get_prefix(client, ctx):
    dir = f"./Setting/{ctx.guild.id}.json"
    if os.path.isfile(dir):
        global ldedPrefix
        with open(dir, "r") as f:
            s = f.read()
            if len(s) != 0:
                wL = json.loads(s)
                if "prefix" in wL:
                    ldedPrefix[ctx.guild.id] = wL["prefix"]

                    return wL["prefix"]
                else:
                    return "$"
            else:
                return "$"

bot = commands.Bot(description=description, command_prefix=get_prefix, intents=intents, help_command=None)
bot.remove_command("help")

@bot.listen('on_message')
async def on_message(message):
    if message.author.bot:
        return

    global voice
    global channel
    global ldedPrefix

    mess_id = message.author.id
    guild_id = message.guild.id # サーバID

    if message.content.startswith(ldedPrefix[guild_id]):
        return
        
    if guild_id not in channel:
        return

    if message.channel.id == channel[guild_id]:
        dir = f"./Setting/{guild_id}.json"
        if os.path.isfile(dir):
            f = open(dir, 'r')
            s = f.read()

            if len(s) == 0:
                vlm = volume
            else:
                ar = json.loads(s)
                if not "volume" in ar:
                    vlm = "75"
                else:
                    vlm = ar["volume"]


        get_msg = re.sub(r'http(s)?://([\w-]+\.)+[\w-]+(/[-\w ./?%&=]*)?', 'URL', message.content)

        get_msg = get_msg.replace('<:', '')
        get_msg = re.sub(r':[0-9]*>', '', get_msg)

        guild_id = message.guild.id
        wA = {}
        dir = f"{DicDir}/{guild_id}.json"
        if os.path.isfile(dir):
            f = open(dir, "r")
            s = f.read()

            if len(s) != 0:
                wA = json.loads(s)
            f.close()

        for oldStr in wA.keys():
            get_msg = get_msg.replace(oldStr, wA[oldStr])

        print(get_msg)

        tmpfile = vt_func.to_wave(get_msg, 'hikari', emotion, emotionlevel, pitch, speed, vlm, guild_id, voicetextAPI)

        while (voice[guild_id].is_playing()):
            await asyncio.sleep(1)

        voice_mess = f'./{tmpfile}'
        voice[guild_id].play(discord.FFmpegPCMAudio(voice_mess))

        while (voice[guild_id].is_playing()):
            await asyncio.sleep(1)

        os.remove(voice_mess) 

@bot.listen('on_ready')
async def on_ready():
    print(f'ログインに成功したよ！ [{bot.user}]')
    await bot.change_presence(activity=discord.Game(f'{len(voice)}サーバーが使用中 (Max:50)'))
    async for guild in bot.fetch_guilds(limit=150):
        dir = f"./Setting/{guild.id}.json"
        if os.path.isfile(dir) == False:
            f = open(dir, 'x', encoding='UTF-8')
            l = {"prefix" : prefix, "role" : "", "volume" : "75"}
            f.write(json.dumps(l, sort_keys=True, indent=4))
            f.close()

@bot.listen('on_guild_join')
async def on_guild_join(guild: discord.Guild):
    print(f"{guild.name} に参加しました！")
    dir = f"./Setting/{guild.id}.json"
    if os.path.isfile(dir) == False:
        f = open(dir, 'x', encoding='UTF-8')
        l = {"prefix" : prefix, "role" : ""}
        f.write(json.dumps(l, sort_keys=True, indent=4))
        f.close()

@bot.listen('on_guild_remove')
async def on_guild_remove(guild: discord.Guild):
    print(f"{guild.name} から削除されました。")
    dir = f"./Setting/{guild.id}.json"
    if os.path.isfile(dir) == True:
        os.remove(dir)
        print('設定ファイルを削除しました。')

@bot.command()
async def testing(ctx, msg):
    await ctx.send(msg)

@bot.event
async def on_voice_state_update(member,before,after):
    global voice
    global channel

    isMe = (member.id is bot.user.id) and (before.channel is not None)
    #print(f"before's channel is {}")
    #print(f"after's channel is {after.channel is None}")
    #print(f"{isMe} : {before.channel.id} : {after.channel.id}")

    guild_id = member.guild.id

    if not isMe and member.bot:
        return

    if isMe:
        if guild_id in voice:
            del voice[guild_id]

        if guild_id in channel:
            del channel[guild_id]
        return

    if guild_id not in channel:
        return

    if not type(before.channel) == discord.channel.VoiceChannel:
        return

    while (voice[guild_id].is_playing()):
        await asyncio.sleep(1)

    if len(before.channel.members) == 1:
        # コマンドが、呼び出したチャンネルで叩かれている場合
        await voice[guild_id].disconnect() # ボイスチャンネル切断
        # 情報を削除
        del voice[guild_id] 
        del channel[guild_id]

    await bot.change_presence(activity=discord.Game(f'{len(voice)}サーバーが使用中 (Max:50)'))

@bot.command(pass_context = True, aliases=["connect","summon"])
async def join(ctx):
    try:
        global voice
        global channel
        author = ctx.message.author

        vo_ch = author.voice.channel
        guild = ctx.message.guild

        if not len(voice) >= 50:
            await ctx.send("おじゃまするで！")
            voice[guild.id] = await vo_ch.connect()
            channel[guild.id] = ctx.channel.id         
        else:
            await ctx.send("今現在回線が混み合ってるから、時間を置いてから追加してな！")
    except Exception as ex:
        print(ex)

@bot.command(pass_context = True)
async def help(ctx):
    embed = discord.Embed(title="AkemiChan", description="Thanks for Using Akemichan!", color=0x4b0082)
    embed.set_author(name="Created by STNG", url="https://twitter.com/stngsan", icon_url="https://i.imgur.com/fVONXji.png")
    embed.set_thumbnail(url="https://i.imgur.com/SzmD9Hy.png")
    embed.add_field(name="join", value="vcに参加するで！使うときは自分もvcに入ってな！", inline=True)
    embed.add_field(name="bye", value="参加したvcから抜けるで！", inline=False)
    embed.add_field(name="add [単語] [読み方]", value="[単語]を[読み方]で読むように覚えるで！", inline=False)
    embed.add_field(name="delete [単語]", value="覚えた読み方で読むのをやめるで！", inline=False)
    embed.set_footer(text="バグ等の報告はDiscord(stng#4545)までお願いします。")
    await ctx.send(embed=embed)

@bot.command(pass_context = True, aliases=["dc","disconnect","kill", "Bye"])
async def bye(ctx):
    try:
        global guild_id
        global voice
        global channel
        guild_id = ctx.guild.id

        if guild_id not in voice or guild_id not in channel:
            return

        # コマンドが、呼び出したチャンネルで叩かれている場合
        if ctx.channel.id == channel[guild_id]:
            

            await ctx.channel.send('じゃあの')
            await voice[guild_id].disconnect() # ボイスチャンネル切断
            # 情報を削除
            del voice[guild_id] 
            del channel[guild_id]

            await bot.change_presence(activity=discord.Game(f'{len(voice)}サーバーが使用中 (Max:50)'))
    except Exception as ex:
        print(f"An error has occurred in {ctx.guild.name}(ID:{ctx.guild.id})")

@bot.command()
async def add(ctx, arg1, arg2):
    guild_id = ctx.guild.id
    wA = {}
    dir = f"{DicDir}/{guild_id}.json"
    if not os.path.isfile(dir):
        f = open(dir, "w+")
    else:
        f = open(dir, "r")
    
    s = f.read()
    
    if len(s) != 0:
        wA = json.loads(s)

    f.close()
    f = open(dir, "w")
    if len(arg1) != 0 and len(arg2) != 0:
        wA[arg1] = arg2
        f.write(json.dumps(wA, sort_keys=True, indent=4))
        f.close()
        await ctx.send(f"{arg1} を {arg2} って読むで！")

@bot.command()
async def delete(ctx, arg1):
    guild_id = ctx.guild.id
    wA = {}
    dir = f"{DicDir}/{guild_id}.json"
    if os.path.isfile(dir):
        f = open(dir, "r")
        s = f.read()

        if len(s) != 0:
            wA = json.loads(s)
            f.close()
            f = open(dir, "w")
            if len(wA[arg1]) != 0:
                forgetStr = f"{arg1} を {wA[arg1]} って読むのやめるで！"
                del wA[arg1]
                f.write(json.dumps(wA, sort_keys=True, indent=4))
                f.close()
                await ctx.send(f"{forgetStr}")
            else:
                await ctx.send("登録されてへんで！")
    else:
        await ctx.send("なんも覚えてないで！")

@bot.command()
async def check_dictional(ctx, arg1):
    guild_id = ctx.guild.id
    wA = {}
    dir = f"{DicDir}/{guild_id}.json"
    if os.path.isfile(dir):
        f = open(dir, "r")
        s = f.read()

        if len(s) != 0:
            wA = json.loads(s)

            if arg1 in wA:
                await ctx.send(f"[{wA[arg1]}] って読んでるで！")
            else:
                await ctx.send("登録されてへんで！")


@bot.command()
async def setting(ctx, *args):
    dir = f"./Setting/{ctx.guild.id}.json"
    if os.path.isfile(dir):
        f = open(dir, 'r')
        s = f.read()

        if len(s) == 0:
             wL = {'prefix': prefix, 'role': '', 'volume' : '70'}
        else:
             wL = json.loads(s)
    f.close()
    f = open(dir, 'w')

    if args[0] == 'prefix':
        wL['prefix'] = args[1]
        f.write(json.dumps(wL, sort_keys=True, indent=4))
        f.close()
        await ctx.send(f"コマンド用の文字を[{args[1]}]に設定したで！")
    if args[0] == 'volume':
        wL['volume'] = args[1]
        f.write(json.dumps(wL, sort_keys=True, indent=4))
        f.close()
        await ctx.send(f"音量を[{args[1]}]に設定したで！")
########################################################################################################

loaded_list = {}

if (os.path.isfile("./Setting.json")) == False:
    f = open('./Setting.json', 'x', encoding='UTF-8')
    l = {"token" : "", "prefix" : "$", "voicetextAPI" : "", "volume" : 80}
    f.write(json.dumps(l, sort_keys=True, indent=4))
    f.close()
    print("設定ファイルを生成しました。\n設定を全て正しく記入した後に再起動してください。")
    sys.exit()
else:
    f = open('./Setting.json', 'r', encoding='UTF-8')
    r = f.read()
    #print(f"読み込んだ文字: \n{r}")
    loaded_list = json.loads(r)
    f.close()
    #print(loaded_list)

prefix = loaded_list["prefix"]
discordtoken = loaded_list["token"]
voicetextAPI = loaded_list["voicetextAPI"]
if not len(loaded_list["volume"]) == 0:
    volume = loaded_list["volume"]

prefix_is_null = len(prefix) == 0
token_is_null = len(discordtoken) == 0
apikey_is_null = len(voicetextAPI) == 0

if (prefix_is_null) or (token_is_null) or (apikey_is_null):
    print(("prefixが空欄です。\n" if prefix_is_null else "") +
          ("tokenが空欄です。\n" if token_is_null else "") + 
          ("voicetextAPIが空欄です。\n" if apikey_is_null else "") +
          ("\nアプリケーションを終了します。"))
    sys.exit()
else:
    bot.run(discordtoken)

