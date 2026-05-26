import discord
from discord.ext import commands
from discord import app_commands

# --------------------------------------------------
# 1. OYUNLAR, İNGİLİZCE RÜTBELER, RENK KODLARI VE RÜTBE EMOJİLERİ
# --------------------------------------------------
OYUN_RUTBELERI = {
    "League of Legends": {
        "Iron": (0x595959, "🪨"), "Bronze": (0xcd7f32, "🥉"), "Silver": (0xc0c0c0, "🥈"),
        "Gold": (0xffd700, "🥇"), "Platinum": (0x00ced1, "💠"), "Emerald": (0x2ecc71, "❇️"),
        "Diamond": (0xb9f2ff, "💎"), "Master": (0x9b59b6, "🟣"), "Grandmaster": (0xe74c3c, "🔴"),
        "Challenger": (0xf1c40f, "👑")
    },
    "Valorant": {
        "Iron": (0x595959, "⚪"), "Bronze": (0xcd7f32, "🟤"), "Silver": (0xc0c0c0, "🥈"),
        "Gold": (0xffd700, "🟡"), "Platinum": (0x00ced1, "💠"), "Diamond": (0xb9f2ff, "💎"),
        "Ascendant": (0x2ecc71, "❇️"), "Immortal": (0xe74c3c, "🔴"), "Radiant": (0xfffdd0, "🌟")
    },
    "CS2": {
        "Silver": (0xc0c0c0, "🥈"), "Gold Nova": (0xffd700, "🥇"), "Master Guardian": (0x3498db, "🛡️"),
        "Legendary Eagle": (0x2980b9, "🦅"), "Supreme Master First Class": (0x8e44ad, "🌟"), "The Global Elite": (0xf1c40f, "🌍")
    },
    "Rainbow Six Siege": {
        "Copper": (0xb87333, "🧱"), "Bronze": (0xcd7f32, "🥉"), "Silver": (0xc0c0c0, "🥈"),
        "Gold": (0xffd700, "🥇"), "Platinum": (0x00ced1, "💠"), "Emerald": (0x2ecc71, "❇️"),
        "Diamond": (0x9b59b6, "💎"), "Champion": (0xe74c3c, "🏆")
    },
    "Apex Legends": {
        "Rookie": (0x7f8c8d, "🔰"), "Bronze": (0xcd7f32, "🥉"), "Silver": (0xc0c0c0, "🥈"),
        "Gold": (0xffd700, "🥇"), "Platinum": (0x3498db, "💠"), "Diamond": (0x00ced1, "💎"),
        "Master": (0x9b59b6, "🟣"), "Apex Predator": (0xe74c3c, "👹")
    },
    "Fortnite": {
        "Bronze": (0xcd7f32, "🥉"), "Silver": (0xc0c0c0, "🥈"), "Gold": (0xffd700, "🥇"),
        "Platinum": (0x3498db, "💠"), "Diamond": (0x00ced1, "💎"), "Elite": (0x34495e, "🏴"),
        "Champion": (0xe67e22, "🏆"), "Unreal": (0x8e44ad, "🌌")
    },
    "PUBG": {
        "Bronze": (0xcd7f32, "🥉"), "Silver": (0xc0c0c0, "🥈"), "Gold": (0xffd700, "🥇"),
        "Platinum": (0x3498db, "💠"), "Diamond": (0x00ced1, "💎"), "Master": (0x9b59b6, "🟣"),
        "Conqueror": (0xe74c3c, "👑")
    },
    "The Finals": {
        "Bronze": (0xcd7f32, "🥉"), "Silver": (0xc0c0c0, "🥈"), "Gold": (0xffd700, "🥇"),
        "Platinum": (0x3498db, "💠"), "Diamond": (0xe91e63, "💎")
    }
}

# --------------------------------------------------
# 2. OYUNLARA ÖZEL İKONLAR (MENÜ GÖRSELLİĞİ İÇİN)
# --------------------------------------------------
OYUN_SIMGELERI = {
    "League of Legends": {"emoji": "⚔️", "desc": "Sihirdar Vadisi rütbeni belirle"},
    "Valorant": {"emoji": "🎯", "desc": "Radyanit arenası rütbeni belirle"},
    "CS2": {"emoji": "💣", "desc": "C4 kuruldu, rütbeni belirle"},
    "Rainbow Six Siege": {"emoji": "🛡️", "desc": "Taktiksel operasyon rütbeni belirle"},
    "Apex Legends": {"emoji": "🚀", "desc": "Apex Oyunları rütbeni belirle"},
    "Fortnite": {"emoji": "⛏️", "desc": "Savaş Otobüsü rütbeni belirle"},
    "PUBG": {"emoji": "🍳", "desc": "Çorba parası rütbeni belirle"},
    "The Finals": {"emoji": "💰", "desc": "Arena şovmenliği rütbeni belirle"}
}

