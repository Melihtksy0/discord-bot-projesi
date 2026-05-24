import discord
from discord.ext import commands
from discord import app_commands

# YETKİLİ ROL ID'LERİ
YETKILI_ROLLER = [1507777388103205004, 1507777395799621832, 1507777393232969818, 1507777394377756712]

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Botun gecikme süresini gösterir.")
    async def ping(self, interaction: discord.Interaction):
        # Güvenlik Kontrolü
        if getattr(interaction.user, "roles", None) is None or not any(rol.id in YETKILI_ROLLER for rol in interaction.user.roles):
            return await interaction.response.send_message("❌ **Güvenlik Duvarı:** Bu komutu kullanmaya yetkiniz yok!", ephemeral=True)

        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! 🏓 {latency}ms", ephemeral=True)

async def setup(bot):
    await bot.add_cog(General(bot))