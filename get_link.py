import requests
from bs4 import BeautifulSoup
import datetime
import time
import os
from tqdm import tqdm
import math
import multiprocessing
import sys
import re

def get_link():

    view_link = "https://s.search.naver.com/p/review/search.naver"
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

    datas={

        'rev'='',
        'where':'view',
        'api_type':'11',
        'start':'0',
        'query':'',
        'nso':'so%3Ar%2Cp%3Aall%2Ca%3Aall',
        'nqx_theme':'',
        'main_q':'',
        'mode':'normal',
        'q_material':'',
        'ac':'0',
        'aq':'0',
        'spq':'0',
        'st_coll':'',
        'topic_r_cat':'',
        'nx_search_query':'',
        'nx_and_query':'',
        'nx_sub_query':'',
        'prank':'61',
        'sm':'tab_opt',
        'ssc':'tab.view.view',
        'ngn_country':'KR',
        'lgl_rcode':'06230112',
        'fgn_region':'',
        'fgn_city':'',
        'lgl_lat':'35.893749',
        'lgl_long':'128.61855',
        'abt':''

    }

    #start 61 -> 91 -> 121
    #prank 61 -> 91 -> 121

    #경북대 좌표
    #lgl_rcode=06230112&fgn_region=&fgn_city=&lgl_lat=35.893749&lgl_long=128.61855

    #1
    #https://s.search.naver.com/p/review/search.naver?rev=44&where=view&api_type=11&start=61&query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&nso=so%3Ar%2Cp%3Aall%2Ca%3Aall&nqx_theme=&main_q=&mode=normal&q_material=&ac=0&aq=0&spq=0&st_coll=&topic_r_cat=&nx_search_query=&nx_and_query=&nx_sub_query=&prank=61&sm=tab_opt&ssc=tab.view.view&ngn_country=KR&lgl_rcode=06230112&fgn_region=&fgn_city=&lgl_lat=35.893749&lgl_long=128.61855&abt=

    #2
    #https://s.search.naver.com/p/review/search.naver?rev=44&where=view&api_type=11&start=91&query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&nso=so%3Ar%2Cp%3Aall%2Ca%3Aall&nqx_theme=&main_q=&mode=normal&q_material=&ac=0&aq=0&spq=0&st_coll=&topic_r_cat=&nx_search_query=&nx_and_query=&nx_sub_query=&prank=91&sm=tab_opt&ssc=tab.view.view&ngn_country=KR&lgl_rcode=06230112&fgn_region=&fgn_city=&lgl_lat=35.893749&lgl_long=128.61855&abt=

    #3
    #https://s.search.naver.com/p/review/search.naver?rev=44&where=view&api_type=11&start=121&query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&nso=so%3Ar%2Cp%3Aall%2Ca%3Aall&nqx_theme=&main_q=&mode=normal&q_material=&ac=0&aq=0&spq=0&st_coll=&topic_r_cat=&nx_search_query=&nx_and_query=&nx_sub_query=&prank=121&sm=tab_opt&ssc=tab.view.view&ngn_country=KR&lgl_rcode=06230112&fgn_region=&fgn_city=&lgl_lat=35.893749&lgl_long=128.61855&abt=

    for x in tqdm(range((date_s - date_e).days+1)):

        #페이지를 증가시키며 탐색
        link_set = []
        retry_cnt = 0
        while True:

            try:
                resp = requests.get(naver_news, headers = hdr, params=datas, timeout=10)

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
                print('unexpect err')
                #페이지 증가
                datas['page'] = str(int(datas['page']) + 1)
                retry_cnt = 0
                continue

            #html 추출
            if resp.status_code == 200:
                _html = resp.text

            #페이지 파싱
            soup = BeautifulSoup(_html, 'lxml')

            #페이지 번호를 위한 파싱
            page_list = soup.find("div", class_='paging')

            #현재페이지
            page_now = page_list.find('strong').text
            if page_now is None:
                print("null page")
                time.sleep(10)
                continue
            #print(page_now, datas['page'])

            #현재페이지와 탐색페이지가 다르면 종료
            if page_now != datas['page']:
                datas['page'] = '1'
                break

            #현재 페이지에서 기사 링크 목록 추출
            for link in soup.find("div", id="main_content").find_all("li"):

                #메이저 언론사인지 확인
                media = link.find('span', class_="writing").text
                if media in newspaper:

                    #링크모음 저장
                    #저장태그
                    #100273_media_20200101_headline_2_link
                    headline = link.find_all('a')[-1].text.replace("\n", '')
                    #앞쪽 공백 삭제
                    p = re.compile('[^\s|^\t|^\n].+')
                    headline = "".join(p.findall(headline))

                    #뒤쪽 공백 삭제
                    p = re.compile('.+[^\s|^\t|^\n]')
                    headline = "".join(p.findall(headline))
                    link_set.append(datas['sid1']+datas['sid2']+"_"+media+"_"+datas['date']+"_"+headline+"_"+datas['page']+"_"+link.find('a')['href'])


            #페이지 증가
            datas['page'] = str(int(datas['page']) + 1)

        #파일명
        fname = sid1+sid2+"_"+datas['date']+".txt"


        f = open(dir+'/'+fname, "w", encoding = 'utf-8')
        f.write("\n".join(link_set))
        f.write("\n")

        #종료조건
        if datas['date'] == date_e:
            break

        #날짜 감소
        date_desc = date_desc - datetime.timedelta(days=1)

        datas['date'] = date_to_str(date_desc)
