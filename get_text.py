import requests
from urllib import parse
from bs4 import BeautifulSoup
import datetime
import time
import os
from tqdm import tqdm
import sys
import re
import sqlite3
import random
from multiprocessing import Process, Queue

def blog_iframelink(link):
    #블로그 링크내의 iframe 링크 추출
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

    cnt = 0

    while True:

        if cnt > 10:
            print(link)
            print("null page" + str(resp.status_code))
            return ''

        try:
            #0초에서 2초 사이의 랜덤한 대기시간
            time.sleep(random.randrange(0, 1000)/500)
            resp = requests.get(link, headers = hdr, timeout=10)
            #print(resp.url)

        except requests.exceptions.Timeout as timeout:

            print(timeout)
            print(link)
            time.sleep(10)
            continue

        except requests.exceptions.ConnectionError as cut:

            print(cut)
            print(link)
            #연결 끊김 발생시 15분 대기
            time.sleep(900)
            continue

        except:
            #첫 페이지 불러오기에 실패
            #None 값 리턴
            print(link ,'첫 페이지 불러오기 실패')
            return ''

        #html 추출
        if resp.status_code == 200:
            html = resp.text
        
            soup = BeautifulSoup(html, 'lxml')

            iframe_link = soup.find('iframe', id = 'mainFrame')['src']

            return iframe_link

        elif resp.status_code == 404:
            print("code : " + str(resp.status_code))
            return ''
        else:
            print("not 200 retry : " + str(cnt))

            if cnt == 10:
                print("null page" + str(resp.status_code))
                return ''
        cnt += 1
def cafe_iframelink(link):
    #블로그 링크내의 iframe 링크 추출
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

    while True:

        try:
            resp = requests.get(link, headers = hdr, timeout=10)
            #print(resp.url)

        except requests.exceptions.Timeout as timeout:

            print(timeout)
            print(link)
            time.sleep(10)
            continue

        except requests.exceptions.ConnectionError as cut:

            print(cut)
            print(link)
            #연결 끊김 발생시 15분 대기
            time.sleep(900)
            continue

        except:
            #첫 페이지 불러오기에 실패
            #None 값 리턴
            print(link ,'첫 페이지 불러오기 실패')
            return None

        #html 추출
        if resp.status_code == 200:
            html = resp.text
        
            soup = BeautifulSoup(html, 'lxml')

            iframe_link = soup.find('iframe', id = 'cafe_main')['src']

            return iframe_link

def get_html(link):

    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
    cnt = 0
    while True:
        
        if cnt > 10:
                print(link)
                print("null page" + str(resp.status_code))
                return ''

        try:
            #0초에서 2초 사이의 랜덤한 대기시간
            time.sleep(random.randrange(0, 1000)/500)
            resp = requests.get(link, headers = hdr, timeout=10)
            #print(resp.url)

        except requests.exceptions.Timeout as timeout:

            print(timeout)
            print(link)
            time.sleep(10)
            cnt += 1
            continue

        except requests.exceptions.ConnectionError as cut:

            print(cut)
            print(link)
            #네이버 블로그일 경우 연결 끊김 발생시 15분 대기
            if "naver" in link:
                cnt += 1
                time.sleep(900)
                continue
            
            #외부 블로그일 경우 1분 대기
            else:
                cnt += 1
                time.sleep(60)
                continue

        except:
            #첫 페이지 불러오기에 실패
            #None 값 리턴
            print(link ,'첫 페이지 불러오기 실패')
            return ''

        #html 추출
        if resp.status_code == 200:
            html = resp.text
            return html

        elif resp.status_code == 404:
            print(link)
            print("code : " + str(resp.status_code))
            return ''
        else:
            print("not 200 retry : " + str(cnt))

            if cnt == 10:
                print(link)
                print("null page" + str(resp.status_code))
                return ''
        cnt += 1

def html_parser(html):

    #페이지 파싱
    soup = BeautifulSoup(html, 'lxml')

    main_text = []
    for data in soup.find_all('p'):

        main_text.append(data.text)

    if main_text:
        return "\n".join(main_text)

    else:
        return "\n".join(soup.text)

def blog_parser(html):

    #페이지 파싱
    soup = BeautifulSoup(html, 'lxml')

    data_list = soup.find('div', id = 'postListBody')

    main_text = []
    for data in data_list.find_all('p'):

        main_text.append(data.text)


    if main_text:
        return "\n".join(main_text)

    else:
        return "\n".join(data_list.text)

def cafe_parser(html):

    #페이지 파싱
    soup = BeautifulSoup(html, 'lxml')

    data_list = soup.find('div', class_ = 'content CafeViewer')

    main_text = []
    for data in data_list.find_all('p'):

        main_text.append(data.text)


    if main_text:
        return "\n".join(main_text)

    else:
        return "\n".join(data_list.text)

