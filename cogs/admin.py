import discord
from discord.ext import commands
import time
import asyncio

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- CANLI GERİ SAYIM (SADECE YETKİLİ) ---
    @commands.hybrid_command(name="gerisayim", description="Everyone atarak canlı bir geri sayım başlatır.")
    @commands.has_permissions(administrator=True) # GÜVENLİK KİLİDİ: Sadece Yöneticiler
    async def gerisayim(self, ctx, dakika: int, *, baslik: str = "Önemli Etkinlik"):
        await ctx.defer()
        
        # Bitiş zamanını Discord'un anlayacağı Unix formatına çeviriyoruz
        bitis_zamani = int(time.time()) + (dakika * 60)
        
        embed = discord.Embed(
            title=f"🚨 GERİ SAYIM: {baslik}",
            description=f"Dikkat! Sürenin dolmasına kalan zaman:\n\n# <t:{bitis_zamani}:R>",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Başlatan: {ctx.author.display_name}")
        
        # Mesajı gönder ve everyone at
        msg = await ctx.send(content="@everyone", embed=embed)
        
        # Arka planda bekle ve süre bitince haber ver
        await asyncio.sleep(dakika * 60)
        
        bitis_embed = discord.Embed(
            title=f"🎉 SÜRE DOLDU: {baslik}",
            description="Geri sayım başarıyla tamamlandı!",
            color=discord.Color.green()
        )
        await msg.reply(content="🔔 @everyone Süre doldu, toplanın!", embed=bitis_embed)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))