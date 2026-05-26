import discord
from discord.ext import commands

# Ticket içindeki "Kapat" butonu
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Talebi Kapat", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Destek talebi 5 saniye içinde kapatılıyor...", ephemeral=True)
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

# Ana sayfadaki "Oluştur" butonu
class TicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Destek Talebi Oluştur", style=discord.ButtonStyle.primary, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        # Sadece kurucular, bot ve butona basan kişi görebilsin
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Kanalı oluştur
        channel = await guild.create_text_channel(
            name=f"destek-{interaction.user.name}",
            overwrites=overwrites,
            reason="Kullanıcı destek talebi açtı."
        )
        
        await interaction.response.send_message(f"Destek talebiniz oluşturuldu: {channel.mention}", ephemeral=True)
        
        embed = discord.Embed(
            title="Destek Talebi",
            description=f"Merhaba {interaction.user.mention}, destek ekibimiz en kısa sürede seninle ilgilenecektir.\nSorunun çözüldüğünde aşağıdaki butona basarak talebi kapatabilirsin.",
            color=discord.Color.green()
        )
        await channel.send(embed=embed, view=CloseTicketView())

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ticket-kur", description="Destek talebi (Ticket) panelini kurar.")
    @commands.has_permissions(administrator=True)
    async def ticket_kur(self, ctx):
        embed = discord.Embed(
            title="🛠️ Destek Merkezi",
            description="Sunucuyla ilgili bir sorun yaşıyorsanız veya bir yetkiliyle görüşmek istiyorsanız aşağıdaki **Destek Talebi Oluştur** butonuna tıklayabilirsiniz.",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=TicketPanel())

async def setup(bot):
    await bot.add_cog(Ticket(bot))