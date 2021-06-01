import pandas as pd
import bs4
from urllib.request import urlopen
import urllib
import time
import tkinter as tk
from tkinter import messagebox
import datetime
import time
import re
import numpy as np
def kortime2engtime(time_string):
    today = datetime.datetime.today()
    number = int(re.findall('\d+', time_string)[0])
    kortime = ''.join(re.findall("[^0-9]",time_string))
    if kortime == '일' :
        before_date = datetime.timedelta(days=number)
    elif kortime == '분':
        before_date= datetime.timedelta(minutes=number)
    elif kortime == '시간' :
        before_date = datetime.timedelta(hours=number)
    elif kortime == '초' : 
        before_date = datetime.timedelta(seconds=number)
    else:
        return time_string
    save_date = (today-before_date).strftime('%Y.%m.%d')
    return save_date
def naver(keyword,op='None'):
    searching = '''{}'''.format(keyword)
    searching = searching.strip()
    if op == 'AND': # AND 조건으로 검색
        tmp = list(map(lambda x: ''.join(filter(str.isalnum, x)),searching.split(','))) 
        op_searching = ' +'.join(tmp)
        word_encode = urllib.parse.quote(op_searching)
    else:
        word_encode = urllib.parse.quote(searching)
    df_list = []
    start=1
    key_list= [searching]
    if ',' in searching:
        key_list = list(map(lambda x: ''.join(filter(str.isalnum, x)),searching.split(',')))
    while True:
        url='https://search.naver.com/search.naver?where=news&sm=tab_jum&query={}&pd=1&start={}'.format(word_encode,start)
        source = urlopen(url).read()
        source = bs4.BeautifulSoup(source,'html.parser')
        title_path =  source.find_all('a',{'class':'news_tit'})
        abstract_path = source.find_all('a',{'class':'api_txt_lines dsc_txt_wrap'})
        date_path = source.find_all('span',{'class':'info'})
        if len(title_path) == 0:
            root = tk.Tk()
            msg = messagebox.showerror(title = "Naver No news",message = 'please search other keyword')
            if msg == 'ok':
                root.destroy()
                break

        for i in range(len(title_path)): # or 조건
            title = title_path[i].get('title')
            if op == 'OR' or op == 'None':
                if any(i in title for i in key_list):
                    abstract = abstract_path[i].text
                    link = title_path[i].get('href')
                    date_txt = date_path[i].text
                    date = kortime2engtime(date_txt.split()[0])
                    df = pd.DataFrame({'title':[title],'abstract':[abstract],'url':[link],'date':[date],'engine':['naver']})
                    df_list.append(df)
            if op == 'AND':
                if all(i in title for i in key_list):
                    abstract = abstract_path[i].text
                    link = title_path[i].get('href')
                    date_txt = date_path[i].text
                    date = kortime2engtime(date_txt.split()[0])
                    df = pd.DataFrame({'title':[title],'abstract':[abstract],'url':[link],'date':[date],'engine':['naver']})
                    df_list.append(df)        

        current_page = source.find_all('a',{'aria-pressed':'true'})[0].text
        last_page = source.find_all('a',{'aria-pressed':'false'})[-1].text
        if last_page == '문서 저장하기':
            break
        if int(current_page)>=int(last_page):
            break
        else:
            start += 10
        time.sleep(0.5)
        print('crawling...')
    if df_list: 
        naver_df = pd.concat(df_list)
        if op == 'AND' or op == 'OR':
            op_searching = searching.replace(',',f' {op} ')
            naver_df.to_excel('''naver_{}_result.xlsx'''.format(op_searching),index=False)
            
        else:
            naver_df.to_excel('''naver_{}_result.xlsx'''.format(searching),index=False)
        root2 = tk.Tk()
        msg = messagebox.showinfo(title='Save msg',message='Naver Save!')
        if msg == 'ok':
            root2.destroy()
        return naver_df
    else:
        root3 = tk.Tk()
        msg = messagebox.showerror(title = "Naver No news",message = 'please search other keyword')
        if msg == 'ok':
            root3.destroy()


def google(keyword,op='None'):
    searching = '''{}'''.format(keyword)
    searching = searching.strip()
    period = ' when:7d'
    if op != 'None':
        op_searching = searching.replace(',',f' {op} ')
        word_encode = urllib.parse.quote(op_searching+period)
    else:
        word_encode = urllib.parse.quote(searching+period)
    base_url = 'https://news.google.com/'
    url = 'https://news.google.com/search?q={}&hl=ko&gl=KR&ceid=KR:ko'.format(word_encode)
    source = urlopen(url).read()
    source = bs4.BeautifulSoup(source,'html.parser')
    df_list = []
    article_list = source.find_all('a',{'class':'DY5T1d RZIKme'})
    date_path = source.find_all('time',{'class':'WW6dff uQIVzc Sksgp'})
    if len(article_list) == 0:
        root = tk.Tk()
        msg = messagebox.showerror(title = "Google No news",message = 'please search other keyword')
        if msg == 'ok':
            root.destroy()
    else:
        key_list= [searching]
        if ',' in searching:
            key_list = list(map(lambda x: ''.join(filter(str.isalnum, x)),searching.split(',')))
        for i in range(len(article_list)):
            title = article_list[i].text
            date = date_path[i].get('datetime').split('T')[0].replace('-','.')
            
            if op == 'OR' or op == 'None':
                if any(i in title for i in key_list):
                    link = base_url + article_list[i].get('href')[1:]
                    df = pd.DataFrame({'title':[title],'abstract':[np.nan],'url':[link],'date':[date],'engine':['Google']})
                    df_list.append(df)
            if op == 'AND':
                if all(i in title for i in key_list):
                    link = base_url + article_list[i].get('href')[1:]
                    df = pd.DataFrame({'title':[title],'abstract':[np.nan],'url':[link],'date':[date],'engine':['Google']})
                    df_list.append(df)
        
        if df_list:
            google_df = pd.concat(df_list)
            if op != 'None':
                google_df.to_excel('''google_{}_result.xlsx'''.format(op_searching),index=False)
            else:
                google_df.to_excel('''google_{}_result.xlsx'''.format(searching),index=False)
            root2 = tk.Tk()
            msg = messagebox.showinfo(title='Save msg',message='Google Save!')
            if msg == 'ok':
                root2.destroy()
            return google_df
        else:
            root3 = tk.Tk()
            msg = messagebox.showerror(title = "Google No news",message = 'please search other keyword')
            if msg == 'ok':
                root3.destroy()
