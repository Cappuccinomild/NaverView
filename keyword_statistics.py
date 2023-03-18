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

    df_col = ['file', 'path', 'Pkeyword', 'keyword', 'Date']
    
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
                
                date = fname.split("_")[0][:-2]

                col = [fname, path, Pkeyword, keyword, date]
                    
                df_result = pd.concat([df_result, pd.DataFrame(data = [col], columns = df_col)])
    
    df_result.to_csv('./Statistics/Temp/' + "temp_" + str(N) + ".csv", encoding='utf-8-sig', index = False)
    
    
def merge(keyword_list):

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

def transpose(matrix):
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]

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

    #merge(map_val).to_csv("Statistics/total.csv", encoding='utf-8-sig', index = False)
    
    df_total = merge(map_val)
    df_date = list(df_total['Date'].unique())
    df_date.sort()
    
    print(df_date)

    #Dataframe col
    df_col = ['Pkeyword', 'keyword', 'Total']
    df_col = df_col + df_date

    df_result = pd.DataFrame(columns = df_col)

    prev_Pkeyword, prev_Ckeyword = map_val[0]
    pkey_list = [0 for i in range(len(df_date))]
    pkey_list.insert(0, 0)
    pkey_list.insert(0, '')

    
    for Pkeyword, Ckeyword in map_val:
        #[x+y for x,y in zip(list1, list2)]
        #P키워드별로 Dataframe 추출
        #df_temp = df_total[(df_total['Pkeyword'] == Pkeyword)]
        
        #추출시 Pkeyword 로 Ckeyword를 모음
        if Pkeyword == prev_Pkeyword:

            #이형태별 통계
            df_temp = df_total[(df_total['Pkeyword'] == Pkeyword) & (df_total['keyword'] == Ckeyword)]

            keyword_col = []
            for date in df_date:    
                cnt_list = df_temp['Date'].loc[df_temp['Date'] == date].count()
                keyword_col.append(cnt_list)
            
            ckey_sum = sum(keyword_col)
            df_list = [Ckeyword + "(" + str(ckey_sum) + ") ", ckey_sum] + keyword_col
            pkey_list = [x+y for x,y in zip(pkey_list, df_list)]
        
        else:
            
            pkey_list.insert(0, prev_Pkeyword)
            df_result = pd.concat([df_result, pd.DataFrame(data = [pkey_list], columns = df_col)])
            
            pkey_list = [0 for i in range(len(df_date))]
            pkey_list.insert(0, 0)
            pkey_list.insert(0, '')

            #이형태별 통계
            df_temp = df_total[(df_total['Pkeyword'] == Pkeyword) & (df_total['keyword'] == Ckeyword)]

            keyword_col = []
            for date in df_date:    
                cnt_list = df_temp['Date'].loc[df_temp['Date'] == date].count()
                keyword_col.append(cnt_list)
            
            #ckey 합계를 더해서 pkey_list에 저장
            ckey_sum = sum(keyword_col)
            df_list = [Ckeyword + "(" + str(ckey_sum) + ") ", ckey_sum] + keyword_col
            pkey_list = [x+y for x,y in zip(pkey_list, df_list)]
           
        prev_Pkeyword = Pkeyword
        prev_Ckeyword = Ckeyword


    pkey_list.insert(0, prev_Pkeyword)
    df_result = pd.concat([df_result, pd.DataFrame(data = [pkey_list], columns = df_col)])
    
    #1차 output
    df_result.to_csv("Statistics/month.csv", encoding='utf-8-sig', index = False)

    #연도별로 모으기    
    years = []
    for col in df_date:
        try:
            year = str(int(col/100))
            if year not in years:
                years.append(year)
        except:
            continue
    
    years.sort()
    
    yearly_sum = []

    for year in years:
        columns = [col for col in df_result.columns if str(col).startswith(year)]
 
        yearly_sum.append([sum(year_list) for year_list in df_result[columns].values.tolist()])

    yearly_col = ['Pkeyword', 'keyword', 'Total'] + years
    
    df_yearly = pd.DataFrame(columns = yearly_col)
    
    pkey_list = df_result[['Pkeyword', 'keyword', 'Total']].values.tolist()
    df_yearly_col = transpose(yearly_sum)

    for i in range(len(pkey_list)):
        pkey_list[i] = pkey_list[i] + df_yearly_col[i]

    df_yearly = pd.DataFrame(data = pkey_list, columns = yearly_col)
            
    df_yearly.to_csv("Statistics/year.csv", encoding='utf-8-sig', index = False)
 