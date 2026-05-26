import discord
from discord.ext import commands
import os
from threading import Thread
from flask import Flask

# --- KEEP ALIVE SİSTEMİ (RENDER 7/24 AKTİFLİK İÇİN) ---
app = Flask('')
@app.route('/')
def home():
    return "YushaBot Aktif ve Çalışıyor!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- GEREKLİ İZİNLER (INTENTS) ---
intents = discord.Intents.default()
intents.message_content = True  # Mesaj okuma izni
intents.members = True          # Üye profillerini görme izni
intents.presences = True        # Aktiflik (Online/Offline) durumlarını görme izni

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

if __name__ == "__main__":
    keep_alive() # Botun Render'da uyumaması için web sunucusunu başlatır
    bot.run(os.environ.get("TOKEN")) # Token'ı Render Environment'dan çeker