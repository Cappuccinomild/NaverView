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

def get_html(view_link, hdr, datas):

    while True:

        try:
            resp = requests.get(view_link, headers = hdr, params=datas, timeout=10)
            #print(resp.url)

        except requests.exceptions.Timeout as timeout:

            print(timeout)
            print(datas)
            time.sleep(10)
            continue

        except requests.exceptions.ConnectionError as cut:

            print(cut)
            print(datas)
            #연결 끊김 발생시 15분 대기
            time.sleep(900)
            continue

        except:
            #첫 페이지 불러오기에 실패
            #None 값 리턴
            print(datas['query'] ,'첫 페이지 불러오기 실패')
            print(datas)
            return None

        #html 추출
        if resp.status_code == 200:
            html = resp.text

            return html

def get_1st_blog(Pquery, Cquery, date_from, date_to):
    #Blog
    #https://search.naver.com/search.naver?where=blog&query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&sm=tab_opt&nso_open=1&nso=so:dd,p:from20110101to20230219,a:all
    #https://s.search.naver.com/p/blog/search.naver?where=blog&sm=tab_pge&api_type=1&query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&rev=44&start=31&dup_remove=1&post_blogurl=&post_blogurl_without=&nso=so%3Add%2Cp%3Afrom20230219to20110101&nlu_query=&dkey=0&source_query=&nx_search_query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&spq=0

    view_link = "https://search.naver.com/search.naver"
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

    datas = {

        'where':'blog',
        'sm':'tab_opt',
        'query':'',
        'nso_open':'1',
        'nso':'',

    }

    #검색어와 날짜 입력
    #datas['query'] = parse.quote(query)
    datas['query'] = Cquery
    datas['nso'] = "so:dd,p:from" + date_from + "to" + date_to + ",a:all"

    #html 초기화
    html = ''

    #DB 연결
    con = sqlite3.connect("./link.db")
    cur = con.cursor()

    #html 추출
    html = get_html(view_link, hdr, datas)
    
    #페이지 파싱
    soup = BeautifulSoup(html, 'lxml')

    data_list = soup.find('ul', class_ = 'lst_total')

    for data in data_list.find_all('div', class_ = 'total_area'):
        author = data.find('span', class_ = 'elss etc_dsc_inner').text
        link = data.find('div', class_="total_dsc_wrap").find('a')["href"]
        written_date = data.find('span', class_='sub_time sub_txt').text

        #'N일 전' 처리
        if(written_date.find("일 전") == 1):
            written_date = (datetime.datetime.now() - datetime.timedelta(days = int(written_date[:-3]))).strftime("%Y.%m.%d")

        #DB 구조
        #Psearch TEXT, Csearch TEXT, Author TEXT, Date TEXT, Link TEXT, Crawled INTEAGER

        #같은 링크를 보유하고있으면 입력하지 않음
        cur.execute("SELECT * FROM SearchLink WHERE Link = '" + link +"'")
        if(len(cur.fetchall()) == 0):    
            db_input = [Pquery, Cquery, author, written_date, link, 0]
            cur.execute("INSERT INTO SearchLink Values(?, ?, ?, ?, ?, ?)", db_input)

        print(author, link)

    con.commit()
    con.close()

    return True

def get_1st_cafe(query, date_from, date_to):
    #Cafe
    #https://search.naver.com/search.naver?where=article&sm=tab_viw.blog&query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&nso=so%3Add%2Cp%3Afrom20110101to20230219%2Ca%3Aall
    #https://s.search.naver.com/p/cafe/search.naver?where=article&ie=utf8&query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&prdtype=0&t=0&st=date&srchby=text&dup_remove=1&cafe_url=&without_cafe_url=&sm=tab_opt&nso=so:dd,p:from20110101to20230219,a:all&nso_open=0&rev=44&abuse=0&ac=0&aq=0&converted=0&is_dst=0&nlu_query=&nqx_context=&nx_and_query=&nx_search_hlquery=&nx_search_query=&nx_sub_query=&people_sql=0&spq=0&x_tab_article=&is_person=0&start=11&display=10&prmore=1

    view_link = "https://search.naver.com/search.naver"
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

    datas = {

        'where':'view',
        'sm':'tab_jum',
        'query':''

    }

    #datas['query'] = parse.quote(query)
    datas['query'] = query


    while True:

        try:
            resp = requests.get(view_link, headers = hdr, params=datas, timeout=10)
            print(resp.url)
        except requests.exceptions.Timeout as timeout:

            print(timeout)
            print(datas)
            time.sleep(10)
            continue

        except requests.exceptions.ConnectionError as cut:

            print(cut)
            print(datas)
            #연결 끊김 발생시 15분 대기
            time.sleep(900)
            continue

        except:
            #첫 페이지 불러오기에 실패
            #None 값 리턴
            print(query ,'첫 페이지 불러오기 실패')
            print(datas)
            return None

        #html 추출
        if resp.status_code == 200:
            html = resp.text
            break  

    return html    

