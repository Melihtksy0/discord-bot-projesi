import discord
from discord.ext import commands
from discord import app_commands

# YETKİLİ ROL ID'LERİ
YETKILI_ROLLER = [1507777388103205004, 1507777395799621832, 1507777393232969818, 1507777394377756712]

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Yardımcı Güvenlik Fonksiyonu
    def yetki_var_mi(self, user):
        if getattr(user, "roles", None) is None: return False
        return any(rol.id in YETKILI_ROLLER for rol in user.roles)

    @app_commands.command(name="ban", description="Kullanıcıyı yasaklar.")
    async def ban(self, interaction: discord.Interaction, uye: discord.Member, sebep: str = "Belirtilmedi"):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ Yetkiniz yok!", ephemeral=True)
        await uye.ban(reason=sebep)
        await interaction.response.send_message(f"✅ {uye.mention} sunucudan yasaklandı.")

    @app_commands.command(name="kick", description="Kullanıcıyı atar.")
    async def kick(self, interaction: discord.Interaction, uye: discord.Member, sebep: str = "Belirtilmedi"):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ Yetkiniz yok!", ephemeral=True)
        await uye.kick(reason=sebep)
        await interaction.response.send_message(f"✅ {uye.mention} sunucudan atıldı.")

    @app_commands.command(name="temizle", description="Mesajları siler.")
    async def temizle(self, interaction: discord.Interaction, miktar: int):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ Yetkiniz yok!", ephemeral=True)
        await interaction.channel.purge(limit=miktar)
        await interaction.response.send_message(f"✅ {miktar} mesaj silindi.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))