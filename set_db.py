import sqlite3

con = sqlite3.connect("./link.db")

cur = con.cursor()

try:
    cur.execute("CREATE TABLE SearchLink(Psearch TEXT, Csearch TEXT, Author TEXT, Date TEXT, Link TEXT, Crawled INTEAGER);")
    cur.execute("CREATE TABLE LinkText(Psearch TEXT, Csearch TEXT, Author TEXT, Date TEXT, Link TEXT, Main TEXT);")
except:
    pass
'''

test_data = ['무민세대', '무Mean세대', '블로그명', '20210101', 'www.naver.com', 0]
cur.execute("INSERT INTO SearchLink Values(?, ?, ?, ?, ?, ?)", test_data)
'''

#cur.execute("DROP TABLE SearchLink")
#cur.execute("DROP TABLE LinkText")


#cur.execute("SELECT * FROM SearchLink ORDER BY Date")
#cur.execute("SELECT Psearch, Csearch, Author, Date, Link FROM LinkText")

#cur.execute("SELECT * FROM SearchLink WHERE Crawled = '1' AND Link LIKE '%blog%'")
cur.execute("SELECT * FROM SearchLink WHERE Crawled = '0' AND Link LIKE '%cafe%'")

i = 0
for row in cur.fetchall():
    i += 1
    print(row)
print(i)
con.commit()
con.close()
