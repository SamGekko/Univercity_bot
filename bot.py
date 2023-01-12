import sys
import platform
import discord as ds  # Подключаем библиотеку
import os
from discord.ext import commands
from cogs import music, error_f, meta, usual
import config
from os.path import join, dirname
from dotenv import load_dotenv

cfg = config.load_config()

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
PREFIX = str(os.getenv('PREFIX'))


intents = ds.Intents.default()  # Подключаем "Разрешения"
intents.message_content = True
intents.members = True

# префикс и разрешения
bot = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"discord.py API version: {ds.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    print(f"{bot.user} is ready and online!")


@bot.event
async def on_member_join(member):
    print("Recognised that a member called " + member.name + " joined")
    try:
        await bot.send_message(member, f'Здравствуйте {member.name}, добро пожаловать на сервер '
                                           f'{ds.guild.Guild.__name__}!')
        print("Sent message to " + member.name)
    except:
        print("Couldn't message " + member.name)
    embed = ds.Embed(
        title="Welcome " + member.name + "!",
        description="We're so glad you're here!",
        color=ds.Color.green()
    )
    channel = bot.get_channel(1063209198567051440)
    await channel.send(embed=embed)
    '''
    role = ds.utils.get(member.server.roles, name="my_role")
    await bot.add_roles(member, role)  # Gives the role to the user
    print("Added role '" + role.name + "' to " + member.name)'''


@bot.event
async def on_member_leave(member):
    print("Recognised that a member called " + member.name + " left")
    embed = ds.Embed(
        title="😢 Goodbye " + member.name + "!",
        description="Until we meet again old friend.",
        color=ds.Color.red()
    )
    channel = bot.get_channel(1063209198567051440)
    await channel.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply("Unknown command.")


@bot.event
async def on_guild_join(guild):

    text_channels = guild.text_channels

    if text_channels:
        channel = text_channels[0]

    await channel.send('Привет, {}!'.format(guild.name))


COGS = [music.Music, error_f.CommandErrorHandler, meta.Meta, usual.Usual]


def add_cogs(bot):
    for cog in COGS:
        bot.add_cog(cog(bot, cfg))  # Initialize the cog and add it to the bot


def run():
    add_cogs(bot)
    if cfg["token"] == "":
        raise ValueError(
            "No token has been provided. Please ensure that config.toml contains the bot token."
        )
        sys.exit(1)
    bot.run(cfg["token"])