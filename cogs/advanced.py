import discord
from discord.ext import commands
from discord import app_commands
import re

# YETKİLİ ROL ID'LERİ (Sadece bu rollere sahip olanlar komutları tetikleyebilir)
YETKILI_ROLLER = [1507777388103205004, 1507777395799621832, 1507777393232969818, 1507777394377756712]

class Advanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Yardımcı Güvenlik Fonksiyonu
    def yetki_var_mi(self, user):
        if getattr(user, "roles", None) is None: return False
        return any(rol.id in YETKILI_ROLLER for rol in user.roles)

    # --------------------------------------------------
    # MEVCUT KOMUTU
    # --------------------------------------------------
    @app_commands.command(name="mevcut", description="Sunucudaki üyelerin ve rollerin detaylı aktiflik durumunu gösterir.")
    async def mevcut(self, interaction: discord.Interaction):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ **Güvenlik Duvarı:** Bu komutu kullanmaya yetkiniz yok!", ephemeral=True)
            
        guild = interaction.guild
        toplam_uye = guild.member_count
        cevrimici = sum(1 for m in guild.members if m.status != discord.Status.offline and not m.bot)
        cevrimdisi = sum(1 for m in guild.members if m.status == discord.Status.offline and not m.bot)
        botlar = sum(1 for m in guild.members if m.bot)

        embed = discord.Embed(title=f"📊 {guild.name} - Sunucu İstatistikleri", color=discord.Color.brand_green())
        embed.add_field(name="👥 Toplam Üye", value=f"**{toplam_uye}**", inline=False)
        embed.add_field(name="🟢 Çevrimiçi", value=f"{cevrimici}", inline=True)
        embed.add_field(name="⚫ Çevrimdışı", value=f"{cevrimdisi}", inline=True)
        embed.add_field(name="🤖 Bot Sayısı", value=f"{botlar}", inline=True)
        
        await interaction.response.send_message(embed=embed)

    # --------------------------------------------------
    # KİLİTLE KOMUTU
    # --------------------------------------------------
    @app_commands.command(name="kilitle", description="Bulunulan kanalı üyelerin mesaj yazmasına kapatır.")
    async def kilitle(self, interaction: discord.Interaction):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ Yetkiniz yok!", ephemeral=True)
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 **Bu kanal yetkililer tarafından kilitlenmiştir.**")

    # --------------------------------------------------
    # KİLİT AÇ KOMUTU
    # --------------------------------------------------
    @app_commands.command(name="kilit_ac", description="Kilitli kanalı tekrar mesaj yazımına açar.")
    async def kilit_ac(self, interaction: discord.Interaction):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ Yetkiniz yok!", ephemeral=True)
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
        await interaction.response.send_message("🔓 **Kanal kilidi açıldı.**")

    # --------------------------------------------------
    # YAVAŞ MOD KOMUTU
    # --------------------------------------------------
    @app_commands.command(name="yavasmod", description="Kanala yavaş mod ekler.")
    async def yavasmod(self, interaction: discord.Interaction, saniye: int):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ Yetkiniz yok!", ephemeral=True)
        await interaction.channel.edit(slowmode_delay=saniye)
        await interaction.response.send_message(f"✅ Yavaş mod güncellendi: {saniye} saniye.")

    # --------------------------------------------------
    # GELİŞMİŞ DETAYLI BİLGİ KOMUTU
    # --------------------------------------------------
    @app_commands.command(name="bilgi", description="Bir kullanıcının detaylı hesap, yaş (eskilik) ve sunucu geçmişini analiz eder.")
    @app_commands.describe(kullanici="Hakkında bilgi almak istediğiniz kullanıcı")
    async def bilgi(self, interaction: discord.Interaction, kullanici: discord.Member = None):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ Yetkiniz yok!", ephemeral=True)
        
        # Eğer kullanıcı girilmediyse komutu yazan kişiyi hedef alır
        kullanici = kullanici or interaction.user
        
        # Hassas Zaman Hesaplamaları (Delta Zaman Analizi)
        simdi = discord.utils.utcnow()
        hesap_yasi_gun = (simdi - kullanici.created_at).days
        sunucu_yasi_gun = (simdi - kullanici.joined_at).days if kullanici.joined_at else 0
        
        # Discord Dinamik Zaman Etiketleri (Kullanıcının kendi bilgisayar saatine göre otomatik dönüsür)
        olusturma_tarihi = f"<t:{int(kullanici.created_at.timestamp())}:F> (<t:{int(kullanici.created_at.timestamp())}:R>)"
        katilma_tarihi = f"<t:{int(kullanici.joined_at.timestamp())}:F> (<t:{int(kullanici.joined_at.timestamp())}:R>)" if kullanici.joined_at else "Bilinmiyor"
        
        # Şık Arayüz Tasarımı (Embed)
        embed = discord.Embed(title=f"🔍 Detaylı Kullanıcı Profili: {kullanici.name}", color=kullanici.color)
        embed.set_thumbnail(url=kullanici.display_avatar.url)
        
        # Kimlik Bilgileri
        embed.add_field(name="🆔 Kullanıcı ID", value=f"`{kullanici.id}`", inline=False)
        
        # Yaş ve Zaman Analizleri (İstediğin Detaylar)
        embed.add_field(name="📅 Hesap Oluşturulma Zamanı", value=olusturma_tarihi, inline=False)
        embed.add_field(name="⏳ Hesap Yaşı (Eskilik Skoru)", value=f"**{hesap_yasi_gun} gündür** Discord üyesi.", inline=True)
        
        embed.add_field(name="📥 Sunucuya Giriş Zamanı", value=katilma_tarihi, inline=False)
        embed.add_field(name="⏱️ Sunucu Üyelik Süresi", value=f"**{sunucu_yasi_gun} gündür** bu sunucuda bulunuyor.", inline=True)
        
        # Durum ve Aktiflik Analizi
        durum_haritasi = {
            discord.Status.online: "🟢 Çevrimiçi (Online)",
            discord.Status.idle: "🟡 Boşta (Idle)",
            discord.Status.dnd: "🔴 Rahatsız Etmeyin (Do Not Disturb)",
            discord.Status.offline: "⚫ Çevrimdışı / Gizli (Offline)"
        }
        aktiflik = durum_haritasi.get(kullanici.status, "⚫ Bilinmiyor")
        embed.add_field(name="⚡ Aktiflik Durumu", value=aktiflik, inline=True)
        
        # Hesap Tipi ve Rol Hiyerarşisi
        embed.add_field(name="🤖 Hesap Tipi", value="Bot / Otomasyon" if kullanici.bot else "Gerçek Kullanıcı", inline=True)
        embed.add_field(name="🎖️ En Yüksek Yetki Rolü", value=kullanici.top_role.mention, inline=True)
        
        # Sahip Olduğu Roller Listesi (everyone rolünü gizleyerek temiz liste sunar)
        roller = [rol.mention for rol in kullanici.roles if rol.name != "@everyone"]
        roller_metni = " ".join(roller) if roller else "Herhangi bir role sahip değil."
        embed.add_field(name="📜 Sunucu Rolleri Listesi", value=roller_metni, inline=False)
        
        embed.set_footer(text="Gelişmiş Denetim ve Kimlik Doğrulama Sistemi", icon_url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Advanced(bot))