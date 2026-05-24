import discord
from discord.ext import commands
from discord import app_commands
import random

YETKILI_ROLLER = [1507777388103205004, 1507777395799621832, 1507777393232969818, 1507777394377756712]

# --------------------------------------------------
# ÇEKİLİŞ BUTONU ARAYÜZÜ
# --------------------------------------------------
class CekilisButton(discord.ui.View):
    def __init__(self, rol_id: int):
        super().__init__(timeout=None)
        self.rol_id = rol_id

    @discord.ui.button(label="Çekilişe Katıl", style=discord.ButtonStyle.success, emoji="🎉")
    async def katil(self, interaction: discord.Interaction, button: discord.ui.Button):
        rol = interaction.guild.get_role(self.rol_id)
        if not rol:
            return await interaction.response.send_message("❌ Çekiliş rolü silinmiş veya bulunamıyor!", ephemeral=True)
            
        if rol in interaction.user.roles:
            await interaction.response.send_message("👀 Zaten çekilişe katılmışsın! Beklemede kal.", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(rol)
                await interaction.response.send_message(f"✅ Çekilişe başarıyla katıldın! **{rol.name}** rolü sana verildi. Bol şans!", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Kritik Hata: Botun rol verme yetkisi yok.", ephemeral=True)

# --------------------------------------------------
# ÇEKİLİŞ ANA MODÜLÜ
# --------------------------------------------------
class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def yetki_var_mi(self, user):
        if getattr(user, "roles", None) is None: return False
        return any(rol.id in YETKILI_ROLLER for rol in user.roles)

    @app_commands.command(name="cekilis_kur", description="Otonom rol oluşturan çekiliş başlatır.")
    @app_commands.describe(odul="Kazanana ne verilecek?", rol_adi="Oluşturulacak çekiliş rolünün adı ne olsun? (Örn: yemek-cekilisi)")
    async def cekilis_kur(self, interaction: discord.Interaction, odul: str, rol_adi: str):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ **Güvenlik Duvarı:** Yetkiniz yok!", ephemeral=True)
            
        await interaction.response.defer(ephemeral=True) # Rol oluşturma sürebileceği için defer atıyoruz
        
        guild = interaction.guild
        # 1. Rol zaten var mı diye kontrol et
        rol = discord.utils.get(guild.roles, name=rol_adi)
        
        # 2. Rol yoksa OTONOM olarak sıfırdan oluştur
        if not rol:
            try:
                rol = await guild.create_role(name=rol_adi, mentionable=True, reason="Otonom Çekiliş Sistemi")
            except discord.Forbidden:
                return await interaction.followup.send("❌ Hata: Botun yeni bir rol oluşturma yetkisi yok!")

        embed = discord.Embed(
            title="🎁 YENİ ÇEKİLİŞ BAŞLADI!", 
            description=f"**Ödül:** {odul}\n\nAşağıdaki butona tıklayarak çekilişe katılabilirsin.\n*(Katılanlara otonom olarak {rol.mention} rolü verilecektir)*", 
            color=discord.Color.gold()
        )
        embed.set_footer(text="Çekiliş başladı, bol şans!")
        
        await interaction.channel.send(embed=embed, view=CekilisButton(rol.id))
        await interaction.followup.send(f"✅ Çekiliş kuruldu. `{rol.name}` rolü sisteme entegre edildi.", ephemeral=True)

    @app_commands.command(name="cekilis_sonucla", description="Çekilişi bitirir, kazananı açıklar ve dağıtılan rolü tamamen siler.")
    @app_commands.describe(rol="Hangi çekilişi bitiriyoruz? (Rolü seçin)")
    async def cekilis_sonucla(self, interaction: discord.Interaction, rol: discord.Role):
        if not self.yetki_var_mi(interaction.user):
            return await interaction.response.send_message("❌ **Güvenlik Duvarı:** Yetkiniz yok!", ephemeral=True)
            
        await interaction.response.defer()
        
        katilimcilar = [uye for uye in rol.members if not uye.bot]
        
        if not katilimcilar:
            return await interaction.followup.send(f"❌ Kimse bu çekilişe katılmamış!")
            
        kazanan = random.choice(katilimcilar)
        
        embed = discord.Embed(title="🎊 ÇEKİLİŞ SONUÇLANDI! 🎊", color=discord.Color.green())
        embed.add_field(name="Kazanan Şanslı Kişi", value=kazanan.mention, inline=False)
        embed.add_field(name="Toplam Katılımcı", value=str(len(katilimcilar)), inline=False)
        
        await interaction.channel.send(content=f"Tebrikler {kazanan.mention}!", embed=embed)
        
        # 3. MUAZZAM TEMİZLİK (Rolü kökünden siliyoruz, böylece herkesten aynı anda silinmiş oluyor ve sunucuyu yormuyor)
        try:
            await rol.delete(reason="Çekiliş bitti, otonom sunucu temizliği yapıldı.")
            await interaction.followup.send(f"✅ Çekiliş bitti. Sunucu optizimasyonu için `{rol.name}` rolü tamamen silindi.", ephemeral=True)
        except:
            await interaction.followup.send(f"✅ Çekiliş bitti ancak botun yetkisi olmadığı için rol silinemedi.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Giveaway(bot))