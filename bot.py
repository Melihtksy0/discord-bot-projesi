import discord
from discord.ext import commands
import os

# --- GEREKLİ İZİNLER (INTENTS) ---
# Botun üyelerin durumunu, mesajlarını ve profillerini görebilmesi için şarttır.
intents = discord.Intents.default()
intents.message_content = True  # Mesaj içeriklerini okuma izni
intents.members = True          # Sunucu üyelerini (mevcut, bilgi vb. için) görme izni
intents.presences = True        # Aktiflik (Online/Offline) durumlarını görme izni

# Bot Tanımlaması
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} başarıyla giriş yaptı!')
    print('-----------------------------------')
    
    # 1. Cogs (Modüller) Yükleme
    try:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f'⚙️ Modül yüklendi: {filename}')
                except commands.ExtensionAlreadyLoaded:
                    pass
        print('🚀 Tüm modüller başarıyla aktif edildi.')
    except Exception as e:
        print(f'❌ Modül yükleme hatası: {e}')

    # 2. Hayalet Komut Temizleyici ve Global Senkronizasyon
    print("🧹 Sunuculardaki eski hayalet komutlar temizleniyor...")
    for guild in bot.guilds:
        try:
            bot.tree.clear_commands(guild=guild)
            await bot.tree.sync(guild=guild)
        except Exception:
            pass

    try:
        synced = await bot.tree.sync()
        print(f'✨ {len(synced)} adet Slash komutu global olarak senkronize edildi.')
    except Exception as e:
        print(f'❌ Senkronizasyon hatası: {e}')

# BOTUNU ÇALIŞTIR (Kendi token yapına göre burayı düzenleyebilirsin, Render'da env kullanıyorsan os.getenv("TOKEN") yapabilirsin)
if __name__ == "__main__":
    # Eğer token'ı direkt yazıyorsan buraya ekle. (Örn: bot.run("MTIz..."))
    # Eğer .env dosyasından çekiyorsan: bot.run(os.getenv("DISCORD_TOKEN"))
    bot.run(os.getenv("DISCORD_TOKEN"))
    