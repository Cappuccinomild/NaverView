import sqlite3

con = sqlite3.connect("./link.db")

cur = con.cursor()

#cur.execute("CREATE TABLE SearchLink(Psearch TEXT, Csearch TEXT, Author TEXT, Date TEXT, Link TEXT, Crawled INTEAGER);")
'''

test_data = ['무민세대', '무Mean세대', '블로그명', '20210101', 'www.naver.com', 0]
cur.execute("INSERT INTO SearchLink Values(?, ?, ?, ?, ?, ?)", test_data)
'''

#cur.execute("DROP TABLE SearchLink")
cur.execute("SELECT * FROM SearchLink ORDER BY Date")



i = 0
for row in cur.fetchall():
    i += 1
    print(row)
print(i)
con.commit()
con.close()