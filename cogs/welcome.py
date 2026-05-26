import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Belirttiğin yeni Karşılama Kanalı ID'si
        self.welcome_channel_id = 1507781991121289487 

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(self.welcome_channel_id)
        if not channel:
            return

        # Modern ve Göz Alıcı Tasarım
        embed = discord.Embed(
            title="👋 Aramıza Hoş Geldin!",
            description=f"Selam {member.mention}, sunucumuza katıldığın için çok mutluyuz! 🎉\n\nSeninle birlikte koca bir aile olduk ve **{member.guild.member_count}** kişiye ulaştık. Kurallara göz atmayı unutma!",
            color=discord.Color.from_rgb(88, 101, 242) # Discord'un orijinal "Blurple" rengi
        )
        
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
            
        embed.set_footer(
            text=f"Kullanıcı ID: {member.id} • {member.guild.name}", 
            icon_url=member.guild.icon.url if member.guild.icon else None
        )

        # Hem kişiyi etiketler (bildirim gitmesi için) hem de şık kartı gönderir
        await channel.send(content=f"{member.mention}", embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))