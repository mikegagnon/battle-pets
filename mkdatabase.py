import sqlite3

# TODO: command line arg
conn = sqlite3.connect("database.db")

c = conn.cursor()

# TODO: uniq names? ids?
# Create table
c.execute('''CREATE TABLE Animals
             (name text, strength real, agility real, wit real, senses real)''')

# Save (commit) the changes
conn.commit()

conn.close()