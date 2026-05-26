import discord
from discord.ext import commands

class Genel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}
        self.son_mesajlar = {} # Kullanıcıların son mesajlarını geçici olarak tutar

    # --- MESAJ TAKİP VE AFK DİNLEYİCİSİ ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return

        # 1. Son Aktiviteyi Kaydet (Bilgi komutu için)
        self.son_mesajlar[message.author.id] = {
            "icerik": message.content[:60] + "..." if len(message.content) > 60 else message.content,
            "kanal": message.channel.mention,
            "link": message.jump_url,
            "zaman": int(message.created_at.timestamp())
        }

        # 2. AFK Modundan Çıkış
        if message.author.id in self.afk_users:
            del self.afk_users[message.author.id]
            try:
                await message.channel.send(f"👋 {message.author.mention} AFK modundan döndü!", delete_after=5)
            except:
                pass

        # 3. AFK Olanı Etiketleyenlere Uyarı
        for mention in message.mentions:
            if mention.id in self.afk_users:
                sebep = self.afk_users[mention.id]
                try:
                    await message.channel.send(f"💤 {mention.display_name} şu an AFK. Sebep: **{sebep}**", delete_after=5)
                except:
                    pass

    # --- MODERN SOSYAL MEDYA ---
    @commands.hybrid_command(name="sosyal", description="Sosyal medya bağlantılarımızı gösterir.")
    async def sosyal(self, ctx):
        embed = discord.Embed(title="🔗 Sosyal Medya Bağlantıları", color=discord.Color.from_rgb(43, 45, 49))
        embed.description = """
🟩 **Kick**
[https://kick.com/yusha99](https://kick.com/yusha99) **[BURDAYIZ]**

📸 **Instagram**
[https://www.instagram.com/21yusha1999/?hl=tr](https://www.instagram.com/21yusha1999/?hl=tr)

▶️ **Youtube**
[https://www.youtube.com/@yusha1999](https://www.youtube.com/@yusha1999)
"""
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Kick", url="https://kick.com/yusha99", emoji="🟩", style=discord.ButtonStyle.link))
        view.add_item(discord.ui.Button(label="Instagram", url="https://www.instagram.com/21yusha1999/?hl=tr", emoji="📸", style=discord.ButtonStyle.link))
        view.add_item(discord.ui.Button(label="YouTube", url="https://www.youtube.com/@yusha1999", emoji="▶️", style=discord.ButtonStyle.link))
        await ctx.send(embed=embed, view=view)

    # --- AVATAR ---
    @commands.hybrid_command(name="avatar", description="Kullanıcının profil fotoğrafını gösterir.")
    async def avatar(self, ctx, kullanici: discord.Member = None):
        kullanici = kullanici or ctx.author
        embed = discord.Embed(title=f"🖼️ {kullanici.display_name} Avatarı", color=discord.Color.blue())
        if kullanici.display_avatar:
            embed.set_image(url=kullanici.display_avatar.url)
        else:
            embed.description = "Bu kullanıcının bir profil fotoğrafı yok."
        await ctx.send(embed=embed)

    # --- MEVCUT ---
    @commands.hybrid_command(name="mevcut", description="Sunucunun anlık üye durumunu gösterir.")
    async def mevcut(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"📊 {guild.name} Sunucu Mevcudu", color=discord.Color.green())
        embed.add_field(name="👥 Toplam Üye", value=str(guild.member_count), inline=True)
        insanlar = len([m for m in guild.members if not m.bot])
        botlar = len([m for m in guild.members if m.bot])
        embed.add_field(name="👤 İnsanlar", value=str(insanlar), inline=True)
        embed.add_field(name="🤖 Botlar", value=str(botlar), inline=True)
        await ctx.send(embed=embed)

    # --- AFK SİSTEMİ ---
    @commands.hybrid_command(name="afk", description="AFK (Bilgisayar Başında Değil) moduna geçersiniz.")
    async def afk(self, ctx, *, sebep: str = "Belirtilmedi"):
        self.afk_users[ctx.author.id] = sebep
        await ctx.send(f"✅ {ctx.author.mention} artık AFK. Sebep: **{sebep}**")

    # --- BİLGİ (KULLANICI ANALİZ PANELİ) ---
    @commands.hybrid_command(name="bilgi", description="Bir kullanıcının detaylı profilini ve son aktivitesini gösterir.")
    async def bilgi(self, ctx, kullanici: discord.Member = None):
        kullanici = kullanici or ctx.author
        
        # Aktiflik Çevirici
        durum_sozlugu = {
            discord.Status.online: "🟢 Çevrimiçi",
            discord.Status.idle: "🌙 Boşta",
            discord.Status.dnd: "🔴 Rahatsız Etmeyin",
            discord.Status.offline: "⚫ Çevrimdışı / Gizli"
        }
        durum = durum_sozlugu.get(kullanici.status, "⚫ Çevrimdışı / Gizli")

        # Roller
        roller = [role.mention for role in reversed(kullanici.roles) if role != ctx.guild.default_role]
        en_yuksek_rol = kullanici.top_role.mention if roller else "Rolü Yok"
        rol_listesi = " ".join(roller[:5]) + ("..." if len(roller) > 5 else "") if roller else "Yok"

        embed = discord.Embed(
            title=f"🔍 Profil Analizi: {kullanici.display_name}",
            color=kullanici.color if kullanici.color != discord.Color.default() else discord.Color.blurple()
        )
        if kullanici.display_avatar:
            embed.set_thumbnail(url=kullanici.display_avatar.url)

        # Yan Yana Temel Veriler
        embed.add_field(name="🆔 Kullanıcı ID", value=f"`{kullanici.id}`", inline=True)
        embed.add_field(name="🤖 Hesap Tipi", value="Bot" if kullanici.bot else "Gerçek Kullanıcı", inline=True)
        embed.add_field(name="⚡ Aktiflik Durumu", value=durum, inline=True)

        # Discord Dinamik Saat Yapısı ile Tarihler
        olusturma = int(kullanici.created_at.timestamp())
        katilim = int(kullanici.joined_at.timestamp())
        
        embed.add_field(name="📆 Hesap Kurulumu", value=f"<t:{olusturma}:D>\n(<t:{olusturma}:R>)", inline=True)
        embed.add_field(name="📥 Sunucuya Katılım", value=f"<t:{katilim}:D>\n(<t:{katilim}:R>)", inline=True)
        
        # Yetkiler
        embed.add_field(name="🛡️ En Yüksek Yetki", value=en_yuksek_rol, inline=False)
        if roller:
            embed.add_field(name=f"🎭 Sahip Olduğu Roller ({len(roller)})", value=rol_listesi, inline=False)

        # Son Aktivite Takibi
        son_mesaj = self.son_mesajlar.get(kullanici.id)
        if son_mesaj:
            mesaj_detayi = (
                f"**Kanal:** {son_mesaj['kanal']} (<t:{son_mesaj['zaman']}:R>)\n"
                f"**Mesaj:** `{son_mesaj['icerik']}`\n"
                f"🔗 **[Mesaja Gitmek İçin Tıkla]({son_mesaj['link']})**"
            )
            embed.add_field(name="📝 Son Aktivitesi", value=mesaj_detayi, inline=False)
        else:
            embed.add_field(name="📝 Son Aktivitesi", value="Bot yeniden başlatıldığından beri sistemimizde bir aktivitesi yok.", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Genel(bot))