def blog_parser(Pquery, Cquery, html):
    
    #DB 연결
    con = sqlite3.connect("./link.db")
    cur = con.cursor()

    soup = BeautifulSoup(html, 'lxml')

    for data in soup.find_all('li'):

        data_A = data.find_all('a')
        #link 추출
        link = data_A[-1]["href"][2:-2]
        author = data_A[4].text
        #공백 제거
        data = data.text.split(' ')
        data = ' '.join(data).split()

        data = data[6:]

        if(data[0] == "공식"):
            data = data[1:]

        #['문서', '저장하기', 'Keep에', '저장', 'Keep', '바로가기', '2022.12.28.', '머니머신팩토리', '무민세대', '뜻,', 'N포세대 와는', '무엇이', '다를까?', '경쟁사회에', '지친...', '무민세대', '뜻,', 'N포세대와는', '무엇이', '다를까?', '경쟁사회에', '지친', '세대,', '소확행...', '핀란드의', '스토리텔링', '캐릭터인', "'무민'과도", '단어가', '비슷하여', '그', '의미가', '더', '강조되는', '것', '같다....']
        written_date = data[0]
        # 공백있는 이름이 처리가 안됨
        # --author = data[1]
        
        #'N일 전' 처리
        if(written_date.find("일 전") == 1):
            written_date = (datetime.datetime.now() - datetime.timedelta(days = int(written_date[:-3]))).strftime("%Y.%m.%d")

        #DB 구조
        #Psearch TEXT, Csearch TEXT, Author TEXT, Date TEXT, Link TEXT, Crawled INTEAGER

        #같은 링크를 보유하고있으면 입력하지 않음
        cur.execute("SELECT * FROM SearchLink WHERE Link = '" + link +"'")
        if(len(cur.fetchall()) == 0):    
            db_input = [Pquery, Cquery, author, written_date, link, 0]
            cur.execute("INSERT INTO SearchLink Values(?, ?, ?, ?, ?, ?)", db_input)

        #print(written_date, author, link)

    con.commit()
    con.close()

def get_blog_link(Pquery, Cquery, date_from, date_to):

    #1
    #https://s.search.naver.com/p/blog/search.naver?where=blog&sm=tab_pge&api_type=1&
    #query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&rev=44&start=31&dup_remove=1&post_blogurl=&
    #post_blogurl_without=&nso=so%3Add%2Cp%3Afrom20230219to20110101&nlu_query=&dkey=0&source_query=&nx_search_query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&spq=0

    #2
    #https://s.search.naver.com/p/blog/search.naver?where=blog&sm=tab_pge&api_type=1&
    #query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&rev=44&start=61&dup_remove=1&post_blogurl=&
    #post_blogurl_without=&nso=so%3Add%2Cp%3Afrom20230219to20110101&nlu_query=&dkey=0&source_query=&nx_search_query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&spq=0

    view_link = "https://s.search.naver.com/p/blog/search.naver?"
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

    datas={

        'where':'blog',
        'sm':'tab_pge',
        'api_type':'1',
        'query':'',
        'rev':'44',
        'start':'31',
        'dup_remove':'1',
        'post_blogurl':'',
        'post_blogurl_without':'',
        'nso':'so%3Add%2Cp%3Afrom20230219to20110101',
        'nlu_query':'',
        'dkey':'0',
        'source_query':'',
        'nx_search_query':'',
        'spq':'0'
    }

    #검색어 입력
    #datas['query'] = parse.quote(Cquery)
    #datas['nx_search_query'] = parse.quote(Cquery)
    datas['query'] = Cquery
    datas['nx_search_query'] = Cquery

    #날짜 입력
    #so%3Add%2Cp%3Afrom20230219to20110101
    datas['nso'] = "so%3Add%2Cp%3Afrom" + date_from + "to" + date_to
    
    #start init
    #start 61 -> 91 ->  121
    #prank 61 -> 91 -> 121

    #html 초기화
    html = ''

    #전체 크기를 받아오기 위해 한번 크롤링
    html = get_html(view_link, hdr, datas)
    
    soup = BeautifulSoup(html, 'lxml')

    #전체 크기 추출
    p = re.compile('"[0-9].+?"')
    max_size = int(p.findall(soup.find('body').text)[0][1:-1])


    for x in tqdm(range(int(max_size/30))):
        
        #html 추출
        html = get_html(view_link, hdr, datas)
        
        #파싱
        blog_parser(Pquery, Cquery, html)

        #개수 증가
        datas['start'] = str(int(datas['start']) + 30)

    #html 추출
    html = get_html(view_link, hdr, datas)
    
    #파싱
    blog_parser(Pquery, Cquery, html)



if __name__ == '__main__':


    #input file 읽어오기

        #Psearch 읽어오기
    
        #DB 테이블 생성
        #Psearch    Csearch     Author      Date    Link
        #Csearch 멀티프로세싱으로 크롤링


    
    get_1st_blog('무민세대', '무민세대', '20110101', '20230219')

    get_blog_link('무민세대', '무민세대', '20110101', '20230219')
