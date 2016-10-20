import sqlite3

# TODO: command line arg
conn = sqlite3.connect("database.db")

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE animals
             (name text, strength real, agility real, wit real, senses real)''')

# Save (commit) the changes
conn.commit()

conn.close()