import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio

# YETKİLİ ROL ID'LERİ (Güvenlik Duvarı)
YETKILI_ROLLER = [1507777388103205004, 1507777395799621832, 1507777393232969818, 1507777394377756712]

# AYARLANMASI GEREKEN ID'LER
TEMP_VC_OLUSTURUCU_ID = 123456789012345678 # Özel oda oluşturacak ana ses kanalının ID'si
SES_LOG_KANALI_ID = 123456789012345678    # Ses giriş/çıkışlarının yazılacağı log kanalı ID'si

# Veritabanı Dosyaları
WARNS_FILE = "warns.json"
NOTES_FILE = "notes.json"

def dosya_kontrol(dosya_adi):
    if not os.path.exists(dosya_adi):
        with open(dosya_adi, "w") as f:
            json.dump({}, f)

class DynoCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        dosya_kontrol(WARNS_FILE)
        dosya_kontrol(NOTES_FILE)
        self.temp_kanallar = []

    # YARDIMCI GÜVENLİK FONKSİYONU
    def yetki_var_mi(self, user):
        if getattr(user, "roles", None) is None: return False
        return any(rol.id in YETKILI_ROLLER for rol in user.roles)

    # --------------------------------------------------
    # KARANTİNA (LOCKDOWN) - SADECE YETKİLİLER
    # --------------------------------------------------
    @app_commands.command(name="karantina", description="Sunucudaki tüm kanalları mesaj yazımına kapatır (Saldırı Durumu).")
    async def karantina(self, interaction: discord.Interaction):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ **Güvenlik Duvarı:** Yetkiniz yok!", ephemeral=True)
        
        await interaction.response.defer()
        for channel in interaction.guild.text_channels:
            try: 
                await channel.set_permissions(interaction.guild.default_role, send_messages=False)
            except: 
                pass
        await interaction.followup.send("🚨 **KARANTİNA PROTOKOLÜ AKTİF:** Tüm kanallar kilitlendi!")

    # --------------------------------------------------
    # SUNUCU YEDEKLEME - SADECE YETKİLİLER
    # --------------------------------------------------
    @app_commands.command(name="yedek_al", description="Sunucudaki rollerin ve kanalların yapısını JSON olarak yedekler.")
    async def yedek_al(self, interaction: discord.Interaction):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ **Güvenlik Duvarı:** Yetkiniz yok!", ephemeral=True)
        
        backup_data = {"roller": [], "kanallar": []}
        for role in interaction.guild.roles: 
            backup_data["roller"].append({"ad": role.name, "renk": str(role.color)})
        for channel in interaction.guild.channels: 
            backup_data["kanallar"].append({"ad": channel.name, "tip": str(channel.type)})
            
        with open("server_backup.json", "w", encoding="utf-8") as f: 
            json.dump(backup_data, f, indent=4, ensure_ascii=False)
            
        await interaction.response.send_message("✅ Sunucu iskeleti `server_backup.json` dosyasına güvenli bir şekilde yedeklendi.")

    # --------------------------------------------------
    # GEÇİCİ SES KANALLARI VE SES LOGLARI (OTONOM ARKA PLAN)
    # --------------------------------------------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        
        log_kanal = self.bot.get_channel(SES_LOG_KANALI_ID)
        if log_kanal:
            if before.channel is None and after.channel is not None:
                await log_kanal.send(f"🔊 **{member.name}**, `{after.channel.name}` kanalına **katıldı**.")
            elif before.channel is not None and after.channel is None:
                await log_kanal.send(f"🔇 **{member.name}**, `{before.channel.name}` kanalından **ayrıldı**.")

        if after.channel and after.channel.id == TEMP_VC_OLUSTURUCU_ID:
            kategori = after.channel.category
            yeni_kanal = await guild.create_voice_channel(f"🎙️ {member.name}'in Odası", category=kategori)
            await member.move_to(yeni_kanal)
            self.temp_kanallar.append(yeni_kanal.id)

        if before.channel and before.channel.id in self.temp_kanallar:
            if len(before.channel.members) == 0:
                await before.channel.delete()
                self.temp_kanallar.remove(before.channel.id)

    # --------------------------------------------------
    # UYARI (WARN) SİSTEMİ - SADECE YETKİLİLER
    # --------------------------------------------------
    @app_commands.command(name="uyar", description="Bir kullanıcıya resmi uyarı verir.")
    async def uyar(self, interaction: discord.Interaction, kullanici: discord.Member, sebep: str):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ **Güvenlik Duvarı:** Yetkiniz yok!", ephemeral=True)
            
        with open(WARNS_FILE, "r") as f: 
            warns = json.load(f)
        kid = str(kullanici.id)
        if kid not in warns: 
            warns[kid] = []
        warns[kid].append(sebep)
        
        with open(WARNS_FILE, "w") as f: 
            json.dump(warns, f)
        await interaction.response.send_message(f"⚠️ {kullanici.mention} uyarıldı. (Toplam uyarı: {len(warns[kid])}) \nSebep: {sebep}")

    # --------------------------------------------------
    # ADLİ SİCİL NOTLARI - SADECE YETKİLİLER
    # --------------------------------------------------
    @app_commands.command(name="not_ekle", description="Bir kullanıcı hakkında gizli yetkili notu alır.")
    async def not_ekle(self, interaction: discord.Interaction, kullanici: discord.Member, not_metni: str):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ **Güvenlik Duvarı:** Yetkiniz yok!", ephemeral=True)
            
        with open(NOTES_FILE, "r") as f: 
            notes = json.load(f)
        kid = str(kullanici.id)
        if kid not in notes: 
            notes[kid] = []
        notes[kid].append(f"[{interaction.user.name}]: {not_metni}")
        
        with open(NOTES_FILE, "w") as f: 
            json.dump(notes, f)
        await interaction.response.send_message(f"📝 {kullanici.name} adlı kişinin dosyasına not işlendi.", ephemeral=True)

    # --------------------------------------------------
    # OTO-CEVAP SİSTEMİ (OTONOM ARKA PLAN)
    # --------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        
        otomatik_yanitlar = {
            "sa": "Aleyküm selam, hoş geldin!",
            "sea": "Aleyküm selam, hoş geldin!",
            "ip": "Sunucu IP adresimiz: `play.sunucuadi.com`",
            "kurallar": "Lütfen kurallar kanalını incelemeyi unutmayın."
        }
        
        icerik = message.content.lower()
        if icerik in otomatik_yanitlar: 
            await message.reply(otomatik_yanitlar[icerik])

    # --------------------------------------------------
    # HATIRLATICI - SADECE YETKİLİLER
    # --------------------------------------------------
    @app_commands.command(name="hatirlat", description="Belirttiğiniz süre sonunda size mesaj atar.")
    async def hatirlat(self, interaction: discord.Interaction, dakika: int, konu: str):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ **Güvenlik Duvarı:** Yetkiniz yok!", ephemeral=True)
            
        await interaction.response.send_message(f"⏰ Tamamdır! Sana {dakika} dakika sonra `{konu}` konusunu hatırlatacağım.", ephemeral=True)
        await asyncio.sleep(dakika * 60)
        try: 
            await interaction.user.send(f"🔔 **HATIRLATMA:** {konu}")
        except: 
            await interaction.channel.send(f"🔔 {interaction.user.mention}, hatırlatman geldi: **{konu}**")

async def setup(bot):
    await bot.add_cog(DynoCore(bot))