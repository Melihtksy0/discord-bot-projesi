import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Sunucunun sistem mesajı kanalını veya ilk bulduğu metin kanalını seçer
        channel = member.guild.system_channel or next(
            (ch for ch in member.guild.text_channels if ch.permissions_for(member.guild.me).send_messages), 
            None
        )
        
        if not channel:
            return

        embed = discord.Embed(
            title="📥 Aramıza Hoş Geldin!",
            description=f"Merhaba {member.mention}, Aramıza hoşgeldin! 🎉\n\nSeninle birlikte **{member.guild.member_count}** kişi olduk!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Kullanıcı ID: {member.id} • Sunucu: {member.guild.name}")

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))