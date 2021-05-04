import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
from submodules.VoiceText import vt_func
from pykakasi import kakasi
import logging
import time
import asyncio
import re
import os
import json
import sys
from datetime import datetime, timedelta
import requests
import pyvcroid2
import threading

#py -3.9-32 main.py

###############DIRECTORY################
SettingDir = "./Setting"
DicDir = "./dictionary"

###############SETTINGS#################
description = "Bot"
prefix = '#'
voiceapikey = ""
dicordtoken = ""
defaultvoicetype = "akane_west"

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
loaded_list = {}
dictionaries = {"ai" : "ai_44",
                "akane_west" : "akane_west_emo_44",
                "aoi" : "aoi_emo_44",
                "kiritan" : "kiritan_44",
                "kou" : "kou_44",
                "seika" : "seika_44",
                "shouta" : "shouta_44",
                "tamiyasu" : "tamiyasu_44",
                "tsuina" : "tsuina_44",
                "tsuina_west" : "tsuina_west_44",
                "yoshidakun" : "yoshidakun_44",
                "yukari" : "yukari_44",
                "zunko" : "zunko_44",
                "yukari_emo" : "yukari_emo_44"}


if (os.path.isfile("./Setting.json")) == False:
    f = open('./Setting.json', 'x', encoding='UTF-8')
    l = {"token" : "", "prefix" : "$", "voicetextAPI" : "", "voiceroidAPI" : "", "volume" : 80}
    loaded_list = l
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

def get_prefix(client, ctx):
    if len(loaded_list["prefix"]) == 0:
        loaded_list["prefix"] = prefix

    if ctx.guild is None:
        return loaded_list["prefix"]

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
                    return loaded_list["prefix"]
            else:
                return loaded_list["prefix"]

bot = commands.Bot(description=description, command_prefix=get_prefix, intents=intents, help_command=None)
bot.remove_command("help")

def say_Exception(e):
    print('=== エラー内容 ===')
    print('type:' + str(type(e)))
    print('args:' + str(e.args))
    print('message:' + e.message)
    print('e_main:' + str(e))
    print('=======================')

async def Logger_Loop():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

@bot.check #bool型
async def globally_block_dms(ctx):
    return ctx.guild is not None

async def get_guild_prefix(guildid):
    global loaded_list
    global ldedPrefix

    if ldedPrefix[guildid] is None:
        pfx = loaded_list["prefix"]
    else:
        pfx = ldedPrefix[guildid]

@bot.listen('on_message')
async def on_message(message):
    if message.author.bot:
        return

    if message.guild is None:
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

    if message.channel is None:
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

                if not "voicetype" in ar:
                    l_vt = defaultvoicetype
                else:
                    l_vt = ar["voicetype"]

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

        #print(get_msg)

        kks = kakasi()
        kks.setMode('J', 'H')
        conv = kks.getConverter()
        get_msg_converted = conv.do(get_msg)

        #tmpfile = vt_func.to_wave(get_msg_converted, 'hikari', emotion, emotionlevel, pitch, speed, vlm, guild_id, voicetextAPI)

        filename = "./" + datetime.now().strftime(f"%Y%m%d_%H%M%S_{guild_id}") + ".wav"

        voicetype = dictionaries[l_vt]
        bot.loop.create_task(vt_func().new_to_voiceroid_wave(get_msg_converted, guild_id, voicetype, filename))
        #tmpfile = vt_func().to_voiceroid_wave(get_msg_converted, guild_id)

        while (voice[guild_id].is_playing()):
            await asyncio.sleep(1)

        while (not os.path.isfile(filename)):
            await asyncio.sleep(1)

        if os.path.isfile(filename):
            voice[guild_id].play(discord.FFmpegPCMAudio(filename))

            while (voice[guild_id].is_playing()):
                await asyncio.sleep(1)

            if os.path.isfile(filename):
                os.remove(filename) 

