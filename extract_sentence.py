import re
import numpy as np
import pandas as pd
from multiprocessing import Process
import os
import sys
from tqdm import tqdm

def preprocess_sentence_kr(w):
  w = w.strip()
  w = re.sub(r"[^0-9가-힣?.!,¿]+", " ", w) # \n도 공백으로 대체해줌
  w = w.strip()
  return w

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

def keyword_search(text):

    sentence_queue = []


if __name__ == "__main__":
    
    df_col = ['file','link','-10', '-9', '-8', '-7', '-6', '-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    df_result = pd.DataFrame(columns = df_col)

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