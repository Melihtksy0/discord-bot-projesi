import discord
from discord.ext import commands
import json
import os
import datetime

# --- GERİ ALMA BUTONU PANELI ---
class RevertView(discord.ui.View):
    def __init__(self, action_type, target_user):
        super().__init__(timeout=86400) 
        self.action_type = action_type
        self.target_user = target_user

    @discord.ui.button(label="İşlemi Geri Al", style=discord.ButtonStyle.danger, emoji="↩️")
    async def revert_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.moderate_members:
            return await interaction.response.send_message("⚠️ Bu işlemi geri almak için yetkiniz yok!", ephemeral=True)

        guild = interaction.guild
        
        try:
            if self.action_type == "timeout":
                member = guild.get_member(self.target_user.id)
                if member:
                    await member.timeout(None, reason=f"Ceza {interaction.user.name} tarafından geri alındı.")
            elif self.action_type == "ban":
                user = await interaction.client.fetch_user(self.target_user.id)
                await guild.unban(user, reason=f"Ban {interaction.user.name} tarafından kaldırıldı.")
        except Exception as e:
            return await interaction.response.send_message(f"Hata: İşlem geri alınamadı ({e})", ephemeral=True)

        button.disabled = True
        button.style = discord.ButtonStyle.success
        button.label = f"Geri Alındı ({interaction.user.name})"
        
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.add_field(name="♻️ İŞLEM İPTAL EDİLDİ", value=f"Bu ceza {interaction.user.mention} tarafından geri alındı.", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)


