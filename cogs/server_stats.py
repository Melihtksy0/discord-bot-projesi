import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os

STATS_FILE = "stats_config.json"
YETKILI_ROLLER = [1507777388103205004, 1507777395799621832, 1507777393232969818, 1507777394377756712]

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stat_guncelleme_dongusu.start() # Bot açılır açılmaz güncelleme motorunu başlatır

    def cog_unload(self):
        self.stat_guncelleme_dongusu.cancel()

    def yetki_var_mi(self, user):
        if getattr(user, "roles", None) is None: return False
        return any(rol.id in YETKILI_ROLLER for rol in user.roles)

    # PANOLARI OTOMATİK KURAN KOMUT
    @app_commands.command(name="stat_kur", description="Dinamik sunucu istatistik panosunu otonom olarak kurar.")
    async def stat_kur(self, interaction: discord.Interaction):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ **Güvenlik Duvarı:** Yetkiniz yok!", ephemeral=True)
            
        await interaction.response.defer()
        guild = interaction.guild
        
        # Kategori oluştur
        kategori = await guild.create_category("📊 SUNUCU İSTATİSTİKLERİ")
        
        # Ses kanallarına üyelerin girmesini engellemek için izin kilitleri
        overwrites = {guild.default_role: discord.PermissionOverwrite(connect=False)}
        
        ch_toplam = await guild.create_voice_channel(f"👥 Toplam Üye: {guild.member_count}", category=kategori, overwrites=overwrites)
        
        cevrimici = sum(1 for m in guild.members if m.status != discord.Status.offline and not m.bot)
        ch_aktif = await guild.create_voice_channel(f"🟢 Çevrimiçi: {cevrimici}", category=kategori, overwrites=overwrites)
        
        botlar = sum(1 for m in guild.members if m.bot)
        ch_bot = await guild.create_voice_channel(f"🤖 Botlar: {botlar}", category=kategori, overwrites=overwrites)
        
        # Kanal ID'lerini sisteme kaydet
        config = {
            "toplam_kanal_id": ch_toplam.id,
            "aktif_kanal_id": ch_aktif.id,
            "bot_kanal_id": ch_bot.id
        }
        with open(STATS_FILE, "w") as f:
            json.dump(config, f)
            
        await interaction.followup.send("✅ Dinamik İstatistik Panosu başarıyla kuruldu! Veriler her 10 dakikada bir otomatik güncellenecektir.")

    # ARKA PLANDA ÇALIŞAN OTOMASYON MOTORU
    @tasks.loop(minutes=10)
    async def stat_guncelleme_dongusu(self):
        if not os.path.exists(STATS_FILE): return
        
        try:
            with open(STATS_FILE, "r") as f:
                config = json.load(f)
        except:
            return

        for guild in self.bot.guilds:
            try:
                ch_toplam = guild.get_channel(config.get("toplam_kanal_id"))
                ch_aktif = guild.get_channel(config.get("aktif_kanal_id"))
                ch_bot = guild.get_channel(config.get("bot_kanal_id"))

                if ch_toplam: await ch_toplam.edit(name=f"👥 Toplam Üye: {guild.member_count}")
                
                cevrimici = sum(1 for m in guild.members if m.status != discord.Status.offline and not m.bot)
                if ch_aktif: await ch_aktif.edit(name=f"🟢 Çevrimiçi: {cevrimici}")
                
                botlar = sum(1 for m in guild.members if m.bot)
                if ch_bot: await ch_bot.edit(name=f"🤖 Botlar: {botlar}")
            except Exception as e:
                print(f"Stat güncelleme uyarısı: {e}")

    @stat_guncelleme_dongusu.before_loop
    async def before_stat_guncelleme(self):
        await self.bot.wait_until_ready() # Bot tam açılmadan motoru çalıştırma

async def setup(bot):
    await bot.add_cog(ServerStats(bot))