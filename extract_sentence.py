import re
import numpy as np
import pandas as pd
from multiprocessing import Process
import os

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
            while len(temp) < 21:  # 결과가 21개 미만이면 ''를 채워줌
                temp.insert(0, '')
                temp.append('')
            result.append(temp)
    return result

def keyword_search(text):

    sentence_queue = []


if __name__ == "__main__":
    
    for (path, dir, file) in os.walk('Search\내시피족\내시피족'):

        for fname in file:
            print(path, fname)

            #파일을 읽어서 공백 제거
            text = read_file(path, fname)
            text = text.replace('\u200b','')
            text = text.split("\n")
            text = list(filter(bool, text))
            
            #키워드 추출
            print(extract_sentences(text, '내시피족'))