import discord
from discord.ext import commands

# LOGLARIN DÜŞECEĞİ GİZLİ KANALIN ID'Sİ
MOD_LOG_KANALI_ID = 1507891861631533106

class AuditLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. SİLİNEN MESAJLARI YAKALAMA
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return # Botların kendi sildiği mesajları yoksay
        
        log_kanal = self.bot.get_channel(MOD_LOG_KANALI_ID)
        if not log_kanal: return

        embed = discord.Embed(title="🗑️ Mesaj Silindi", color=discord.Color.red())
        embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
        embed.add_field(name="Kanal", value=message.channel.mention, inline=False)
        embed.add_field(name="Silinen İçerik", value=message.content or "*(İçerik yok veya medya/embed silindi)*", inline=False)
        embed.set_footer(text=f"Kullanıcı ID: {message.author.id}")
        
        await log_kanal.send(embed=embed)

    # 2. DÜZENLENEN MESAJLARI YAKALAMA
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot: return
        if before.content == after.content: return # Discord'un kendi embed güncellemelerini yoksay
        
        log_kanal = self.bot.get_channel(MOD_LOG_KANALI_ID)
        if not log_kanal: return

        embed = discord.Embed(title="✏️ Mesaj Düzenlendi", url=after.jump_url, color=discord.Color.orange())
        embed.set_author(name=before.author.name, icon_url=before.author.display_avatar.url)
        embed.add_field(name="Kanal", value=before.channel.mention, inline=False)
        embed.add_field(name="Eski Hal", value=before.content or "*(Boş)*", inline=False)
        embed.add_field(name="Yeni Hal", value=after.content or "*(Boş)*", inline=False)
        embed.set_footer(text=f"Kullanıcı ID: {before.author.id}")
        
        await log_kanal.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AuditLog(bot))