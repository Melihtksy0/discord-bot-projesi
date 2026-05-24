import discord
from discord.ext import commands
import os
import threading
from flask import Flask

# 1. Flask Web Sunucusu (Render'ın uyumaması için)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Aktif ve 7/24 Çalışıyor!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# 2. Bot Ayarları
# Render Environment Variables kısmına yazdığın DISCORD_TOKEN'ı çeker
TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} başarıyla giriş yaptı!')
    # Cogs yükleme
    try:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
        print('🚀 Tüm cogs başarıyla yüklendi.')
    except Exception as e:
        print(f'❌ Cog yükleme hatası: {e}')
    
    await bot.tree.sync()
    print('✨ Slash komutları senkronize edildi.')

# 3. Çalıştırma
if __name__ == "__main__":
    # Web sunucusunu ayrı bir iş parçacığında (thread) başlat
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()
    
    # Botu başlat
    if TOKEN:
        print("Bot başlatılıyor...")
        bot.run(TOKEN)
    else:
        print("❌ HATA: DISCORD_TOKEN bulunamadı! Render panelinden Environment Variables kontrol et.")