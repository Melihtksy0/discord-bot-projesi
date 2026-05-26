import discord
from discord.ext import commands
import os
import sys
import time
import asyncio

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- BOT YENİDEN BAŞLATMA ---
    @commands.hybrid_command(name="restart", description="Botu yeniden başlatır (Sadece yetkililer).")
    @commands.has_permissions(administrator=True)
    async def restart(self, ctx):
        embed = discord.Embed(
            title="🔄 Sistem Yeniden Başlatılıyor...",
            description="Bot şu anda güncelleniyor ve yeniden başlatılıyor. Kısa süre içinde aktif olacaktır.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        
        print("🔄 Bot yeniden başlatılıyor...")
        os.execv(sys.executable, ['python'] + sys.argv)

    # --- CANLI GERİ SAYIM ---
    @commands.hybrid_command(name="gerisayim", description="Everyone atarak canlı bir geri sayım başlatır.")
    @commands.has_permissions(administrator=True)
    async def gerisayim(self, ctx, dakika: int, *, baslik: str = "Önemli Etkinlik"):
        await ctx.defer()
        
        bitis_zamani = int(time.time()) + (dakika * 60)
        
        embed = discord.Embed(
            title=f"🚨 GERİ SAYIM: {baslik}",
            description=f"Dikkat! Sürenin dolmasına kalan zaman:\n\n# <t:{bitis_zamani}:R>",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Başlatan: {ctx.author.display_name}")
        
        msg = await ctx.send(content="@everyone", embed=embed)
        
        await asyncio.sleep(dakika * 60)
        
        bitis_embed = discord.Embed(
            title=f"🎉 SÜRE DOLDU: {baslik}",
            description="Geri sayım başarıyla tamamlandı!",
            color=discord.Color.green()
        )
        await msg.reply(content="🔔 @everyone Süre doldu, toplanın!", embed=bitis_embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))