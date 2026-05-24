import discord
from discord.ext import commands

class SosyalMedya(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Komutumuzun adı /sosyal olacak
    @commands.hybrid_command(name="sosyal", description="Sosyal medya bağlantılarını gösterir.")
    async def sosyal(self, ctx):
        
        # 1. Embed'in temel iskeleti (Başlık ve sol şerit rengi)
        embed = discord.Embed(
            title="🔗 Sosyal Medya Bağlantıları",
            color=discord.Color.green() # Sol taraftaki yeşil şerit
        )

        # 2. Sağ üstteki fotoğraf (Thumbnail)
        # Kendi fotoğrafını Discord'a yükleyip "Bağlantıyı Kopyala" diyerek buraya yapıştırabilirsin.
        embed.set_thumbnail(url="https://i.imgur.com/BoşBırakmaBurayaResimLinkiGelecek.png") 

        # 3. İçerik kısmı (\n işareti alt satıra geçmek içindir)
        aciklama = (
            "**🟩 Kick**\n"
            "https://kick.com/yusha99 [BURDAYIZ]\n\n"
            
            "**📸 Instagram**\n"
            "https://www.instagram.com/21yusha1999/?hl=tr\n\n"

            "**▶️ Youtube**\n"
            "https://www.youtube.com/@yusha1999\n\n"
   
        )
        
        embed.description = aciklama

        # Mesajı gönder
        await ctx.send(embed=embed)

# Bu fonksiyon Cog'u bota tanıtır
async def setup(bot):
    await bot.add_cog(SosyalMedya(bot))