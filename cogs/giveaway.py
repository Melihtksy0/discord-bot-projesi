import discord
from discord.ext import commands
import asyncio
import random

# Çekiliş için modern "Katıl" butonu arayüzü
class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.participants = set() # Katılımcıları tutacağımız küme (aynı kişi 2 kez katılamaz)

    @discord.ui.button(label="🎉 Çekilişe Katıl", style=discord.ButtonStyle.success, custom_id="gw_join")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.participants:
            await interaction.response.send_message("Hali hazırda bu çekilişe katıldın! Bol şans 🍀", ephemeral=True)
        else:
            self.participants.add(interaction.user.id)
            await interaction.response.send_message("Çekilişe başarıyla katıldın!", ephemeral=True)

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="çekiliş-başlat", description="Butonlu, gelişmiş bir çekiliş başlatır.")
    async def cekilis_baslat(self, ctx, odul: str, sure_saniye: int, kazanan_sayisi: int = 1):
        # Sadece yetkililer başlatabilsin
        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.send("Bu komutu kullanmak için yetkin yok!", ephemeral=True)

        view = GiveawayView()
        
        embed = discord.Embed(
            title="🎁 YENİ ÇEKİLİŞ!",
            description=f"**Ödül:** {odul}\n**Süre:** {sure_saniye} Saniye\n**Kazanacak Kişi Sayısı:** {kazanan_sayisi}\n\n*Aşağıdaki butona tıklayarak çekilişe katılabilirsiniz!*",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Başlatan: {ctx.author.name}")
        
        # Çekiliş mesajını gönder
        msg = await ctx.send(embed=embed, view=view)
        
        # Belirlenen süre kadar bekle
        await asyncio.sleep(sure_saniye)
        
        # Süre bittiğinde yapılacaklar
        if len(view.participants) == 0:
            await ctx.send(f"😢 Kimse katılmadığı için **{odul}** çekilişi iptal edildi.")
        else:
            # Kazananları rastgele seç
            winners = random.sample(list(view.participants), min(len(view.participants), kazanan_sayisi))
            winners_mentions = ", ".join(f"<@{w}>" for w in winners)
            
            win_embed = discord.Embed(
                title="🎉 ÇEKİLİŞ SONUÇLANDI!",
                description=f"**Ödül:** {odul}\n**Kazanan(lar):** {winners_mentions}",
                color=discord.Color.green()
            )
            await ctx.send(content=f"Tebrikler {winners_mentions}! **{odul}** kazandınız!", embed=win_embed)
        
        # Süre bitince butonu devre dışı bırak
        for child in view.children:
            child.disabled = True
        await msg.edit(view=view)

async def setup(bot):
    await bot.add_cog(Giveaway(bot))