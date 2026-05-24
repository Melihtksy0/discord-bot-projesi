import discord
from discord.ext import commands
from discord import app_commands

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # KOPYALADIĞIN KANAL ID'SİNİ BURAYA YAPIŞTIR (Örn: 10345... numaralı bir şey olacak, tırnaksız yaz)
        self.log_kanal_id = 1507805533430616074

    # 1. Silinen Mesajları Yakalama (Olay Dinleyicisi)
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Eğer mesajı silen kişi bir botsa (veya kendi mesajıysa) bunu yoksay
        if message.author.bot:
            return
            
        kanal = self.bot.get_channel(self.log_kanal_id)
        if not kanal:
            return

        embed = discord.Embed(title="🗑️ Mesaj Silindi", color=discord.Color.red())
        embed.add_field(name="Kullanıcı", value=message.author.mention, inline=True)
        embed.add_field(name="Kanal", value=message.channel.mention, inline=True)
        # Mesaj içeriği boşsa (sadece fotoğraf silindiyse) hata vermemesi için önlem
        embed.add_field(name="İçerik", value=message.content or "[Medya/Görsel]", inline=False)
        
        await kanal.send(embed=embed)

    # 2. Düzenlenen Mesajları Yakalama
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # Botların mesajlarını veya sadece link önizlemesi değişen mesajları yoksay
        if before.author.bot or before.content == after.content:
            return

        kanal = self.bot.get_channel(self.log_kanal_id)
        if not kanal:
            return

        embed = discord.Embed(title="✏️ Mesaj Düzenlendi", color=discord.Color.blue())
        embed.add_field(name="Kullanıcı", value=before.author.mention, inline=True)
        embed.add_field(name="Kanal", value=before.channel.mention, inline=True)
        embed.add_field(name="Eski Mesaj", value=before.content or "[Boş]", inline=False)
        embed.add_field(name="Yeni Mesaj", value=after.content or "[Boş]", inline=False)
        
        # Mesajın linkini de ekleyelim ki üstüne tıklayıp direkt mesaja gidilebilsin
        embed.add_field(name="Mesaja Git", value=f"[Tıkla]({after.jump_url})", inline=False)
        
        await kanal.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logger(bot))