def blog_text(SearchLink):
    
    con = sqlite3.connect("./link.db")

    cur = con.cursor()

    #나중에 INSERT 하기 위해 SearchLink를 list로 변환
    SearchLink = list(SearchLink)
        
    link = SearchLink[4]

    #네이버 블로그일경우 iframe 링크 추출
    if (link.find('naver') != -1):

        link = 'https://blog.naver.com' + blog_iframelink(link)

        html = get_html(link)

        #html 추출 성공
        if html:

            SearchLink.pop()
            SearchLink.append(blog_parser(html))
            
            #print(SearchLink[-1])
            cur.execute("UPDATE SearchLink SET Crawled = ? WHERE Link = ?", (1, SearchLink[4]))
            cur.execute("INSERT INTO LinkText Values(?, ?, ?, ?, ?, ?)", SearchLink)

            con.commit()

        #실패한 경우 -1 입력
        else:
            cur.execute("UPDATE SearchLink SET Crawled = ? WHERE Link = ?", (-1, SearchLink[4]))
            con.commit()
    
    #네이버 블로그가 아닌 경우
    else:

        html = get_html(link)

        #html 추출 성공
        if html:

            SearchLink.pop()
            SearchLink.append(html_parser(html))

            #print(SearchLink[-1])
            cur.execute("UPDATE SearchLink SET Crawled = ? WHERE Link = ?", (1, SearchLink[4]))
            cur.execute("INSERT INTO LinkText Values(?, ?, ?, ?, ?, ?)", SearchLink)

            con.commit()

        #실패한 경우 -1 입력
        else:
            cur.execute("UPDATE SearchLink SET Crawled = ? WHERE Link = ?", (-1, SearchLink[4]))
            con.commit()


    con.close()            

def cafe_text(SearchLink_list):
    
    con = sqlite3.connect("./link.db")

    cur = con.cursor()

    for x in tqdm(range(len(SearchLink_list))):

        #나중에 INSERT 하기 위해 SearchLink를 list로 변환
        SearchLink = SearchLink_list[x]
        SearchLink = list(SearchLink)
        
        link = SearchLink[4]

        #네이버 카페일 경우 iframe 링크 추출
        if (link.find('naver') != -1):
            print(link)
            link = 'https:' + cafe_iframelink(link)

            html = get_html(link)

            #html 추출 성공
            if html:

                SearchLink.pop()
                SearchLink.append(cafe_parser(html))
                
                #print(SearchLink[-1])
                cur.execute("UPDATE SearchLink SET Crawled = ? WHERE Link = ?", (1, SearchLink[4]))
                cur.execute("INSERT INTO LinkText Values(?, ?, ?, ?, ?, ?)", SearchLink)

                con.commit()
        
        #네이버 카페가 아닌 경우
        else:

            html = get_html(link)

            #html 추출 성공
            if html:

                SearchLink.pop()
                SearchLink.append(html_parser(html))

                #print(SearchLink[-1])
                cur.execute("UPDATE SearchLink SET Crawled = ? WHERE Link = ?", (1, SearchLink[4]))
                cur.execute("INSERT INTO LinkText Values(?, ?, ?, ?, ?, ?)", SearchLink)

                con.commit()


    con.close()            

def walk_db(SearchLink_Q):

    con = sqlite3.connect("./link.db")

    cur = con.cursor()

    cur.execute("SELECT * FROM SearchLink WHERE Crawled = '0'")

    for line in tqdm(cur.fetchall()):
        SearchLink_Q.put(line)

    #프로세스 종료를 위해 빈 리스트 삽입
    for i in range(10):
        SearchLink_Q.put([])

    con.close()

def run_process(N, SearchLink_Q):

    while True:
        flag = SearchLink_Q.get()

        if not flag:
            break

        else:
            blog_text(flag)

if __name__ == '__main__':
    
    start = time.time()

    SearchLink_Q = Queue()

    process_list = []
    p = Process(target=walk_db, args=(SearchLink_Q,))
    p.start()
    process_list.append(p)

    for N in range(0, 10):
        process = Process(target=run_process, args=(N, SearchLink_Q,))
        process.start()
        process_list.append(process)

    print("join_start")
    for process in process_list:
        process.join()
        print(process)

    print(time.time() - start)
    #db timeout 설정
    #db.execute('pragma busy_timeout=10000')
    '''
    cur.execute("SELECT * FROM SearchLink WHERE Crawled = '0' AND Link LIKE '%cafe%'")
    cafe_text(cur.fetchall())

    '''
    #last run
    #100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7905/7905 [1:13:07<00:00,  1.80it/s] 

    #print(get_html("https://cafe.naver.com/ArticleRead.nhn?articleid=1474800&art=ZXh0ZXJuYWwtc2VydmljZS1uYXZlci1zZWFyY2gtY2FmZS1wcg.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjYWZlVHlwZSI6IkNBRkVfVVJMIiwiY2FmZVVybCI6ImNob2djYSIsImFydGljbGVJZCI6MTQ3NDgwMCwiaXNzdWVkQXQiOjE2NzY5ODA5ODA5MzR9.3XqXJMIQmZStF4bbbrwEuXvX2dOuSR0DVft72PpMBQE&clubid=21231131"))
    
    '''
    $("cafe_main").src = "//cafe.naver.com/ArticleRead.nhn?articleid=1474800&art=ZXh0ZXJuYWwtc2VydmljZS1uYXZlci1zZWFyY2gtY2FmZS1wcg.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjYWZlVHlwZSI6IkNBRkVfVVJMIiwiY2FmZVVybCI6ImNob2djYSIsImFydGljbGVJZCI6MTQ3NDgwMCwiaXNzdWVkQXQiOjE2NzY5ODA5ODA5MzR9.3XqXJMIQmZStF4bbbrwEuXvX2dOuSR0DVft72PpMBQE&clubid=21231131";
    '''					