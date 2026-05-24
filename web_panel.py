from flask import Flask, render_template_string
import threading

app = Flask(__name__)
bot_referansi = None # Botumuzun verilerini buraya çekeceğiz

# Basit ama şık bir HTML şablonu (Tailwind CSS kullanılarak tasarlandı)
html_sablonu = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProMod Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white flex items-center justify-center h-screen">
    <div class="bg-gray-800 p-8 rounded-lg shadow-2xl w-96 text-center border border-gray-700">
        <h1 class="text-3xl font-bold mb-2 text-indigo-400">ProMod Panel</h1>
        <p class="text-gray-400 mb-6">Sistem Durumu: <span class="text-green-500 font-bold">Aktif</span></p>
        
        <div class="bg-gray-700 p-4 rounded-md mb-4 text-left">
            <h2 class="text-xl font-semibold mb-2">Bot İstatistikleri</h2>
            <p>🌐 <strong>Bağlı Sunucu:</strong> {{ sunucu_sayisi }}</p>
            <p>👥 <strong>Toplam Kullanıcı:</strong> {{ kullanici_sayisi }}</p>
            <p>⏱️ <strong>Gecikme (Ping):</strong> {{ ping }}ms</p>
        </div>
        <p class="text-sm text-gray-500 mt-4">Flask & Discord.py Entegrasyonu</p>
    </div>
</body>
</html>
"""

@app.route('/')
def ana_sayfa():
    if not bot_referansi or not bot_referansi.is_ready():
        return "<h1>Sistem Beklemede... Botun Discord'a bağlanması bekleniyor.</h1>"

    # Botun anlık verilerini çekiyoruz
    sunucu_sayisi = len(bot_referansi.guilds)
    kullanici_sayisi = sum([guild.member_count for guild in bot_referansi.guilds])
    ping_suresi = round(bot_referansi.latency * 1000)

    # Verileri HTML içine gömüp ekrana basıyoruz
    return render_template_string(
        html_sablonu, 
        sunucu_sayisi=sunucu_sayisi, 
        kullanici_sayisi=kullanici_sayisi, 
        ping=ping_suresi
    )

def flask_baslat(bot):
    global bot_referansi
    bot_referansi = bot
    # Web sunucusunu 5000 portunda başlat (Debug modunu kapalı tutuyoruz ki Discord ile çakışmasın)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def web_panelini_calistir(bot):
    # Flask sunucusunu ayrı bir "Thread" (iş parçacığı) olarak başlatıyoruz ki botu dondurmasın
    server_thread = threading.Thread(target=flask_baslat, args=(bot,))
    server_thread.daemon = True # Ana dosya kapanınca web sunucusu da kapansın
    server_thread.start()