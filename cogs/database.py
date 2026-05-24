import sqlite3
import discord
from discord.ext import commands

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.baglan()

    def baglan(self):
        # Eğer database.db yoksa otomatik oluşturur
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        # Tablo oluşturma: Kullanıcıların level ve XP bilgilerini tutacağız
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                              (user_id INTEGER PRIMARY KEY, xp INTEGER, level INTEGER)''')
        self.conn.commit()

    # Kullanıcı mesaj attıkça XP kazanması için fonksiyon
    def xp_artir(self, user_id):
        self.cursor.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
        data = self.cursor.fetchone()
        
        if data:
            new_xp = data[0] + 10 # Her mesajda 10 XP
            new_lvl = data[1]
            # Level atlama hesabı (XP 100 olunca level atlar)
            if new_xp >= 100:
                new_xp = 0
                new_lvl += 1
            self.cursor.execute("UPDATE users SET xp = ?, level = ? WHERE user_id = ?", (new_xp, new_lvl, user_id))
        else:
            self.cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user_id, 10, 1))
        self.conn.commit()

async def setup(bot):
    await bot.add_cog(Database(bot))