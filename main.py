import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
from submodules.VoiceText import vt_func
from pykakasi import kakasi
import logging
import regex
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
prefix = '$'
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
#########################################

logger = None

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

#########################################

def get_setting_from_guild(id):
    dir = f"./Setting/{id}.json"
    if os.path.isfile(dir):
        f = open(dir, 'r')
        s = f.read()
        ar = json.loads(s)
        return ar
    else:
        return None

#########################################

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

DefaultGuildSetting = {"prefix" : loaded_list['prefix'], "role" : "", "volume" : loaded_list['volume'], "voicetype" : "akane_west", 'servername' : "None", 'lastused' : 0}

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

async def Disconnect_(guild_id):
    global voice
    global channel
    
    if guild_id not in voice or guild_id not in channel:
        if guild_id not in voice:
            print("guild_id is not in voice")
        if guild_id not in channel:
            print("guild_id is not in channel")
        return

    print(f"{bot.get_guild(guild_id).name}のvcから離脱します。")
    
    await bot.get_channel(channel[guild_id]).send('じゃあの')
    await voice[guild_id].disconnect()

    del voice[guild_id]
    del channel[guild_id]

def say_Exception(e):
    logging.exception(e)
    #print('=== エラー内容 ===')
    #print('type:' + str(type(e)))
    #print('args:' + str(e.args))
    #print('message:' + e.message)
    #print('e_main:' + str(e))
    #print('=======================')


async def Logger_Loop():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
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

async def convert_wave_method(message, guild_id):
    try:
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
            
            if len(message.content) == 0:
                return

            voicetype = dictionaries[l_vt]
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

            filename = "./" + datetime.now().strftime(f"%Y%m%d_%H%M%S_{guild_id}") + ".wav"
            p = regex.compile(r'[\p{Script=Hiragana}\p{Script=Katakana}ーa-z\p{Script=Han}0-9]+')
            ret = p.match(get_msg)

            if ret is None:
                return

            #m = re.match('[a-zA-Z0-9_]+', get_msg)
            #m = re.match(r'\w+', m)
            #print(m)
            await start_speak(ret, guild_id, voicetype, filename)
    except Exception as ex:
        say_Exception(ex)

async def start_speak(msg, guildid, vctype, fname):
    global voice
    filename = "./" + datetime.now().strftime(f"%Y%m%d_%H%M%S_{guildid}") + ".wav"
    await vt_func().new_to_voiceroid_wave(msg, guildid, vctype, fname)
    #bot.loop.create_task(vt_func().new_to_voiceroid_wave(msg, guildid, vctype, fname))
        #tmpfile = vt_func().to_voiceroid_wave(get_msg_converted, guild_id)

    while (voice[guildid].is_playing()):
        await asyncio.sleep(0)

    while (not os.path.isfile(fname)):
        await asyncio.sleep(0)

    if os.path.isfile(fname):
        voice[guildid].play(discord.FFmpegPCMAudio(fname))

    while (voice[guildid].is_playing()):
        await asyncio.sleep(0)

    if os.path.isfile(fname):
        os.remove(fname)

@bot.listen('on_message')
async def on_message(message):
    try:
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
            bot.loop.create_task(convert_wave_method(message, guild_id))
    except Exception as ex:
        say_Exception(ex)

@bot.listen('on_ready')
async def on_ready():
    print(f'ログインに成功したよ！ [{bot.user}]')
    await bot.change_presence(activity=discord.Game(f'{len(voice)}サーバーが使用中 (Max:50)'))
    async for guild in bot.fetch_guilds(limit=999):
        dir = f"./Setting/{guild.id}.json"
        if os.path.isfile(dir) == False:
            f = open(dir, 'x', encoding='UTF-8')
            l = DefaultGuildSetting
            l['servername'] = guild.name
            f.write(json.dumps(l, sort_keys=True, indent=4))
            f.close()

@bot.listen('on_guild_join')
async def on_guild_join(guild: discord.Guild):
    print(f"{guild.name} に参加しました！")
    dir = f"./Setting/{guild.id}.json"
    if os.path.isfile(dir) == False:
        f = open(dir, 'x', encoding='UTF-8')
        l = DefaultGuildSetting
        l['servername'] = guild.name
        f.write(json.dumps(l, sort_keys=True, indent=4))
        f.close()

@bot.listen('on_guild_remove')
async def on_guild_remove(guild: discord.Guild):
    print(f"{guild.name} から削除されました。")
    dir = f"./Setting/{guild.id}.json"
    if os.path.isfile(dir) == True:
        os.remove(dir)
        print('設定ファイルを削除しました。')

@bot.command(pass_context=True)
async def skip(ctx):
    try:
        global voice
        global channel

        guild_id = ctx.guild.id

        if ctx.author.bot:
            return

        if ctx.guild is None or ctx.channel is None:
            return

        if guild_id not in channel:
            return

        if guild_id not in voice:
            return

        voice[guild_id].stop()
    except Exception as ex:
        say_Exception(ex)

@bot.command()
async def testing(ctx):
    got_setting = get_setting_from_guild(ctx.guild.id)
    if got_setting is not None:
        print(got_setting)

    #for guild in bot.guilds:
    #    for Vchannel in guild.voice_channels:
    #        for member in Vchannel.members:
    #            if member.id is bot.user.id:
    #               print(f"{guild.name}にて既に接続済みのユーザーを確認しました。再接続を試みます。")
        #async for vChannel in guild.voice_channels:
        #    print(vChannel)


