import sqlite3
import os
import re
from tqdm import tqdm

con = sqlite3.connect("./link.db")

cur = con.cursor()

#COLUMN
#(Psearch, Csearch, Author, Date, Link, Main)
cur.execute("SELECT * FROM LinkText")

LinkText_list = cur.fetchall()
for x in tqdm(range(len(LinkText_list))):
    row = list(LinkText_list[x])
    dirname = "/".join(row[:2])

    dirname = "/".join(["Search", dirname, row[3][:6]])
    #블로그, 카페명 특수문자 제거
    row[2] = re.sub(r"[^\uAC00-\uD7A30-9a-zA-Z]", "", row[2])
    fname = "_".join(row[3:1:-1])
    
    os.makedirs(dirname, exist_ok=True)

    f = open("/".join([dirname, fname]) + ".txt", "w", encoding='utf-8')

    f.write(row[-1])
    f.write(row[-2])

    f.close()
    
    
con.commit()
con.close()
