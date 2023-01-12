from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bsoup
import requests
from random import randint as rnd
import ruclip
from rudalle.pipelines import generate_images, show, super_resolution, cherry_pick_by_ruclip
from rudalle import get_rudalle_model, get_tokenizer, get_vae, get_realesrgan
from rudalle.utils import seed_everything
import torch
import asyncio
import discord as ds  # Подключаем библиотеку
from discord.ext import commands, tasks
from os.path import join, dirname
from dotenv import load_dotenv
import os
from os.path import join, dirname
from pathlib import Path

p = Path(__file__).parents[1]
print(p)
dotenv_path = join(p, '.env')
load_dotenv(dotenv_path)
TOKEN = str(os.getenv("TOKEN"))
url_2 = str(os.getenv("URL_2"))
titles = ['test_title']
print(url_2)


class Usual(commands.Cog):

    @commands.command(name="ping", brief="Ping the bot")
    async def ping(self, ctx):
        await ctx.reply("Pong!")

    @commands.command(name="hello", brief="Say hello to the bot")
    async def hello(self, ctx):
        await ctx.reply("Привет!")

    @commands.command(name="flip", brief="Flip the coin")
    async def flip(self, ctx):
        if rnd(1, 2) == 1:
            await ctx.reply(
                'Орел'
            )
        else:
            await ctx.reply(
                'Решка'
            )

    @commands.command(name="say", brief="bot send a message")
    async def ping(self, ctx, *, message: str):
        await ctx.send(message)

    @commands.command(name="free", brief="start bot to watch for free games and take the last post from pikabu")
    async def free(self, ctx):
        await ctx.send('Бот включен.')
        await self.updating(ctx)

    @tasks.loop(minutes=30)
    async def updating(self, ctx):
        response = requests.get(url_2, headers={'User-Agent': UserAgent().chrome})

        soup = bsoup(response.text, 'html.parser')
        title = soup.find('h2', attrs={'story__title'}).text

        if title not in titles:
            titles[0] = title
            href = soup.find('a', attrs={'story__title-link'})['href']
            content_text = soup.find('div', attrs={'story-block story-block_type_text'}).text
            date = soup.find('time', attrs={'caption story__datetime hint'}).text

            embed = ds.Embed(color=0xff9900, title=title)
            embed.add_field(name='Описание', value=content_text, inline=True)
            embed.add_field(name='', value='', inline=False)
            embed.add_field(name='Ссылка', value=href, inline=True)
            embed.add_field(name='', value='', inline=False)
            embed.add_field(name='Дата', value=date, inline=True)
            await ctx.send(embed=embed)

    @commands.command(name="malevich", brief="DONT USE STILL IN PROGRESS. Careful its a demo functon, "
                                             "RU-DALLEE will generate your image from text,"
                                             "you have to wait 5-10 minutes")
    async def malevich(self, ctx, *, message: str):
        ctx.send('Wait your pictures is generating...')
        print('torch:', torch.cuda.is_available())
        # prepare models:
        device = 'cuda'
        dalle = get_rudalle_model('Malevich', pretrained=True, fp16=True, device=device)
        vae, tokenizer = get_vae(dwt=True).to(device), get_tokenizer()
        # pipeline utils:
        realesrgan = get_realesrgan('x2', device=device)
        clip, processor = ruclip.load('ruclip-vit-base-patch32-384', device=device)
        clip_predictor = ruclip.Predictor(clip, processor, device, bs=4)
        text = message
        seed_everything(42)
        pil_images = []
        scores = []
        for top_k, top_p, images_num in [
            (768, 0.99, 12),
        ]:
            _pil_images, _scores = generate_images(text, tokenizer, dalle, vae, top_k=top_k, images_num=images_num,
                                                   bs=4,
                                                   top_p=top_p)
            pil_images += _pil_images
            scores += _scores

        # show(pil_images, 4)

        top_images, clip_scores = cherry_pick_by_ruclip(pil_images, text, clip_predictor, count=4)
        # show(top_images, 3)

        sr_images = super_resolution(top_images, realesrgan)
        show(sr_images, 2)  # add ctx send or smth like this need to think...
