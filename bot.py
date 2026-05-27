import discord
from discord.ext import commands
import os
from threading import Thread
from flask import Flask
from waitress import serve

# --- 1. KEEP ALIVE SİSTEMİ (RENDER 7/24 AKTİFLİK) ---
app = Flask('')

@app.route('/')
def home():
    return "YushaBot Aktif ve Çalışıyor!"

def run_server():
    # Waitress ile üretim ortamı sunucusu
    serve(app, host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# --- 2. GEREKLİ İZİNLER (INTENTS) ---
intents = discord.Intents.default()
intents.message_content = True  # Mesajları okuma izni
intents.members = True          # Üye listesini görme izni
intents.presences = True        # Aktiflik durumunu izleme izni

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- 3. BOT HAZIRLIK VE YÜKLEME ---
@bot.event
async def on_ready():
    print(f'✅ {bot.user} başarıyla giriş yaptı!')
    print('-----------------------------------')
    
    # Cogs (Modülleri) Yükle
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'⚙️ Modül yüklendi: {filename}')
            except Exception as e:
                print(f'❌ Modül yüklenemedi {filename}: {e}')

    # Senkronizasyon
    print("🔄 Komutlar senkronize ediliyor...")
    try:
        # Anlık senkronizasyon için tüm sunucuları tara
        for guild in bot.guilds:
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
        print('✨ Tüm komutlar başarıyla senkronize edildi.')
    except Exception as e:
        print(f'❌ Senkronizasyon hatası: {e}')

# --- 4. ANA ÇALIŞTIRMA ---
if __name__ == "__main__":
    # Render 7/24 uyanık tut
    keep_alive()
    
    # Botu başlat (Token'ı Render Env'den al)
    token = os.environ.get("TOKEN")
    if not token:
        print("❌ HATA: TOKEN bulunamadı! Render Environment Variables kısmını kontrol et.")
    else:
        bot.run(token)