import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# 1. BOT YAPILANDIRMASI
TOKEN = os.getenv("DISCORD_TOKEN") # Render'dan çeker
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# 2. WEB PANELİ (Render'ın uyumaması için)
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Aktif ve 7/24 Çalışıyor!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# 3. BOT BAŞLATMA VE COG YÜKLEME
@bot.event
async def on_ready():
    print(f'✅ {bot.user} başarıyla giriş yaptı!')
    # cogs klasöründeki dosyaları otomatik yükle
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
    
    # Slash komutlarını senkronize et
    await bot.tree.sync()
    print('🚀 Tüm komutlar senkronize edildi.')

# 4. ÇALIŞTIRMA
if __name__ == "__main__":
    # Web panelini arka planda başlat
    Thread(target=run_web).start()
    
    # Botu başlat
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ HATA: DISCORD_TOKEN bulunamadı! Render Environment Variables kısmını kontrol et.")