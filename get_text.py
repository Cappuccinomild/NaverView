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

def get_iframelink(link):
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

            if(html):
                soup = BeautifulSoup(html, 'lxml')

                iframe_link = soup.find('iframe', id = 'mainFrame')['src']

                return iframe_link

            else:
                return None


def get_html(link):

    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
    cnt = 0
    while True:

        try:
            resp = requests.get(link, headers = hdr, timeout=10)
            print(resp.url)

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

def naver_parser(html):

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

if __name__ == '__main__':

    con = sqlite3.connect("./link.db")

    cur = con.cursor()

    cur.execute("SELECT * FROM SearchLink WHERE Crawled = '0' AND Link LIKE '%blog%'")

    for SearchLink in cur.fetchall():
        
        #나중에 INSERT 하기 위해 SearchLink를 list로 변환
        SearchLink = list(SearchLink)
        link = SearchLink[4]

        #네이버 블로그일경우 iframe 링크 추출
        if (link.find('naver') != -1):

            link = 'https://blog.naver.com' + get_iframelink(link)

            html = get_html(link)

            #html 추출 성공
            if html:

                SearchLink.append(naver_parser(html))
                print(SearchLink[-1])
        
        #네이버 블로그가 아닌 경우
        else:

            html = get_html(link)

            #html 추출 성공
            if html:
                
                SearchLink.append(html_parser(html))
                print(SearchLink[-1])
                #cur.exeute("UPDATE SearchLink SET Crawled = ? WHERE Link = ?", (1, link))


