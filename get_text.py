import requests
from urllib import parse
from bs4 import BeautifulSoup
import datetime
import time
import os
from tqdm import tqdm
import math
import multiprocessing
import sys
import re
import sqlite3

def blog_iframelink(link):
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

            iframe_link = soup.find('iframe', id = 'mainFrame')['src']

            return iframe_link

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
            if cnt > 0:
                return ''
            #연결 끊김 발생시 1분 대기
            time.sleep(60)
            cnt += 1
            continue

        except:
            #첫 페이지 불러오기에 실패
            #None 값 리턴
            print(link ,'첫 페이지 불러오기 실패')
            return None

        #html 추출
        if resp.status_code == 200:
            html = resp.text
            return html

        #404 코드와 100회 이상 재시도일 경우 '' 리턴
        elif resp.status_code == 404 and cnt > 20:
            return ''

        #30회 재시도
        elif cnt > 30:
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

def blog_text(SearchLink_list):
    
    con = sqlite3.connect("./link.db")

    cur = con.cursor()

    for x in tqdm(range(len(SearchLink_list))):

        #나중에 INSERT 하기 위해 SearchLink를 list로 변환
        SearchLink = SearchLink_list[x]
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

if __name__ == '__main__':

    con = sqlite3.connect("./link.db")

    cur = con.cursor()

    cur.execute("SELECT * FROM SearchLink WHERE Crawled = '0'")
    blog_text(cur.fetchall())
    '''
    cur.execute("SELECT * FROM SearchLink WHERE Crawled = '0' AND Link LIKE '%cafe%'")
    cafe_text(cur.fetchall())

    '''
    #last run
    #100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7905/7905 [1:13:07<00:00,  1.80it/s] 

    #print(get_html("https://cafe.naver.com/ArticleRead.nhn?articleid=1474800&art=ZXh0ZXJuYWwtc2VydmljZS1uYXZlci1zZWFyY2gtY2FmZS1wcg.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjYWZlVHlwZSI6IkNBRkVfVVJMIiwiY2FmZVVybCI6ImNob2djYSIsImFydGljbGVJZCI6MTQ3NDgwMCwiaXNzdWVkQXQiOjE2NzY5ODA5ODA5MzR9.3XqXJMIQmZStF4bbbrwEuXvX2dOuSR0DVft72PpMBQE&clubid=21231131"))
    con.commit()
    '''
    $("cafe_main").src = "//cafe.naver.com/ArticleRead.nhn?articleid=1474800&art=ZXh0ZXJuYWwtc2VydmljZS1uYXZlci1zZWFyY2gtY2FmZS1wcg.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjYWZlVHlwZSI6IkNBRkVfVVJMIiwiY2FmZVVybCI6ImNob2djYSIsImFydGljbGVJZCI6MTQ3NDgwMCwiaXNzdWVkQXQiOjE2NzY5ODA5ODA5MzR9.3XqXJMIQmZStF4bbbrwEuXvX2dOuSR0DVft72PpMBQE&clubid=21231131";
    '''					