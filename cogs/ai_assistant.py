import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai

# YETKİLİ ROL ID'LERİ
YETKILI_ROLLER = [1507777388103205004, 1507777395799621832, 1507777393232969818, 1507777394377756712]

class AIAssistant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        genai.configure(api_key="AIzaSyBnKUXqptwuA5YQ5Sa9kF_sc4GKORHqWCo") # ŞİFRENİ BURAYA GİRMEYİ UNUTMA
        
        secili_model = None
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                secili_model = m.name
                break
        if secili_model:
            self.model = genai.GenerativeModel(secili_model)

    @app_commands.command(name="sor", description="Yapay zekaya soru sor.")
    async def sor(self, interaction: discord.Interaction, soru: str):
        # Güvenlik Duvarı
        if getattr(interaction.user, "roles", None) is None or not any(rol.id in YETKILI_ROLLER for rol in interaction.user.roles):
            return await interaction.response.send_message("❌ **Güvenlik Duvarı:** AI sistemini kullanmaya yetkiniz yok!", ephemeral=True)
            
        await interaction.response.defer() 
        try:
            cevap = self.model.generate_content(soru)
            yanit_metni = cevap.text[:1990] + "..." if len(cevap.text) > 2000 else cevap.text
            embed = discord.Embed(title="🧠 Yapay Zeka", description=yanit_metni, color=discord.Color.purple())
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Hata: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AIAssistant(bot))