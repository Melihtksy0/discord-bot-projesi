import discord
from discord.ext import commands
from discord import app_commands
import random

# YETKİLİ ROL ID'LERİ
YETKILI_ROLLER = [1507777388103205004, 1507777395799621832, 1507777393232969818, 1507777394377756712]

class Systems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_kullanicilar = {}

    # Yardımcı Güvenlik Fonksiyonu
    def yetki_var_mi(self, user):
        if getattr(user, "roles", None) is None: return False
        return any(rol.id in YETKILI_ROLLER for rol in user.roles)

    @app_commands.command(name="afk", description="AFK moduna geçersiniz.")
    async def afk(self, interaction: discord.Interaction, sebep: str = "Şu an buralarda değilim."):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ Yetkiniz yok!", ephemeral=True)
        self.afk_kullanicilar[interaction.user.id] = sebep
        await interaction.response.send_message(f"💤 **{interaction.user.display_name}**, AFK moduna geçtin.")

    @app_commands.command(name="takim_kur", description="Girilen oyuncuları iki eşit takıma böler.")
    async def takim_kur(self, interaction: discord.Interaction, oyuncular: str):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ Yetkiniz yok!", ephemeral=True)
        oyuncu_listesi = [isim.strip() for isim in oyuncular.split(",") if isim.strip()]
        random.shuffle(oyuncu_listesi)
        orta = len(oyuncu_listesi) // 2
        embed = discord.Embed(title="⚔️ Takımlar Belirlendi", color=discord.Color.blurple())
        embed.add_field(name="🔵 Mavi", value="\n".join(oyuncu_listesi[:orta]) or "Boş", inline=True)
        embed.add_field(name="🔴 Kırmızı", value="\n".join(oyuncu_listesi[orta:]) or "Boş", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="anket", description="Sunucuda oylama başlatır.")
    async def anket(self, interaction: discord.Interaction, soru: str, aciklama: str = None):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ Yetkiniz yok!", ephemeral=True)
        embed = discord.Embed(title="📊 Oylama", description=f"**{soru}**", color=discord.Color.gold())
        if aciklama: embed.add_field(name="Detay", value=aciklama, inline=False)
        await interaction.response.send_message(embed=embed)
        mesaj = await interaction.original_response()
        await mesaj.add_reaction("✅")
        await mesaj.add_reaction("❌")

    @app_commands.command(name="avatar", description="Kullanıcının avatarını gösterir.")
    async def avatar(self, interaction: discord.Interaction, kullanici: discord.Member = None):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ Yetkiniz yok!", ephemeral=True)
        kullanici = kullanici or interaction.user
        embed = discord.Embed(title=f"🖼️ Avatar", color=kullanici.color)
        embed.set_image(url=kullanici.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Systems(bot))