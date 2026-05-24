import discord
from discord.ext import commands
import time
import datetime

# YETKİLİ ROL ID'LERİ (Güvenlik Kalkanı bu rollere etki etmez, onlar özgürdür)
YETKILI_ROLLER = [1507777388103205004, 1507777395799621832, 1507777393232969818, 1507777394377756712]

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_kontrol = {}
        # Buraya engellemek istediğin kelimeleri küçük harflerle ekleyebilirsin
        self.yasakli_kelimeler = ["küfür1", "küfür2", "argo1"] 

    # YARDIMCI GÜVENLİK FONKSİYONU
    def yetki_var_mi(self, user):
        if getattr(user, "roles", None) is None: return False
        return any(rol.id in YETKILI_ROLLER for rol in user.roles)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Botların kendi mesajlarını ve DM mesajlarını yoksay
        if message.author.bot or not message.guild: 
            return
            
        # Yetkililer kalkanlardan muaftır
        if self.yetki_var_mi(message.author): 
            return 

        icerik = message.content.lower()

        # --------------------------------------------------
        # 1. ANTI-REKLAM (Siber Kalkan)
        # --------------------------------------------------
        if "discord.gg/" in icerik or "discord.com/invite/" in icerik:
            await message.delete()
            uyari = await message.channel.send(f"🚨 {message.author.mention}, bu sunucuda başka sunucuların reklamını yapmak yasaktır!")
            await uyari.delete(delay=5) # Uyarı mesajını 5 saniye sonra temizle
            return

        # --------------------------------------------------
        # 2. ANTI-KÜFÜR (İçerik Filtresi)
        # --------------------------------------------------
        # Kelimeleri parçalayarak tam eşleşme arar (Örn: "kötü" kelimesi yasaksa, "kötümsersin" kelimesine ceza vermez)
        mesaj_kelimeleri = icerik.split()
        for kelime in self.yasakli_kelimeler:
            if kelime in mesaj_kelimeleri:
                await message.delete()
                uyari = await message.channel.send(f"🤬 {message.author.mention}, lütfen sohbet kurallarına ve kelimelerinize dikkat edin!")
                await uyari.delete(delay=5)
                return

        # --------------------------------------------------
        # 3. ANTI-SPAM (DDoS Koruma Mantığı ve Otonom Susturma)
        # --------------------------------------------------
        yazar_id = message.author.id
        su_an = time.time()
        
        if yazar_id not in self.spam_kontrol:
            self.spam_kontrol[yazar_id] = []
            
        # Kullanıcının sadece son 5 saniyedeki mesajlarının zamanını tut
        self.spam_kontrol[yazar_id] = [t for t in self.spam_kontrol[yazar_id] if su_an - t < 5]
        self.spam_kontrol[yazar_id].append(su_an)
        
        # Eğer son 5 saniye içinde 5 mesaja ulaştıysa spam tespit edilir
        if len(self.spam_kontrol[yazar_id]) >= 5: 
            try:
                await message.delete()
                
                # Kullanıcıya otonom olarak 60 saniyelik Time-Out (Susturma) cezası verilir
                zaman_asimi_suresi = discord.utils.utcnow() + datetime.timedelta(minutes=1)
                await message.author.timeout(zaman_asimi_suresi, reason="Otonom Sistem: Spam/Flood Tespiti")
                
                bilgi = await message.channel.send(f"🛑 **SİSTEM MÜDAHALESİ:** {message.author.mention}, kanalı spamladığı için 1 dakika boyunca susturuldu.")
                await bilgi.delete(delay=10)
                
                self.spam_kontrol[yazar_id] = [] # Cezasını alınca sicilini sıfırla ki ceza bitince tekrar yazabilsin
            except discord.Forbidden:
                pass # Botun susturma yetkisi yoksa sessizce geç

async def setup(bot):
    await bot.add_cog(Security(bot))