@bot.listen('on_ready')
async def on_ready():
    print(f'ログインに成功したよ！ [{bot.user}]')
    await bot.change_presence(activity=discord.Game(f'{len(voice)}サーバーが使用中 (Max:50)'))
    async for guild in bot.fetch_guilds(limit=150):
        dir = f"./Setting/{guild.id}.json"
        if os.path.isfile(dir) == False:
            f = open(dir, 'x', encoding='UTF-8')
            l = {"prefix" : prefix, "role" : "", "volume" : "75", "voicetype" : "akane_west"}
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
    guild_id = ctx.guild.id
    dir = f"./Setting/{guild_id}.json"
    if os.path.isfile(dir):
        f = open(dir, 'r')
        s = f.read()

        if len(s) == 0:
            l_vt = defaultvoicetype
        else:
            ar = json.loads(s)
            if not "voicetype" in ar:
                l_vt = defaultvoicetype
            else:
                l_vt = ar["voicetype"]

            voicetype = dictionaries[l_vt]
            print(voicetype)
            bot.loop.create_task(vt_func().new_to_voiceroid_wave(msg, ctx.guild.id, voicetype))
    #vt_func().new_to_voiceroid_wave(vc, msg, ctx.guild.id)
    #tmpfile = vt_func().to_voiceroid_wave("aaaaa")
    #print(tmpfile)

