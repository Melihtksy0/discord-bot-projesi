import discord
from discord.ext import commands
from discord import app_commands
import asyncio

YETKILI_ROLLER = [1507777388103205004, 1507777395799621832, 1507777393232969818, 1507777394377756712]

# --------------------------------------------------
# BİLETİ KAPATMA BUTONU (YENİ)
# --------------------------------------------------
class TicketCloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Bileti Kapat", style=discord.ButtonStyle.danger, custom_id="ticket_kapat", emoji="🔒")
    async def kapat(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sadece yetkililer veya bileti açan kişi kapatabilir kısıtlaması da eklenebilir, şu an kanalı gören herkes basabilir.
        await interaction.response.send_message("🔒 Bu bilet kapatılıyor... Kanal 5 saniye içinde tamamen silinecektir.", ephemeral=False)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except:
            pass

# --------------------------------------------------
# BİLET (TICKET) AÇMA BUTONU SİSTEMİ
# --------------------------------------------------
class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Destek Talebi Oluştur", style=discord.ButtonStyle.primary, custom_id="ticket_olustur", emoji="🎫")
    async def ticket_olustur(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        kategori = discord.utils.get(guild.categories, name="Destek Talepleri")
        
        if not kategori:
            kategori = await guild.create_category("Destek Talepleri")

        kanal_adi = f"destek-{interaction.user.name}"
        mevcut_kanal = discord.utils.get(guild.channels, name=kanal_adi)
        if mevcut_kanal:
            return await interaction.response.send_message("❌ Zaten açık bir talebiniz bulunuyor!", ephemeral=True)

        # KANAL İZİNLERİ (Sadece kuran kişi ve yetkililer görebilir, rol oluşturmaya gerek kalmaz)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        for rol_id in YETKILI_ROLLER:
            rol = guild.get_role(rol_id)
            if rol: 
                overwrites[rol] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(kanal_adi, category=kategori, overwrites=overwrites)
        
        embed = discord.Embed(
            title="🎫 Destek Talebi", 
            description=f"Hoş geldin {interaction.user.mention}. Sorununu buraya detaylıca yazabilirsin.\n\nİşlemin bittiğinde aşağıdaki butona tıklayarak talebi kapatabilirsin.", 
            color=discord.Color.blue()
        )
        
        # Odaya hem mesajı hem de kapatma butonunu gönderiyoruz
        await ticket_channel.send(content=interaction.user.mention, embed=embed, view=TicketCloseButton())
        await interaction.response.send_message(f"✅ Talebiniz oluşturuldu: {ticket_channel.mention}", ephemeral=True)

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket_kur", description="Destek talebi panelini bulunduğunuz kanala gönderir.")
    async def ticket_kur(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📩 İletişim & Destek Merkezi", 
            description="Aşağıdaki butona tıklayarak yetkililerle özel olarak görüşebileceğiniz bir destek talebi oluşturabilirsiniz.", 
            color=discord.Color.dark_theme()
        )
        await interaction.channel.send(embed=embed, view=TicketButton())
        await interaction.response.send_message("Panel başarıyla kuruldu.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))