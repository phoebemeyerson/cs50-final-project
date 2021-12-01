import sqlite3

conn = sqlite3.connect('noms.db')
c = conn.cursor()

c.execute('''
          CREATE TABLE IF NOT EXISTS users
          ([id] INTEGER PRIMARY KEY, [username] TEXT NOT NULL, [hash] TEXT NOT NULL)
          ''')