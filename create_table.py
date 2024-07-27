import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('CREATE TABLE noise_database (id INT, timestamp TEXT, noise_level INT)')
print("Created table successfully!")

conn.close()