# --- ANA MODERASYON SINIFI ---
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1507891861631533106
        self.file_path = "warns.json"
        
    async def log_action(self, guild, title, user, moderator, reason, color, action_type=None):
        log_channel = guild.get_channel(self.log_channel_id)
        if not log_channel: return

        embed = discord.Embed(title=title, color=color, timestamp=discord.utils.utcnow())
        embed.add_field(name="Kullanıcı", value=f"{user.mention} ({user.id})", inline=True)
        embed.add_field(name="İşlemi Yapan", value=moderator.mention, inline=True)
        embed.add_field(name="Belirtilen Sebep", value=f"`{reason}`", inline=False)
        
        if user.display_avatar:
            embed.set_thumbnail(url=user.display_avatar.url)

        view = None
        if action_type in ["timeout", "ban"]:
            view = RevertView(action_type, user)

        if view:
            await log_channel.send(embed=embed, view=view)
        else:
            await log_channel.send(embed=embed)

    # --- UYARI VE SİCİL SİSTEMİ (MODERNİZE EDİLDİ) ---
    def load_warns(self):
        if not os.path.exists(self.file_path): return {}
        with open(self.file_path, "r", encoding="utf-8") as f: return json.load(f)

    def save_warns(self, data):
        with open(self.file_path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

    @commands.hybrid_command(name="uyar", description="Kullanıcıya ağırlıklı (çarpanlı) uyarı verir.")
    @commands.has_permissions(manage_messages=True)
    async def uyar(self, ctx, kullanici: discord.Member, carpan: int = 1, *, sebep: str = "Belirtilmedi"):
        """carpan (int): Uyarının şiddeti (Örn: 1 basit, 3 ağır)"""
        warns = self.load_warns()
        guild_id, user_id = str(ctx.guild.id), str(kullanici.id)
        
        if guild_id not in warns: warns[guild_id] = {}
        if user_id not in warns[guild_id]: warns[guild_id][user_id] = []
        
        # Yeni uyarı kaydına çarpan ve tarih ekleniyor
        yeni_uyari = {
            "sebep": sebep, 
            "yetkili": ctx.author.name,
            "carpan": carpan,
            "tarih": discord.utils.utcnow().strftime("%d/%m/%Y")
        }
        
        warns[guild_id][user_id].append(yeni_uyari)
        self.save_warns(warns)
        
        # Toplam risk puanı hesaplanıyor (eski kayıtlar 1 çarpan kabul edilir)
        toplam_puan = sum(w.get("carpan", 1) for w in warns[guild_id][user_id])
        
        embed = discord.Embed(
            title="⚠️ Kullanıcı Uyarıldı",
            description=f"{kullanici.mention} kullanıcısına **{carpan}x** şiddetinde uyarı eklendi!",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Sebep", value=f"`{sebep}`", inline=False)
        embed.add_field(name="İşlemi Yapan", value=ctx.author.mention, inline=True)
        embed.add_field(name="Güncel Uyarı Puanı", value=f"**{toplam_puan}**", inline=True)
        
        await ctx.send(embed=embed)
        await self.log_action(ctx.guild, f"⚠️ {carpan}x Uyarı Verildi", kullanici, ctx.author, sebep, discord.Color.yellow())

    @commands.hybrid_command(name="sicil", description="Kullanıcının sicil kaydını ve toplam risk puanını gösterir.")
    @commands.has_permissions(manage_messages=True)
    async def sicil(self, ctx, kullanici: discord.Member):
        warns = self.load_warns()
        guild_id, user_id = str(ctx.guild.id), str(kullanici.id)
        
        if guild_id not in warns or user_id not in warns[guild_id] or not warns[guild_id][user_id]:
            embed = discord.Embed(
                title=f"🛡️ Temiz Sicil: {kullanici.name}",
                description="Bu kullanıcının geçmişinde herhangi bir uyarı kaydı bulunmuyor.",
                color=discord.Color.green()
            )
            return await ctx.send(embed=embed)
            
        kullanici_sicili = warns[guild_id][user_id]
        toplam_puan = sum(w.get("carpan", 1) for w in kullanici_sicili)
        
        # Risk seviyesine göre renk belirleme
        if toplam_puan < 3:
            renk = discord.Color.gold()
        elif toplam_puan < 6:
            renk = discord.Color.orange()
        else:
            renk = discord.Color.dark_red()

        embed = discord.Embed(
            title=f"📋 Sicil Dosyası: {kullanici.name}",
            description=f"**Toplam Uyarı Puanı:** `{toplam_puan}`\nKayıtlı İhlaller Aşağıda Listelenmiştir:",
            color=renk
        )
        
        # En yeni uyarı en üstte çıkması için listeyi ters çeviriyoruz
        for i, w in enumerate(reversed(kullanici_sicili), 1):
            siddet = w.get("carpan", 1)
            tarih = w.get("tarih", "Eski Kayıt")
            
            # Göz yormayan şık liste tasarımı
            detay = f"> **Şiddet:** `{siddet}x`\n> **Yetkili:** {w['yetkili']}\n> **Tarih:** {tarih}"
            embed.add_field(name=f"İhlal: {w['sebep']}", value=detay, inline=False)
            
            # Embed sınırını aşmamak için en fazla son 10 uyarıyı göster
            if i >= 10:
                embed.set_footer(text="Sadece son 10 uyarı gösterilmektedir.")
                break
                
        await ctx.send(embed=embed)

    # --- TIMEOUT VE BAN ---
    @commands.hybrid_command(name="sustur", description="Kullanıcıya Timeout atar.")
    @commands.has_permissions(moderate_members=True)
    async def sustur(self, ctx, kullanici: discord.Member, dakika: int, *, sebep: str = "Belirtilmedi"):
        sure = datetime.timedelta(minutes=dakika)
        await kullanici.timeout(sure, reason=sebep)
        await ctx.send(f"🔇 {kullanici.mention} {dakika} dakika boyunca susturuldu!")
        await self.log_action(ctx.guild, "🔇 Timeout Atıldı", kullanici, ctx.author, f"{dakika} Dakika - {sebep}", discord.Color.orange(), action_type="timeout")

    @commands.hybrid_command(name="ban", description="Kullanıcıyı sunucudan yasaklar.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, kullanici: discord.Member, *, sebep: str = "Belirtilmedi"):
        await kullanici.ban(reason=sebep)
        await ctx.send(f"🔨 {kullanici.mention} sunucudan yasaklandı!")
        await self.log_action(ctx.guild, "🔨 Kullanıcı Banlandı", kullanici, ctx.author, sebep, discord.Color.red(), action_type="ban")

    @commands.hybrid_command(name="sil", description="Belirtilen sayıda mesajı siler.")
    @commands.has_permissions(manage_messages=True)
    async def sil(self, ctx, miktar: int):
        silinen = await ctx.channel.purge(limit=miktar + 1)
        await ctx.send(f"🧹 {len(silinen)-1} mesaj başarıyla silindi!", delete_after=5)

async def setup(bot):
    await bot.add_cog(Moderation(bot))