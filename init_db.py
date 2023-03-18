import sqlite3

con = sqlite3.connect("./link.db")

cur = con.cursor()

try:
    cur.execute("DROP TABLE SearchLink")
    cur.execute("DROP TABLE LinkText")
except:
    pass

try:
    cur.execute("CREATE TABLE SearchLink(Psearch TEXT, Csearch TEXT, Author TEXT, Date TEXT, Link TEXT, Crawled INTEAGER);")
    cur.execute("CREATE TABLE LinkText(Psearch TEXT, Csearch TEXT, Author TEXT, Date TEXT, Link TEXT, Main TEXT);")
except:
    pass

con.commit()
con.close()
