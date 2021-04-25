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

intents = discord.Intents().default()
intents.members = True
client = discord.Client()
voiceClient = None

description = "Bot"
prefix = '$'
bot = commands.Bot(description=description, command_prefix=prefix, intents=intents)

voice = {} 
channel = {} 

@bot.listen('on_message')
async def on_message(message):
    if message.author.bot:
        return

    global voice
    global channel

    mess_id = message.author.id
    guild_id = message.guild.id # サーバID

    if message.content.startswith(prefix):
        return
        
    if guild_id not in channel:
        return

    if message.channel.id == channel[guild_id]:
        get_msg = re.sub(r'http(s)?://([\w-]+\.)+[\w-]+(/[-\w ./?%&=]*)?', 'URL', message.content)

        get_msg = get_msg.replace('<:', '')
        get_msg = re.sub(r':[0-9]*>', '', get_msg)

        tmpfile = vt_func.to_wave(get_msg, 'hikari', "happiness", "75", "100", "100", guild_id)

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

@bot.command()
async def testing(ctx, msg):
    await ctx.send(msg)

@bot.event
async def on_voice_state_update(member,before,after):
    global voice
    global channel

    guild_id = member.guild.id

    if guild_id not in channel:
        return

    while (voice[guild_id].is_playing()):
        await asyncio.sleep(1)

    if len(before.channel.members) == 1:
        # コマンドが、呼び出したチャンネルで叩かれている場合
        await voice[guild_id].disconnect() # ボイスチャンネル切断
        # 情報を削除
        del voice[guild_id] 
        del channel[guild_id]

@bot.command(pass_context = True, aliases=["connect","summon"])
async def join(ctx):
    global voice
    global channel
    author = ctx.message.author

    vo_ch = author.voice.channel
    guild = ctx.message.guild
    voice[guild.id] = await vo_ch.connect()
    channel[guild.id] = ctx.channel.id

@bot.command(pass_context = True)
async def bye(ctx):
    global guild_id
    global voice
    global channel
    guild_id = ctx.guild.id
    # コマンドが、呼び出したチャンネルで叩かれている場合
    if ctx.channel.id == channel[guild_id]:
        await ctx.channel.send('じゃあの')
        await voice[guild_id].disconnect() # ボイスチャンネル切断
        # 情報を削除
        del voice[guild_id] 
        del channel[guild_id]

bot.run('token here')
