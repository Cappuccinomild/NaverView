import re
import numpy as np
import pandas as pd
from multiprocessing import Pool
import os
import sys
from tqdm import tqdm

def run_process(map_val):

    df_col = ['file','link','-10', '-9', '-8', '-7', '-6', '-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    search_num = map_val['argv']
    keyword_list = map_val['keyword']
    file_list = map_val['flist']
    
    #result list 초기화
    df_result = []
    for k in keyword_list:
        df_result.append(pd.DataFrame(columns = df_col))
    
    for path, fname in file_list:

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
        
        i = 0
        for keyword in keyword_list:
            #키워드 추출
            col_insert = extract_sentences(text, keyword)

            #키워드를 탐색한 경우
            if col_insert:

                for col in col_insert:

                    #결과물에 원본링크 입력
                    col.insert(0, link)
                    
                    #결과물에 파일위치 입력
                    col.insert(0, "\\".join([path, fname]))
                    
                    df_result[i] = df_result[i].append(pd.DataFrame(data = [col], columns = df_col))

            i += 1

    return df_result

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

    f = open("keyword.txt", "r", encoding='utf-8')

    keyword_list = f.read().split("\n")


    #리스트 분할
    flist = []
    for (path, dir, file) in os.walk('Search/내시피족'):

        for fname in file:
            flist.append([path, fname])

    for (path, dir, file) in os.walk('Search/덕질메이트'):

        for fname in file:
            flist.append([path, fname])

    flist = divide_list(flist, 10)

    #함수에 넣기 전 전처리
    #{argv : n, keyword : [], flist : []}

    map_val = []
    for file_list in flist:
        map_val.append({'argv' : sys.argv[-1], 'keyword' : keyword_list, 'flist' : file_list})

    with Pool(10) as p:
        result = p.map(run_process, map_val)

    print(result)

    '''
    for keyword in ['덕질Mate', '덕질메이트', '덕질mate', '덕 질 Mate', '덕 질 메이트']:
        print(keyword)
        df_result = pd.DataFrame(columns = df_col)
        for (path, dir, file) in os.walk('Search\덕질메이트'):

            for fname in file:
                print(path, fname)
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
                
                #키워드 추출
                col_insert = extract_sentences(text, keyword)

                #키워드를 탐색한 경우
                if col_insert:

                    for col in col_insert:

                        #결과물에 원본링크 입력
                        col.insert(0, link)
                        
                        #결과물에 파일위치 입력
                        col.insert(0, "\\".join([path, fname]))
                        
                        df_result = df_result.append(pd.DataFrame(data = [col], columns = df_col))


        #n 개의 칼럼만 추출
        col_cnt = int(sys.argv[1])
        return_col = [str(i) for i in range(-col_cnt, col_cnt+1)]
        return_col.insert(0, 'link')
        return_col.insert(0, 'file')

        df_result = df_result[return_col]
        df_result.to_csv(keyword + ".csv", encoding='utf-8-sig')

        '''