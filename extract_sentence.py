import re
import numpy as np
import pandas as pd
from multiprocessing import Process, Queue
import os
import sys
from tqdm import tqdm
import time
import datetime

def walk_file(fname_q):

    for (path, dir, file) in tqdm(os.walk('Search')):

        for fname in file:
            fname_q.put([path, fname])

    for i in range(10):
        fname_q.put([])

def run_process(N, fname_q, keyword_list):

    df_col = ['file', 'link', 'keyword', '-10', '-9', '-8', '-7', '-6', '-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    
    #result list 초기화
    df_result = pd.DataFrame(columns = df_col)

    while True:
        
        flag = fname_q.get()

        #파일을 다 읽어서 빈 리스트
        if not flag:
            #print("return", N ,flag)
            break
        
        else:
            path, fname = flag


        #파일을 읽어서 공백 제거
        text = read_file(path, fname)
        
        #빈 텍스트파일일 경우
        if not text:
            continue

        #유니코드 문자제거
        text = text.replace('\u200b','')
        text = text.replace('\ufeff','')
        text = text.replace('\xa0','')
        
        #줄바꿈으로 문장 구분
        text = text.split("\n")
        text = list(filter(bool, text))
        
        link = text[-1]
        text = [t.strip() for t in text]
        text = ".".join(text)

        #마침표로 문장 구분
        text = text.split(".")
        text = list(filter(bool, text))
        
        for Pkeyword, keyword in keyword_list:
            #키워드 추출
            col_insert = extract_sentences(text, keyword)

            #키워드를 탐색한 경우
            if col_insert:

                for col in col_insert:
                    
                    #결과물에 검색 키워드 입력
                    col.insert(0, keyword)

                    #결과물에 원본링크 입력
                    col.insert(0, link)
                    
                    #결과물에 파일위치 입력
                    col.insert(0, "\\".join([path, fname]))
                    
                    df_result = pd.concat([df_result, pd.DataFrame(data = [col], columns = df_col)])
    
    df_result.to_csv('./KeywordResult/Temp/' + "temp_" + str(N) + ".csv", encoding='utf-8-sig', index = False)
    
    
def merge(keyword_list, col_cnt):

    col_name = ['file', 'link', '-10', '-9', '-8', '-7', '-6', '-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    
    #n 개의 칼럼만 추출
    col_cnt = int(sys.argv[1])
    col_name = [str(i) for i in range(-col_cnt, col_cnt+1)]
    col_name.insert(0, 'link')
    col_name.insert(0, 'file')


    fname_list = os.listdir("KeywordResult/Temp")
    first_fname = "KeywordResult/Temp/" + fname_list.pop()
    df_result = pd.read_csv(first_fname, encoding = "utf-8")
    os.remove(first_fname)

    for fname in fname_list:
        df_result = pd.concat([df_result, pd.read_csv("KeywordResult/Temp/" + fname, encoding = "utf-8")])
        os.remove("KeywordResult/Temp/" + fname)
    

    for Pkeyword, keyword in keyword_list:
        dirname = "./KeywordResult/" + Pkeyword + "/"
        os.makedirs(dirname, exist_ok=True)
        temp = df_result[df_result['keyword'] == keyword]
        temp[col_name].to_csv(dirname + keyword + str(time.time()).split(".")[-1][-4:]+ ".csv", encoding='utf-8-sig', index = False)


def read_file(path, fname):

    f = open("/".join([path, fname]), encoding='utf-8')

    text = f.read()

    f.close()

    return text

def extract_sentences(lst, keyword):
    result = []
    for i in range(len(lst)):
        if keyword in lst[i]:
            start = max(0, i-10)
            end = min(len(lst), i+11)
            temp = lst[start:end]
            if len(temp) < 21:  # 결과가 21개 미만이면 ''를 채워줌
                j = 0
                while j < 10 - i:
                    temp.insert(0, '')
                    j += 1
                
                j = end
                while j < i + 11:
                    temp.append('')
                    j += 1

            result.append(temp)
    return result

def divide_list(lst, n):
    """리스트를 n개의 묶음으로 나누는 함수"""
    quotient = len(lst) // n
    remainder = len(lst) % n
    result = []
    idx = 0
    for i in range(n):
        if i < remainder:
            length = quotient + 1
        else:
            length = quotient
        result.append(lst[idx:idx+length])
        idx += length
    return result

if __name__ == "__main__":

    f = open("input.txt", "r", encoding='utf-8')

    map_val = []
    query_list = []
    for query in f.read().split("\n"):
        
        #query_list가 비었을때 Pquery 설정
        if not query_list:
            Pquery = query
        
        #한 쿼리 묶음을 종료
        if query == "":
            query_list = []
            continue

        map_val.append([Pquery, query])
        query_list.append(query)

    start = time.time()

    fname_q = Queue()

    process_list = []
    p = Process(target=walk_file, args=(fname_q,))
    p.start()
    process_list.append(p)

    for N in range(0, 10):
        process = Process(target=run_process, args=(N, fname_q, map_val,))
        process.start()
        process_list.append(process)

    print("join_start")
    for process in process_list:
        process.join()
        #print(process)

    col_cnt = int(sys.argv[1])
    merge(map_val, col_cnt)
