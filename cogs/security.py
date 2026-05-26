import discord
from discord.ext import commands
import re

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1507891861631533106
        self.yasakli_kelimeler = ["küfür1", "küfür2", "reklam"] 

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        if message.author.guild_permissions.manage_messages:
            return

        icerik = message.content.lower()
        reklam_tespit = False
        kufur_tespit = False

        if "discord.gg/" in icerik or re.search(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", icerik):
            reklam_tespit = True

        for kelime in self.yasakli_kelimeler:
            if kelime in icerik:
                kufur_tespit = True
                break

        if reklam_tespit or kufur_tespit:
            try:
                await message.delete()
            except discord.Forbidden:
                print("HATA: Botun mesaj silme yetkisi yok!")
                return
            except discord.NotFound:
                pass
            
            sebep = "🔗 Reklam / Link Paylaşımı" if reklam_tespit else "🤬 Yasaklı Kelime / Küfür"
            
            try:
                await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda {sebep} yasaktır!", delete_after=5)
            except:
                pass
            
            log_channel = self.bot.get_channel(self.log_channel_id)
            if log_channel:
                safe_content = message.content
                if len(safe_content) > 1000:
                    safe_content = safe_content[:1000] + "..."
                    
                aciklama = f"""**Kanal:** {message.channel.mention}
**Engellenme Sebebi:** `{sebep}`
**Engellenen İçerik:**
```text
{safe_content}
```"""
                
                embed = discord.Embed(
                    description=aciklama,
                    color=discord.Color.dark_red(),
                    timestamp=discord.utils.utcnow()
                )
                
                avatar_url = message.author.display_avatar.url if message.author.display_avatar else None
                embed.set_author(name=f"{message.author.name} - AutoMod Müdahalesi 🛡️", icon_url=avatar_url)
                embed.set_footer(text=f"Kullanıcı ID: {message.author.id}")
                
                try:
                    await log_channel.send(embed=embed)
                except Exception as e:
                    print(f"AutoMod logu gönderilemedi: {e}")

async def setup(bot):
    await bot.add_cog(Security(bot))