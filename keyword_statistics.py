import re
import numpy as np
import pandas as pd
from multiprocessing import Process, Queue
import os
import sys
from tqdm import tqdm
import time

def walk_file(fname_q):

    for (path, dir, file) in tqdm(os.walk('Search')):

        for fname in file:
            fname_q.put([path, fname])

    for i in range(10):
        fname_q.put([])

def run_process(N, fname_q, keyword_list):

    df_col = ['file', 'link', 'Pkeyword', 'keyword', 'Date']
    
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

        for Pkeyword, keyword in keyword_list:
        
            #키워드를 탐색한 경우
            if keyword in text:
                
                date = fname.split("_")[0]

                col = [fname, path, Pkeyword, keyword, date]
                    
                df_result = pd.concat([df_result, pd.DataFrame(data = [col], columns = df_col)])
    
    df_result.to_csv('./Statistics/Temp/' + "temp_" + str(N) + ".csv", encoding='utf-8-sig')
    
    
def merge(keyword_list):

    col_name = ['file', 'link', 'Pkeyword', 'keyword', 'Date']
    
    fname_list = os.listdir("Statistics/Temp")
    first_fname = "Statistics/Temp/" + fname_list.pop()
    df_result = pd.read_csv(first_fname, encoding = "utf-8")
    os.remove(first_fname)

    for fname in fname_list:
        df_result = pd.concat([df_result, pd.read_csv("Statistics/Temp/" + fname, encoding = "utf-8")])
        os.remove("Statistics/Temp/" + fname)
    
    return df_result


def read_file(path, fname):

    f = open("/".join([path, fname]), encoding='utf-8')

    text = f.read()

    f.close()

    return text


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

    merge(map_val).to_csv("Statistics/total.csv", encoding='utf-8-sig')