# --------------------------------------------------
# 3. AŞAMA MENÜSÜ: RÜTBE SEÇİMİ
# --------------------------------------------------
class RutbeSecimMenu(discord.ui.Select):
    def __init__(self, secilen_oyun: str):
        self.secilen_oyun = secilen_oyun
        secenekler = []
        
        for rutbe, detaylar in OYUN_RUTBELERI[secilen_oyun].items():
            emoji = detaylar[1]
            secenekler.append(
                discord.SelectOption(label=rutbe, emoji=emoji, description=f"{secilen_oyun} - {rutbe} rank")
            )
            
        super().__init__(placeholder=f"🎮 Choose your {secilen_oyun} rank...", min_values=1, max_values=1, options=secenekler)

    async def callback(self, interaction: discord.Interaction):
        secilen_rutbe = self.values[0]
        renk_kodu = OYUN_RUTBELERI[self.secilen_oyun][secilen_rutbe][0] 
        emoji = OYUN_RUTBELERI[self.secilen_oyun][secilen_rutbe][1]
        
        rol_adi = f"{self.secilen_oyun} - {secilen_rutbe}"
        guild = interaction.guild
        user = interaction.user

        await interaction.response.defer(ephemeral=True)

        try:
            silinecek_roller = [rol for rol in user.roles if rol.name.startswith(f"{self.secilen_oyun} -")]
            if silinecek_roller:
                await user.remove_roles(*silinecek_roller)

            rol = discord.utils.get(guild.roles, name=rol_adi)

            if not rol:
                rol = await guild.create_role(
                    name=rol_adi, 
                    color=discord.Color(renk_kodu), 
                    hoist=True, 
                    mentionable=True, 
                    reason="Otonom Rank Sistemi tarafından oluşturuldu."
                )
            
            await user.add_roles(rol)
            
            embed = discord.Embed(
                title=f"{emoji} Rank Updated!", 
                description=f"Başarıyla **{rol.mention}** rolüne atandın.", 
                color=discord.Color(renk_kodu)
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

        except discord.Forbidden:
            await interaction.followup.send("❌ **Kritik Hata:** Botun rol yönetme yetkisi yok veya botun kendi rolü oluşturduğu rolden daha aşağıda!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Bir hata oluştu: {e}", ephemeral=True)

# --------------------------------------------------
# 4. AŞAMA MENÜSÜ: OYUN SEÇİMİ (MODERNİZE EDİLDİ)
# --------------------------------------------------
class OyunSecimMenu(discord.ui.Select):
    def __init__(self):
        secenekler = []
        for oyun_adi, detaylar in OYUN_SIMGELERI.items():
            secenekler.append(
                discord.SelectOption(
                    label=oyun_adi, 
                    emoji=detaylar["emoji"], 
                    description=detaylar["desc"]
                )
            )
            
        super().__init__(placeholder="🕹️ Hangi oyunun rütbesini ayarlamak istiyorsun?", min_values=1, max_values=1, options=secenekler)

    async def callback(self, interaction: discord.Interaction):
        secilen_oyun = self.values[0]
        
        view = discord.ui.View()
        view.add_item(RutbeSecimMenu(secilen_oyun))
        
        # Seçilen oyunun emojisini başlığa ekleyelim
        oyun_emojisi = OYUN_SIMGELERI[secilen_oyun]["emoji"]
        await interaction.response.edit_message(content=f"{oyun_emojisi} **{secilen_oyun}** seçildi! Şimdi güncel rütbeni belirt:", view=view)

class RankSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rank", description="Rekabetçi oyunlardaki güncel rütbeni seçip rolünü al.")
    async def rank(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(OyunSecimMenu())
        
        embed = discord.Embed(
            title="🏆 Otonom Rank Sistemi", 
            description="Aşağıdaki menüden oynadığın oyunu seçerek rütbeni alabilirsin.\nSistem rütbe renklerini, özel ikonları ve isimleri otomatik atayacaktır.", 
            color=0x2b2d31 
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(RankSistemi(bot))