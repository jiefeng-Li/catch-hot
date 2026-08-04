import sqlite3
p='data/catchhot.db'
con=sqlite3.connect(p)
cur=con.cursor()
try:
    cur.execute("ALTER TABLE hot_items ADD COLUMN score FLOAT DEFAULT 0.0")
    cur.execute("ALTER TABLE hot_items ADD COLUMN meta JSON")
    con.commit()
    print('migrated')
except Exception as e:
    print('skip or error', e)
cur.close()
con.close()
