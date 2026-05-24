import discord
from discord.ext import commands, tasks
import asyncio

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category_name = "📊 SUNUCU İSTATİSTİKLERİ"
        self.istatistik_guncelle.start() 

    def cog_unload(self):
        self.istatistik_guncelle.cancel() 

    @commands.hybrid_command(name="istatistik-kur", description="Herkesin görebileceği istatistik kanallarını kurar.")
    @commands.has_permissions(administrator=True) # Komutu SADECE yetkililer kullanabilir
    async def istatistik_kur(self, ctx):
        await ctx.defer()
        guild = ctx.guild

        kategori = discord.utils.get(guild.categories, name=self.category_name)
        if not kategori:
            # AYAR: Herkes GÖRÜR (view_channel=True), kimse BAĞLANAMAZ (connect=False)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True)
            }
            kategori = await guild.create_category(self.category_name, overwrites=overwrites)
        else:
            await ctx.send("⚠️ İstatistik kategorisi zaten mevcut. Sistem arka planda güncelleniyor.")
            return

        await ctx.send("✅ İstatistik kategorisi kuruldu! Herkes kanalları görebilecek ama bağlanamayacak.")
        await self.istatistik_guncelle()

    @commands.hybrid_command(name="istatistik-kaldir", description="İstatistik kategorisini ve kanallarını temizler.")
    @commands.has_permissions(administrator=True) # Komutu SADECE yetkililer kullanabilir
    async def istatistik_kaldir(self, ctx):
        await ctx.defer()
        guild = ctx.guild
        kategori = discord.utils.get(guild.categories, name=self.category_name)
        
        if not kategori:
            return await ctx.send("⚠️ Silinecek bir istatistik kategorisi bulunamadı!")

        for channel in kategori.voice_channels:
            await channel.delete(reason="İstatistik sistemi kapatıldı.")
        
        await kategori.delete(reason="İstatistik sistemi kapatıldı.")
        await ctx.send("🗑️ İstatistik sistemi başarıyla kaldırıldı!")

    @tasks.loop(minutes=10)
    async def istatistik_guncelle(self):
        await self.bot.wait_until_ready()
        
        for guild in self.bot.guilds:
            try:
                kategori = discord.utils.get(guild.categories, name=self.category_name)
                if not kategori:
                    continue 

                toplam = guild.member_count
                insanlar = len([m for m in guild.members if not m.bot])
                botlar = len([m for m in guild.members if m.bot])
                boosts = guild.premium_subscription_count

                stats_data = {
                    "👥": f"👥 Toplam Üye: {toplam}",
                    "👤": f"👤 İnsanlar: {insanlar}",
                    "🤖": f"🤖 Botlar: {botlar}",
                    "🚀": f"🚀 Takviyeler: {boosts}"
                }

                # AYAR: Kendi kendini tamir ederken de Herkes GÖRÜR, kimse BAĞLANAMAZ
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True)
                }

                for emoji, new_name in stats_data.items():
                    kanal_bulundu = False
                    
                    for vc in kategori.voice_channels:
                        if emoji in vc.name:
                            kanal_bulundu = True
                            if vc.name != new_name:
                                try:
                                    await vc.edit(name=new_name)
                                    await asyncio.sleep(1.5) 
                                except Exception as e:
                                    print(f"Kanal güncellenemedi ({guild.name}): {e}")
                            break
                    
                    if not kanal_bulundu:
                        try:
                            await guild.create_voice_channel(new_name, category=kategori, overwrites=overwrites)
                            await asyncio.sleep(1.5)
                        except Exception as e:
                            print(f"Eksik kanal oluşturulamadı ({guild.name}): {e}")

            except Exception as e:
                print(f"İstatistik genel hatası ({guild.name}): {e}")

async def setup(bot):
    await bot.add_cog(ServerStats(bot))