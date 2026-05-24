import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # KOPYALADIĞIN ID'LERİ AŞAĞIYA GİR (Tırnak kullanmadan, sadece rakamları yaz)
        self.hosgeldin_kanal_id = 1507781991121289487
        self.verilecek_rol_id = 1507777390779043890

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # 1. OTOMATİK ROL VERME İŞLEMİ
        rol = member.guild.get_role(self.verilecek_rol_id)
        if rol:
            try:
                await member.add_roles(rol)
            except discord.Forbidden:
                print("❌ Hata: Botun yetkisi bu rolü vermeye yetmiyor. Botun rolünü yukarı taşıyın!")
            except Exception as e:
                print(f"❌ Rol verme hatası: {e}")

        # 2. HOŞ GELDİN MESAJI GÖNDERME İŞLEMİ
        kanal = self.bot.get_channel(self.hosgeldin_kanal_id)
        if kanal:
            # Görseldekiyle birebir aynı format: @kullanici! Sunucuya Hoşgeldiniz,
            await kanal.send(f"{member.mention}! Sunucuya Hoşgeldiniz,")

async def setup(bot):
    await bot.add_cog(Welcome(bot))