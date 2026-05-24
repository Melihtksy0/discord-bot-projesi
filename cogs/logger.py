import discord
from discord.ext import commands

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1507891861631533106

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        channel = self.bot.get_channel(self.log_channel_id)
        if not channel:
            return

        icerik = message.content
        if not icerik:
            icerik = "*(Metin içeriği yok - Sadece görsel veya dosya silinmiş olabilir)*"
        elif len(icerik) > 1000:
            icerik = icerik[:1000] + "... (mesaj çok uzundu, kesildi)"

        aciklama = f"""**Kanal:** {message.channel.mention}
**Silinen İçerik:**
```text
{icerik}
```"""

        embed = discord.Embed(
            description=aciklama,
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        
        avatar_url = message.author.display_avatar.url if message.author.display_avatar else None
        embed.set_author(name=f"{message.author.name} - Mesaj Silindi", icon_url=avatar_url)
        embed.set_footer(text=f"Kullanıcı ID: {message.author.id}")
        
        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Silme Logu Gönderilemedi: {e}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return

        channel = self.bot.get_channel(self.log_channel_id)
        if not channel:
            return

        eski_icerik = before.content if before.content else "*(Boş)*"
        yeni_icerik = after.content if after.content else "*(Boş)*"
        
        if len(eski_icerik) > 900: eski_icerik = eski_icerik[:900] + "..."
        if len(yeni_icerik) > 900: yeni_icerik = yeni_icerik[:900] + "..."

        aciklama = f"""**Kanal:** {before.channel.mention} | [Düzenlenen Mesaja Git]({after.jump_url})

**Eski Hali:**
```text
{eski_icerik}
{yeni_icerik}
```"""

        embed = discord.Embed(
            description=aciklama,
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        avatar_url = before.author.display_avatar.url if before.author.display_avatar else None
        embed.set_author(name=f"{before.author.name} - Mesaj Düzenlendi", icon_url=avatar_url)
        embed.set_footer(text=f"Kullanıcı ID: {before.author.id}")

        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Düzenleme Logu Gönderilemedi: {e}")

async def setup(bot):
    await bot.add_cog(Logger(bot))