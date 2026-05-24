import discord
from discord.ext import commands
import json
import os
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1507891861631533106
        self.file_path = "warns.json"
        
    async def log_action(self, guild, title, user, moderator, reason, color):
        log_channel = guild.get_channel(self.log_channel_id)
        if log_channel:
            embed = discord.Embed(title=title, color=color, timestamp=discord.utils.utcnow())
            embed.add_field(name="Kullanıcı", value=f"{user.mention} ({user.id})", inline=False)
            embed.add_field(name="Yetkili", value=moderator.mention, inline=False)
            embed.add_field(name="Sebep", value=f"`{reason}`", inline=False)
            embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
            await log_channel.send(embed=embed)

    # --- UYARI VE SİCİL SİSTEMİ ---
    def load_warns(self):
        if not os.path.exists(self.file_path): return {}
        with open(self.file_path, "r", encoding="utf-8") as f: return json.load(f)

    def save_warns(self, data):
        with open(self.file_path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

    @commands.hybrid_command(name="uyar", description="Kullanıcıyı uyarır.")
    @commands.has_permissions(manage_messages=True)
    async def uyar(self, ctx, kullanici: discord.Member, *, sebep: str):
        warns = self.load_warns()
        guild_id, user_id = str(ctx.guild.id), str(kullanici.id)
        if guild_id not in warns: warns[guild_id] = {}
        if user_id not in warns[guild_id]: warns[guild_id][user_id] = []
        
        warns[guild_id][user_id].append({"sebep": sebep, "yetkili": ctx.author.name})
        self.save_warns(warns)
        await ctx.send(f"⚠️ {kullanici.mention} başarıyla uyarıldı. Sebep: {sebep}")
        await self.log_action(ctx.guild, "⚠️ Kullanıcı Uyarıldı", kullanici, ctx.author, sebep, discord.Color.yellow())

    @commands.hybrid_command(name="sicil", description="Geçmiş uyarıları gösterir.")
    async def sicil(self, ctx, kullanici: discord.Member):
        warns = self.load_warns()
        guild_id, user_id = str(ctx.guild.id), str(kullanici.id)
        if guild_id not in warns or user_id not in warns[guild_id] or not warns[guild_id][user_id]:
            return await ctx.send(f"✅ {kullanici.mention} temiz bir sicile sahip!")
            
        embed = discord.Embed(title=f"📋 Sicil: {kullanici.name}", color=discord.Color.blue())
        for i, w in enumerate(warns[guild_id][user_id], 1):
            embed.add_field(name=f"Uyarı #{i}", value=f"Sebep: {w['sebep']} | Yetkili: {w['yetkili']}", inline=False)
        await ctx.send(embed=embed)

    # --- TIMEOUT (SUSTURMA) ---
    @commands.hybrid_command(name="sustur", description="Kullanıcıya Timeout atar.")
    @commands.has_permissions(moderate_members=True)
    async def sustur(self, ctx, kullanici: discord.Member, dakika: int, *, sebep: str = "Belirtilmedi"):
        sure = datetime.timedelta(minutes=dakika)
        await kullanici.timeout(sure, reason=sebep)
        await ctx.send(f"🔇 {kullanici.mention} {dakika} dakika boyunca susturuldu!")
        await self.log_action(ctx.guild, "🔇 Timeout Atıldı", kullanici, ctx.author, f"{dakika} Dakika - {sebep}", discord.Color.orange())

    # --- BAN & KICK ---
    @commands.hybrid_command(name="ban", description="Kullanıcıyı sunucudan yasaklar.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, kullanici: discord.Member, *, sebep: str = "Belirtilmedi"):
        await kullanici.ban(reason=sebep)
        await ctx.send(f"🔨 {kullanici.mention} sunucudan yasaklandı!")
        await self.log_action(ctx.guild, "🔨 Kullanıcı Banlandı", kullanici, ctx.author, sebep, discord.Color.red())

    @commands.hybrid_command(name="sil", description="Belirtilen sayıda mesajı siler.")
    @commands.has_permissions(manage_messages=True)
    async def sil(self, ctx, miktar: int):
        silinen = await ctx.channel.purge(limit=miktar + 1)
        await ctx.send(f"🧹 {len(silinen)-1} mesaj başarıyla silindi!", delete_after=5)

async def setup(bot):
    await bot.add_cog(Moderation(bot))