@bot.command(pass_context=True)
async def invite(ctx):
    await ctx.send("これがurlやで！")
    await ctx.send(f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions={'0'}&scope={'bot'}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("そんな呪文ないで！")

@bot.event
async def on_voice_state_update(member,before,after):
    global voice
    global channel

    isMe = (member.id is bot.user.id) and (before.channel is not None) and (after.channel is None)
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

        await bot.change_presence(activity=discord.Game(f'{len(voice)}サーバーが使用中 (Max:50)'))
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

        if author.voice is None:
            await ctx.send("先にvcに入ってな！") 
            return

        vo_ch = author.voice.channel
        guild = ctx.message.guild

        if not len(voice) >= 50:          
            voice[guild.id] = await vo_ch.connect()
            channel[guild.id] = ctx.channel.id     

            await ctx.send("おじゃまするで！") 
            await bot.change_presence(activity=discord.Game(f'{len(voice)}サーバーが使用中 (Max:50)'))   
        else:
            await ctx.send("今現在回線が混み合ってるから、時間を置いてから追加してな！")
    except Exception as ex:
        say_Exception(ex)

@bot.command(pass_context = True)
async def voicetype(ctx):
    if ldedPrefix[ctx.guild.id] is None:
        pfx = loaded_list["prefix"]
    else:
        pfx = ldedPrefix[ctx.guild.id]

    embed=discord.Embed(title="AkemiChan Voicetypes", description="Thanks for Using Akemichan!", color=0x4b0082)
    embed.set_author(name="Created by STNG", url="https://twitter.com/stngsan", icon_url="https://i.imgur.com/fVONXji.png")
    embed.set_thumbnail(url="https://i.imgur.com/SzmD9Hy.png")
    embed.add_field(name="`こうやって使ってな！`", value=f"`例:{pfx}setting voicetype akane_west`", inline=False)
    embed.add_field(name="月読アイ(v1)", value="設定用 : ai", inline=False)
    embed.add_field(name="琴葉 茜", value="設定用 : akane_west", inline=False)
    embed.add_field(name="琴葉 葵", value="設定用 : aoi", inline=False)
    embed.add_field(name="東北きりたん", value="設定用 : kiritan", inline=False)
    embed.add_field(name="水奈瀬コウ", value="設定用 : kou", inline=False)
    embed.add_field(name="京町セイカ(v1)", value="設定用 : seika", inline=False)
    embed.add_field(name="月読ショウタ(v1)", value="設定用 : shouta", inline=False)
    embed.add_field(name="民安ともえ(v1)", value="設定用 : tamiyasu", inline=False)
    embed.add_field(name="ついなちゃん (通常)", value="設定用 : tsuina", inline=False)
    embed.add_field(name="ついなちゃん (関西弁)", value="設定用 : tsuina_west", inline=False)
    embed.add_field(name="鷹の爪 吉田くん(v1)", value="設定用 : yoshidakun", inline=False)
    embed.add_field(name="結月ゆかり", value="設定用 : yukari, yukari_emo", inline=False)
    embed.add_field(name="東北ずんこ", value="設定用 : zunko", inline=False)
    embed.set_footer(text="バグ等の報告はDiscord(stng#4545)までお願いします🥳   (ver-beta)")
    await ctx.send(embed=embed)



@bot.command(pass_context = True)
async def help(ctx):
    global ldedPrefix
    if ldedPrefix[ctx.guild.id] is None:
        pfx = loaded_list["prefix"]
    else:
        pfx = ldedPrefix[ctx.guild.id]

    embed = discord.Embed(title="AkemiChan", description="Thanks for Using Akemichan!", color=0x4b0082, type="rich")
    embed.set_author(name="Created by STNG", url="https://twitter.com/stngsan", icon_url="https://i.imgur.com/fVONXji.png")
    embed.set_thumbnail(url="https://i.imgur.com/SzmD9Hy.png")
    embed.add_field(name=f"{pfx}join", value="`vcに参加するで！使うときは自分もvcに入ってな！`", inline=True)
    embed.add_field(name=f"{pfx}bye", value="`参加したvcから抜けるで！`", inline=False)
    embed.add_field(name=f"{pfx}add [単語] [読み方]", value="`[単語]を[読み方]で読むように覚えるで！`", inline=False)
    embed.add_field(name=f"{pfx}delete [単語]", value="`覚えた読み方で読むのをやめるで！`", inline=False)
    embed.add_field(name=f"{pfx}invite", value="`招待リンクを送るで！`", inline=False)
    embed.add_field(name=f"{pfx}setting [変更する要素] [値]", value="`サーバー内の設定を変更するで！`\n例:setting prefix #\n`例文通りに打つとコマンドを起動する文字が[ # ]になるで！`\n`詳しくは{pfx}setting help で確認してな！`", inline=False)
    embed.set_footer(text="バグ等の報告はDiscord(stng#4545)までお願いします🥳   (ver-beta)")

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

        if ctx.channel.id == channel[guild_id]:
            await ctx.channel.send('じゃあの')
            await voice[guild_id].disconnect()

            del voice[guild_id] 
            del channel[guild_id]

            await bot.change_presence(activity=discord.Game(f'{len(voice)}サーバーが使用中 (Max:50)'))
    except Exception as ex:
        print(f"An error has occurred in {ctx.guild.name}(ID:{ctx.guild.id})")
        say_Exception(ex)

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
    wL = {}
    dir = f"./Setting/{ctx.guild.id}.json"
    if os.path.isfile(dir):
        f = open(dir, 'r')
        s = f.read()

        if len(s) == 0:
             wL = {'prefix': prefix, 'role': '', 'volume' : '70', 'voicetype' : "akane_west"}
        else:
             wL = json.loads(s)
    f.close()

    saveflag = False

    if args[0] == 'help':
        embed=discord.Embed(title="Akemichan Setting Help", description="Thanks for Using Akemichan!", color=0x4b0082)
        embed.set_author(name="Created by STNG", url="https://twitter.com/stngsan", icon_url="https://i.imgur.com/fVONXji.png")
        embed.set_thumbnail(url="https://i.imgur.com/SzmD9Hy.png")
        embed.add_field(name="setting prefix [コマンド用の文字]", value="`[コマンド用の文字]でコマンドを起動するように設定するで！`", inline=False)
        embed.add_field(name="setting volume [音量]", value="`読み上げ時の音量を変えんで！`", inline=False)
        embed.add_field(name="setting voicetype", value=f"`読み上げる人を変えるで！`\n`詳しくは {wL['prefix']}voicetype で確認してな！`", inline=False)
        embed.set_footer(text="バグ等の報告はDiscord(stng#4545)までお願いします🥳   (ver-beta)")
        await ctx.send(embed=embed)
    if args[0] == 'prefix':
        saveflag = True
        wL['prefix'] = args[1]
        await ctx.send(f"コマンド用の文字を[{args[1]}]に設定したで！")
    if args[0] == 'volume':
        saveflag = True
        wL['volume'] = args[1]
        await ctx.send(f"音量を[{args[1]}]に設定したで！")
    if args[0] == 'voicetype':
        saveflag = True
        if args[1] in dictionaries.keys():
            wL['voicetype'] = args[1]
            await ctx.send(f"喋る人を[{dictionaries[args[1]]}]に設定したで！")

    if saveflag:
        f = open(dir, 'w')
        f.write(json.dumps(wL, sort_keys=True, indent=4))
        f.close()
########################################################################################################

async def test_loop():
    print(len(voice))
    time.sleep(2)

prefix = loaded_list["prefix"]
discordtoken = loaded_list["token"]
voicetextAPI = loaded_list["voicetextAPI"]
if not len(loaded_list["volume"]) == 0:
    volume = loaded_list["volume"]

prefix_is_null = len(prefix) == 0
token_is_null = len(discordtoken) == 0
apikey_is_null = len(voicetextAPI) == 0

if (prefix_is_null) or (token_is_null) or (apikey_is_null):
    pr1t(("prefixが空欄です。\n" if prefix_is_null else "") +
          ("tokenが空欄です。\n" if token_is_null else "") + 
          ("voicetextAPIが空欄です。\n" if apikey_is_null else "") +
          ("\nアプリケーションを終了します。"))
    sys.exit()
else:
    bot.loop.create_task(Logger_Loop())
    bot.run(discordtoken)