@bot.command()
async def say(ctx, msg):
    if ctx.author.id == 264463661295206400:
        global voice
        global channel
        for joining_id in channel.keys():
            send_chl = bot.get_channel(channel[joining_id])
            await send_chl.send(msg)

@bot.command(pass_context=True)
async def invite(ctx):
    await ctx.send("これがurlやで！")
    await ctx.send(f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions={'0'}&scope={'bot'}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("そんな呪文ないで！")

@bot.listen('on_voice_state_update')
async def voice_move_event(member, before, after):
    #aftName = 'None' if after.channel is None else after.channel.name

    if before.channel is not None:
        if before.channel is not after.channel:
            pass
            if after.channel is None:
                pass
                #print(f"{member.name} is Leaved from {before.channel.name} ({member.guild.name})") #vcから抜けたとき
            else:
                pass
                #print(f"{member.name} is Moved to {aftName} ({member.guild.name})")                #vcからvcへ移動した時
    elif before.channel is None:
        pass
        #print(f"{member.name} is Joined to {str(after.channel.name)} ({member.guild.name})")       #vcへ参加した時

@bot.listen('on_voice_state_update')
async def on_voice_state_update(member,before,after):
    global voice
    global channel

    guildID = member.guild.id
    if before.channel is not None:
        if guildID in voice:
            if len(before.channel.members) == 1:
                for m in before.channel.members:
                    if m.id is bot.user.id:
                        await Disconnect_(guildID)
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

            wL = {}
            dir = f"./Setting/{ctx.guild.id}.json"
            if os.path.isfile(dir):
                f = open(dir, 'r')
                s = f.read()

                if len(s) == 0:
                    wL = DefaultGuildSetting
                else:
                    wL = json.loads(s)
            f.close()

            wL['lastused'] = ctx.channel.id

            f = open(dir, 'w')
            f.write(json.dumps(wL, sort_keys=True, indent=4))
            f.close()

            await ctx.send("おじゃまするで！")
            await bot.change_presence(activity=discord.Game(f'{len(voice)}サーバーが使用中 (Max:50)'))   
            print(f"{ctx.guild.name}のvcに参加しました。")
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

@bot.command()
async def ban(ctx):
    pass

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
    embed.add_field(name=f"{pfx}check_dictional [単語]", value="`[単語]を覚えてる読み方で送信するで！`", inline=False)
    embed.add_field(name=f"{pfx}check_dictional_all", value="`このサーバーで覚えてる読み方をすべて送信するで！`", inline=False)
    embed.add_field(name="使い方はこちらのリンクへ", value="[こちら](https://github.com/StangIsGod/TextToSpeech-Python-Bot/wiki/%E4%BD%BF%E3%81%84%E6%96%B9)")
    embed.set_footer(text="バグ等の報告はDiscord(stng#4545)までお願いします🥳   (ver-beta)\n")

    await ctx.send(embed=embed)

@bot.command(pass_context = True, aliases=["dc","disconnect","kill", "Bye"])
async def bye(ctx):
    try:
        global channel
        if ctx.channel.id == channel[ctx.guild.id]:
            await Disconnect_(ctx.guild.id)
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

@bot.command(pass_context = True)
async def check_dictional_all(ctx):
    guild_id = ctx.guild.id
    dir = f"{DicDir}/{guild_id}.json"
    wA = {}
    if os.path.isfile(dir):
        f = open(dir, "r")
        s = f.read()
        if len(s) != 0:
            wA = json.loads(s)
            msg = ""
            for keyword in wA.keys():
                await ctx.send(f"[{keyword}] を [{wA[keyword]}]")
            await ctx.send(f"って読んでるで！")

@bot.command()
async def setting(ctx, *args):
    wL = {}
    dir = f"./Setting/{ctx.guild.id}.json"
    if os.path.isfile(dir):
        f = open(dir, 'r')
        s = f.read()

        if len(s) == 0:
            wL = DefaultGuildSetting
        else:
            wL = json.loads(s)
    f.close()

    saveflag = False

    if ldedPrefix[ctx.guild.id] is None:
        pfx = loaded_list["prefix"]
    else:
        pfx = ldedPrefix[ctx.guild.id]

    if args[0] == 'help':
        embed=discord.Embed(title="Akemichan Setting Help", description="Thanks for Using Akemichan!", color=0x4b0082)
        embed.set_author(name="Created by STNG", url="https://twitter.com/stngsan", icon_url="https://i.imgur.com/fVONXji.png")
        embed.set_thumbnail(url="https://i.imgur.com/SzmD9Hy.png")
        embed.add_field(name=f"{pfx}setting prefix [コマンド用の文字]", value="`[コマンド用の文字]でコマンドを起動するように設定するで！`", inline=False)
        embed.add_field(name=f"{pfx}setting volume [音量]", value="`読み上げ時の音量を変えんで！`", inline=False)
        embed.add_field(name=f"{pfx}setting voicetype", value=f"`読み上げる人を変えるで！`\n`詳しくは {wL['prefix']}voicetype で確認してな！`", inline=False)
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

    if len(args[0]) == 0:
        await ctx.send('そんな呪文ないで！')

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
    print(("prefixが空欄です。\n" if prefix_is_null else "") +
          ("tokenが空欄です。\n" if token_is_null else "") +
          ("voicetextAPIが空欄です。\n" if apikey_is_null else "") +
          ("\nアプリケーションを終了します。"))
    sys.exit()
else:
    #bot.loop.create_task(Exception_Loop())
    bot.loop.create_task(Logger_Loop())
    bot.run(discordtoken, reconnect=True)


