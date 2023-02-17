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

def get_1st_html(query):
    #https://search.naver.com/search.naver?where=view&sm=tab_jum&query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80
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

def get_link(search_keyword, search_len):

    view_link = "https://s.search.naver.com/p/review/search.naver"
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

    datas={

        'rev':'',
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

    datas['query'] = parse.quote(search_keyword)

    #start init
    #start 61 -> 91 ->  121
    #prank 61 -> 91 -> 121
    datas['start'] = '61'
    datas['prank'] = '61'


    #경북대 좌표
    #lgl_rcode=06230112&fgn_region=&fgn_city=&lgl_lat=35.893749&lgl_long=128.61855

    #첫페이지
    #https://search.naver.com/search.naver?where=view&sm=tab_jum&query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80

    #q1
    #https://s.search.naver.com/p/review/search.naver?rev=44&where=view&api_type=11&start=61&query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&nso=so%3Ar%2Cp%3Aall%2Ca%3Aall&nqx_theme=&main_q=&mode=normal&q_material=&ac=0&aq=0&spq=0&st_coll=&topic_r_cat=&nx_search_query=&nx_and_query=&nx_sub_query=&prank=61&sm=tab_opt&ssc=tab.view.view&ngn_country=KR&lgl_rcode=06230112&fgn_region=&fgn_city=&lgl_lat=35.893749&lgl_long=128.61855&abt=

    #q2
    #https://s.search.naver.com/p/review/search.naver?rev=44&where=view&api_type=11&start=91&query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&nso=so%3Ar%2Cp%3Aall%2Ca%3Aall&nqx_theme=&main_q=&mode=normal&q_material=&ac=0&aq=0&spq=0&st_coll=&topic_r_cat=&nx_search_query=&nx_and_query=&nx_sub_query=&prank=91&sm=tab_opt&ssc=tab.view.view&ngn_country=KR&lgl_rcode=06230112&fgn_region=&fgn_city=&lgl_lat=35.893749&lgl_long=128.61855&abt=

    #q3
    #https://s.search.naver.com/p/review/search.naver?rev=44&where=view&api_type=11&start=121&query=%EB%AC%B4%EB%AF%BC%EC%84%B8%EB%8C%80&nso=so%3Ar%2Cp%3Aall%2Ca%3Aall&nqx_theme=&main_q=&mode=normal&q_material=&ac=0&aq=0&spq=0&st_coll=&topic_r_cat=&nx_search_query=&nx_and_query=&nx_sub_query=&prank=121&sm=tab_opt&ssc=tab.view.view&ngn_country=KR&lgl_rcode=06230112&fgn_region=&fgn_city=&lgl_lat=35.893749&lgl_long=128.61855&abt=

    for x in tqdm(range(search_len)):

        #html 받아오기
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


if __name__ == '__main__':



    html = get_1st_html('무민세대')

    #페이지 파싱
    soup = BeautifulSoup(html, 'lxml')

    data_list = soup.find('ul', class_ = 'lst_total _list_base')

    os.makedirs(exist_ok = True)
    for data in data_list.find_all('div', class_ = 'total_area'):
        author = data.find('span', class_ = 'elss etc_dsc_inner').text
        link = data.find('div', class_="total_dsc_wrap").find('a')["href"]

        print(author, link)
    #print(html)
